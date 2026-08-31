from __future__ import annotations

import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any

ARTIFACT_TYPES = {"problem", "representation", "evidence", "message", "literature", "computation", "invocation"}
NODE_STATUSES = {"active", "dormant", "rejected"}


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def digest_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


class Store:
    def __init__(self, root: Path):
        self.root = root

    def init(self, name: str) -> None:
        for p in ("artifacts", "nodes", "proposals", "contexts", "dispatches", "outputs", "history"):
            (self.root / p).mkdir(parents=True, exist_ok=True)
        self.write_json(self.root / "program.json", {
            "id": "PROGRAM-001", "type": "research_program", "name": name,
            "created_at": now(), "provenance": {"implementation": "math-automation-portable"},
            "constitution": [
                "No canonical mathematical outlook exists.",
                "Messages do not mutate recipient nodes.",
                "Evidence and interpretation remain distinguishable.",
                "Agreement is not independent confirmation.",
                "Exploration may report no natural alternative.",
            ],
        })
        self.event("program_initialized", program="PROGRAM-001")

    def write_json(self, path: Path, data: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")

    def read_json(self, path: Path) -> dict[str, Any]:
        return json.loads(path.read_text())

    def event(self, event: str, **data: Any) -> None:
        record = {"event": event, "time": now(), **data}
        with (self.root / "history" / "events.jsonl").open("a") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")

    def artifact_path(self, artifact_type: str, artifact_id: str) -> Path:
        return self.root / "artifacts" / artifact_type / f"{artifact_id}.json"

    def create_artifact(self, artifact_type: str, artifact_id: str, payload: dict[str, Any],
                        refs: list[str] | None = None, status: str = "active") -> dict[str, Any]:
        if artifact_type not in ARTIFACT_TYPES:
            raise ValueError(f"unsupported artifact type: {artifact_type}")
        path = self.artifact_path(artifact_type, artifact_id)
        if path.exists():
            raise ValueError(f"artifact already exists: {artifact_id}")
        item = {"id": artifact_id, "type": artifact_type, "created_at": now(), "status": status,
                "provenance": {"created_by": "portable-cli"}, "references": refs or [], "payload": payload}
        self.write_json(path, item)
        self.event("artifact_created", artifact_id=artifact_id, artifact_type=artifact_type)
        return item

    def find(self, artifact_id: str) -> dict[str, Any]:
        for directory in (self.root / "artifacts").glob("*"):
            candidate = directory / f"{artifact_id}.json"
            if candidate.exists():
                return self.read_json(candidate)
        candidate = self.root / "nodes" / f"{artifact_id}.json"
        if candidate.exists():
            return self.read_json(candidate)
        candidate = self.root / "proposals" / f"{artifact_id}.json"
        if candidate.exists():
            return self.read_json(candidate)
        raise KeyError(artifact_id)

    def create_node(self, node_id: str, problem_id: str) -> dict[str, Any]:
        self.require("problem", problem_id)
        path = self.root / "nodes" / f"{node_id}.json"
        if path.exists():
            raise ValueError(f"node already exists: {node_id}")
        node = {"id": node_id, "type": "node_state", "created_at": now(), "status": "active",
                "problem": problem_id, "representations": [], "evidence": [], "messages": [],
                "hypotheses": [], "questions": [], "interpretation": "", "history": []}
        self.write_json(path, node); self.event("node_created", node_id=node_id, problem=problem_id)
        return node

    def node(self, node_id: str) -> dict[str, Any]:
        return self.read_json(self.root / "nodes" / f"{node_id}.json")

    def require(self, artifact_type: str, artifact_id: str) -> None:
        item = self.find(artifact_id)
        if item["type"] != artifact_type:
            raise ValueError(f"{artifact_id} is not {artifact_type}")

    def message(self, message_id: str, sender: str, recipient: str, refs: list[str], comment: str = "",
                request: str = "reconsider") -> dict[str, Any]:
        self.node(recipient)
        for ref in refs: self.find(ref)
        return self.create_artifact("message", message_id,
            {"sender": sender, "recipient": recipient, "artifact_references": refs,
             "interpretation_comment": comment, "requested_action": request}, refs)

    def proposal(self, proposal_id: str, node_id: str, changes: dict[str, Any], invocation_id: str | None = None) -> dict[str, Any]:
        self.node(node_id)
        item = {"id": proposal_id, "type": "update_proposal", "created_at": now(), "status": "pending",
                "node": node_id, "changes": changes, "invocation": invocation_id, "provenance": {"created_by": "portable-cli"}}
        self.write_json(self.root / "proposals" / f"{proposal_id}.json", item)
        self.event("proposal_created", proposal_id=proposal_id, node_id=node_id)
        return item

    def decide(self, proposal_id: str, decision: str) -> dict[str, Any]:
        if decision not in {"accepted", "rejected"}: raise ValueError("decision must be accepted or rejected")
        path = self.root / "proposals" / f"{proposal_id}.json"; proposal = self.read_json(path)
        if proposal["status"] != "pending": raise ValueError("proposal is not pending")
        proposal["status"] = decision; proposal["decided_at"] = now()
        if decision == "accepted":
            node_path = self.root / "nodes" / f"{proposal['node']}.json"; node = self.read_json(node_path)
            for key, value in proposal["changes"].items():
                if key in {"representations", "evidence", "messages", "hypotheses", "questions"}:
                    node[key] = list(value)
                elif key == "interpretation": node[key] = str(value)
            node["history"].append({"proposal": proposal_id, "accepted_at": now()}); self.write_json(node_path, node)
        self.write_json(path, proposal); self.event("proposal_decided", proposal_id=proposal_id, decision=decision)
        return proposal

    def context(self, context_id: str, node_id: str, selected: list[str], operation: str) -> dict[str, Any]:
        node = self.node(node_id); items = [self.find(x) for x in selected]
        material = {"problem": self.find(node["problem"]), "node": node, "selected_artifacts": items, "operation": operation}
        text = json.dumps(material, indent=2, sort_keys=True)
        manifest = {"id": context_id, "type": "context_manifest", "created_at": now(), "node": node_id,
                    "operation": operation, "artifact_references": selected, "material_sha256": digest_text(text),
                    "no_canonical_outlook": True}
        self.write_json(self.root / "contexts" / f"{context_id}.json", manifest)
        self.write_json(self.root / "contexts" / f"{context_id}.material.json", material)
        self.event("context_materialized", context_id=context_id, node_id=node_id, operation=operation)
        return manifest

    def treatment(self, dispatch_id: str, context_id: str, operation: str, excluded: list[str] | None = None) -> dict[str, Any]:
        context = self.read_json(self.root / "contexts" / f"{context_id}.material.json")
        problem = context["problem"]["payload"]["statement"]
        if operation == "ordinary":
            instruction = "Conduct an ordinary mathematical investigation using only the declared material. It may confirm, refine, or question local state; it need not seek novelty."
        elif operation == "exploration":
            instruction = "Investigate without organizing the work around the supplied existing representation(s). Seek a substantively different organization if one is natural. It is acceptable to conclude that no natural alternative was found."
        else: raise ValueError("operation must be ordinary or exploration")
        body = {"id": dispatch_id, "type": "dispatch", "created_at": now(), "operation": operation,
                "context": context_id, "problem": problem, "excluded_representations": excluded or [], "instruction": instruction}
        text = json.dumps(body, indent=2, sort_keys=True); body["material_sha256"] = digest_text(text)
        self.write_json(self.root / "dispatches" / f"{dispatch_id}.json", body); self.event("dispatch_materialized", dispatch_id=dispatch_id, operation=operation)
        return body

    def invocation(self, invocation_id: str, dispatch_id: str, output: str, provider: str = "manual") -> dict[str, Any]:
        dispatch = self.read_json(self.root / "dispatches" / f"{dispatch_id}.json")
        item = {"id": invocation_id, "type": "invocation", "created_at": now(), "status": "recorded",
                "provider": provider, "dispatch": dispatch_id, "dispatch_sha256": dispatch["material_sha256"],
                "output_sha256": digest_text(output), "provenance": {"material_treatment_fidelity": "manual/provider boundary"}}
        self.write_json(self.artifact_path("invocation", invocation_id), item)
        (self.root / "outputs").mkdir(exist_ok=True); (self.root / "outputs" / f"{invocation_id}.md").write_text(output)
        self.event("invocation_recorded", invocation_id=invocation_id, dispatch=dispatch_id)
        return item

    def validate(self) -> list[str]:
        errors = []
        if not (self.root / "program.json").exists(): return ["missing program.json"]
        ids = set()
        for path in (self.root / "artifacts").glob("*/*.json"):
            item = self.read_json(path); ids.add(item["id"])
            for ref in item.get("references", []):
                try: self.find(ref)
                except KeyError: errors.append(f"{item['id']}: missing reference {ref}")
        for path in (self.root / "nodes").glob("*.json"):
            node = self.read_json(path)
            try: self.require("problem", node["problem"])
            except (KeyError, ValueError): errors.append(f"{node['id']}: missing problem")
            for ref in node["representations"] + node["evidence"] + node["messages"]:
                try: self.find(ref)
                except KeyError: errors.append(f"{node['id']}: missing local reference {ref}")
        for path in (self.root / "proposals").glob("*.json"):
            proposal = self.read_json(path)
            if proposal["status"] not in {"pending", "accepted", "rejected"}: errors.append(f"{proposal['id']}: invalid lifecycle")
            try: self.node(proposal["node"])
            except FileNotFoundError: errors.append(f"{proposal['id']}: missing node")
        return errors
