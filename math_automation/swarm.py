"""Provider-neutral, filesystem-safe run planning and result recording."""
from __future__ import annotations

import json, os, threading
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any
from .store import Store, digest_text, now

STATUSES = {"PENDING", "RUNNING", "SUCCEEDED", "FAILED", "RETRYABLE", "SKIPPED"}


class Swarm:
    def __init__(self, store: Store):
        self.store = store; self.lock = threading.Lock()

    @property
    def runs(self) -> Path: return self.store.root / "runs"

    def write(self, path: Path, item: Any) -> None: self.store.write_json(path, item)
    def spec_path(self, run_id: str) -> Path: return self.runs / run_id / "run_spec.json"
    def jobs_dir(self, run_id: str) -> Path: return self.runs / run_id / "jobs"

    @contextmanager
    def job_lock(self, run_id: str, job_id: str):
        """Serialize updates to one job across local threads/processes on POSIX."""
        lock_path = self.runs / run_id / ".locks" / f"{job_id}.lock"
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        with lock_path.open("a") as handle:
            try:
                import fcntl
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            except ImportError:  # Atomic replaces still protect individual files elsewhere.
                fcntl = None
            try:
                yield
            finally:
                if fcntl is not None:
                    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)

    def create_spec(self, spec: dict[str, Any]) -> dict[str, Any]:
        required = {"id", "problem", "nodes", "provider", "model", "concurrency", "retry_limit", "jobs"}
        missing = required - set(spec)
        if missing: raise ValueError(f"run spec missing: {sorted(missing)}")
        self.store.require("problem", spec["problem"])
        for node in spec["nodes"]: self.store.node(node)
        for template in spec["jobs"]:
            if template.get("operation") == "exploration":
                excluded = template.get("excluded_representations", [])
                if not excluded: raise ValueError("exploration jobs require explicit representation exclusions")
                for representation in excluded: self.store.require("representation", representation)
        if spec["concurrency"] < 1 or spec["retry_limit"] < 0: raise ValueError("invalid execution limits")
        if "output_location" in spec and Path(spec["output_location"]).is_absolute():
            raise ValueError("output_location must be relative to the state root")
        path = self.spec_path(spec["id"])
        if path.exists(): raise ValueError("run already exists")
        intended_invocations = sum(int(template.get("count", 1)) for template in spec["jobs"])
        record = {**spec, "type": "run_spec", "created_at": now(), "status": "PREPARED",
                  "intended_invocations": intended_invocations,
                  "output_location": spec.get("output_location", f"runs/{spec['id']}/outputs"),
                  "provenance": {"implementation": "portable swarm layer"}, "canonical_outlook": None}
        self.write(path, record); self.store.event("run_spec_created", run_id=spec["id"])
        return record

    def plan(self, run_id: str) -> list[dict[str, Any]]:
        spec = self.store.read_json(self.spec_path(run_id)); jobs = []
        for template in spec["jobs"]:
            operation = template["operation"]
            if operation not in {"ordinary", "exploration"}: raise ValueError("unknown operation")
            node = template["node"]
            if node not in spec["nodes"]: raise ValueError("job node not in run")
            count = int(template.get("count", 1))
            if count < 1: raise ValueError("job count must be positive")
            selected = template.get("selected_artifacts", [])
            excluded = template.get("excluded_representations", [])
            if operation == "exploration":
                for representation in excluded: self.store.require("representation", representation)
            for index in range(1, count + 1):
                job_id = f"{run_id}-{template['id']}-{index:04d}"
                job_path = self.jobs_dir(run_id) / f"{job_id}.json"
                if job_path.exists():
                    jobs.append(self.store.read_json(job_path)); continue
                context_id, dispatch_id = f"CTX-{job_id}", f"DISP-{job_id}"
                context = self.store.context(context_id, node, selected, operation)
                dispatch = self.store.treatment(dispatch_id, context_id, operation, excluded)
                job = {"id": job_id, "type": "invocation_job", "run": run_id, "node": node,
                       "operation": operation, "status": "PENDING", "attempts": [],
                       "context": context_id, "context_sha256": context["material_sha256"],
                       "dispatch": dispatch_id, "dispatch_sha256": dispatch["material_sha256"],
                       "ordered_artifact_references": selected, "excluded_representations": excluded,
                       "provider": spec["provider"], "model": spec["model"],
                       "treatment_metadata": template.get("treatment_metadata", {}),
                       "independence": template.get("independence", "independent"), "created_at": now()}
                self.write(job_path, job); jobs.append(job); self.store.event("job_planned", run_id=run_id, job_id=job_id)
        if spec["status"] == "PREPARED":
            spec["status"] = "MATERIALIZED"; spec["materialized_at"] = now()
            self.write(self.spec_path(run_id), spec); self.store.event("run_materialized", run_id=run_id, jobs=len(jobs))
        return jobs

    def dry_run(self, run_id: str) -> dict[str, Any]:
        jobs = self.plan(run_id); errors = self.validate_run(run_id)
        spec = self.store.read_json(self.spec_path(run_id))
        return {"run": run_id, "provider_calls": 0, "jobs": len(jobs), "provider": spec["provider"],
                "model": spec["model"], "concurrency": spec["concurrency"], "errors": errors,
                "operations": {op: sum(j["operation"] == op for j in jobs) for op in ("ordinary", "exploration")}}

    def mark_running(self, run_id: str, job_id: str) -> dict[str, Any]:
        """Persist an observable in-flight attempt before calling a provider."""
        with self.lock:
            with self.job_lock(run_id, job_id):
                path = self.jobs_dir(run_id) / f"{job_id}.json"; job = self.store.read_json(path)
                if job["status"] not in {"PENDING", "RETRYABLE"}: raise ValueError("job is not eligible to run")
                job["status"] = "RUNNING"
                job["active_attempt"] = {"attempt": len(job["attempts"]) + 1, "started_at": now()}
                job["updated_at"] = now(); self.write(path, job)
                self.store.event("job_started", run_id=run_id, job_id=job_id, attempt=job["active_attempt"]["attempt"])
                return job

    def record_result(self, run_id: str, job_id: str, output: str | None, *, failure: str | None = None,
                      transmitted_dispatch: str | None = None, provider_metadata: dict[str, Any] | None = None,
                      resulting_artifacts: list[str] | None = None, resulting_proposals: list[str] | None = None) -> dict[str, Any]:
        with self.lock:
            with self.job_lock(run_id, job_id):
                path = self.jobs_dir(run_id) / f"{job_id}.json"; job = self.store.read_json(path)
                if job["status"] == "SUCCEEDED": raise ValueError("successful job may not be overwritten")
                spec = self.store.read_json(self.spec_path(run_id))
                active = job.pop("active_attempt", None)
                attempt = active["attempt"] if active else len(job["attempts"]) + 1
                if attempt > spec["retry_limit"] + 1: raise ValueError("retry limit exhausted")
                dispatch = self.store.read_json(self.store.root / "dispatches" / f"{job['dispatch']}.json")
                transmitted_hash = digest_text(transmitted_dispatch) if transmitted_dispatch is not None else None
                fidelity = "observable" if transmitted_hash else "intended_only"
                record = {"id": f"INV-{run_id}-{job_id}-A{attempt}", "run": run_id, "job": job_id, "node": job["node"],
                          "operation": job["operation"], "attempt": attempt,
                          "started_at": active["started_at"] if active else now(), "ended_at": now(), "provider": job["provider"],
                          "model": job["model"], "provider_metadata": provider_metadata or {},
                          "material_treatment": {"source_context": job["context"], "ordered_artifacts": job["ordered_artifact_references"],
                            "dispatch": job["dispatch"], "dispatch_sha256": dispatch["material_sha256"],
                            "transmitted_dispatch_sha256": transmitted_hash, "fidelity": fidelity},
                          "status": "FAILED" if failure else "SUCCEEDED", "failure": failure,
                          "resulting_artifact_references": resulting_artifacts or [],
                          "resulting_proposal_references": resulting_proposals or []}
                if output is not None:
                    outpath = self.store.root / spec["output_location"] / f"{job_id}.attempt-{attempt}.md"; outpath.parent.mkdir(parents=True, exist_ok=True)
                    temp = outpath.with_suffix(".tmp")
                    with temp.open("w") as handle:
                        handle.write(output); handle.flush(); os.fsync(handle.fileno())
                    os.replace(temp, outpath)
                    record["raw_response_path"] = str(outpath.relative_to(self.store.root)); record["raw_response_sha256"] = digest_text(output)
                job["attempts"].append(record)
                job["status"] = "RETRYABLE" if failure and attempt <= spec["retry_limit"] else ("FAILED" if failure else "SUCCEEDED")
                job["updated_at"] = now()
                self.write(path, job); self.store.event("job_result_recorded", run_id=run_id, job_id=job_id, attempt=attempt, status=job["status"])
                return job

    def resume(self, run_id: str, executor=None) -> list[str]:
        """Execute only pending/retryable jobs through a supplied provider callback.

        No built-in provider exists; callers must pass `executor(job, dispatch) -> str`.
        """
        spec = self.store.read_json(self.spec_path(run_id)); todo = []
        for path in self.jobs_dir(run_id).glob("*.json"):
            job = self.store.read_json(path)
            if job["status"] == "RUNNING":
                # A prior process died after persisting start state but before a result.
                # Preserve that attempt before making a retry eligible.
                self.record_result(run_id, job["id"], None, failure="interrupted before result recording")
                job = self.store.read_json(path)
            if job["status"] in {"PENDING", "RETRYABLE"} and len(job["attempts"]) <= spec["retry_limit"]: todo.append(job)
        if executor is None: return [j["id"] for j in todo]
        spec["status"] = "RUNNING"; spec.setdefault("started_at", now()); self.write(self.spec_path(run_id), spec)
        def work(job):
            try:
                dispatch_text = (self.store.root / "dispatches" / f"{job['dispatch']}.json").read_text()
                self.mark_running(run_id, job["id"])
                self.record_result(run_id, job["id"], executor(job, dispatch_text), transmitted_dispatch=dispatch_text)
            except Exception as exc: self.record_result(run_id, job["id"], None, failure=f"{type(exc).__name__}: {exc}")
        with ThreadPoolExecutor(max_workers=spec["concurrency"]) as pool: list(pool.map(work, todo))
        remaining = self.resume(run_id)
        spec = self.store.read_json(self.spec_path(run_id))
        spec["status"] = "PARTIAL" if remaining else "COMPLETED"; spec["ended_at"] = now()
        self.write(self.spec_path(run_id), spec)
        return [j["id"] for j in todo]

    def validate_run(self, run_id: str) -> list[str]:
        errors = self.store.validate(); spec = self.store.read_json(self.spec_path(run_id))
        for path in self.jobs_dir(run_id).glob("*.json"):
            job = self.store.read_json(path)
            if job["status"] not in STATUSES: errors.append(f"{job['id']}: invalid status")
            if not (self.store.root / "contexts" / f"{job['context']}.json").exists(): errors.append(f"{job['id']}: missing context")
            if not (self.store.root / "dispatches" / f"{job['dispatch']}.json").exists(): errors.append(f"{job['id']}: missing dispatch")
            if job["operation"] == "exploration" and not job["excluded_representations"]: errors.append(f"{job['id']}: exploration lacks exclusions")
        return errors

    def inspect(self, run_id: str) -> dict[str, Any]:
        jobs = [self.store.read_json(p) for p in self.jobs_dir(run_id).glob("*.json")]
        return {"run": run_id, "run_status": self.store.read_json(self.spec_path(run_id))["status"], "jobs": len(jobs), "statuses": {s: sum(j["status"] == s for j in jobs) for s in sorted(STATUSES)},
                "independent": sum(j["independence"] == "independent" for j in jobs)}
