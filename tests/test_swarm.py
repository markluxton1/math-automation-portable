import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from math_automation.store import Store
from math_automation.swarm import Swarm


class SwarmTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.s = Store(Path(self.temp.name)); self.s.init("swarm")
        self.s.create_artifact("problem", "P", {"statement": "neutral problem"})
        self.s.create_artifact("representation", "R", {"problem": "P", "description": "existing framing"})
        self.s.create_node("A", "P"); self.s.create_node("B", "P"); self.w = Swarm(self.s)
        self.spec = {"id": "RUN-1", "problem": "P", "nodes": ["A", "B"], "provider": "manual", "model": "Sol Ultra", "concurrency": 4, "retry_limit": 1,
          "jobs": [{"id": "ordinary", "node": "A", "operation": "ordinary", "count": 4, "selected_artifacts": []},
                   {"id": "explore", "node": "B", "operation": "exploration", "count": 3, "selected_artifacts": [], "excluded_representations": ["R"]}]}
        self.w.create_spec(self.spec)

    def tearDown(self): self.temp.cleanup()

    def test_dry_run_is_deterministic_isolated_and_uncontaminated(self):
        first = self.w.dry_run("RUN-1"); second = self.w.dry_run("RUN-1")
        self.assertEqual(first["jobs"], 7); self.assertEqual(first["jobs"], second["jobs"]); self.assertEqual(first["errors"], [])
        jobs = list((self.s.root / "runs" / "RUN-1" / "jobs").glob("*.json"))
        self.assertEqual(len(jobs), 7)
        for path in jobs:
            job = self.s.read_json(path); context = self.s.read_json(self.s.root / "contexts" / f"{job['context']}.material.json")
            self.assertNotIn("research_outlook", str(context)); self.assertEqual(context["selected_artifacts"], [])
            if job["operation"] == "exploration": self.assertEqual(job["excluded_representations"], ["R"])

    def test_concurrent_results_failure_retry_and_resume(self):
        self.w.dry_run("RUN-1"); job_ids = [p.stem for p in (self.s.root / "runs" / "RUN-1" / "jobs").glob("*.json")]
        with ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(lambda job: self.w.record_result("RUN-1", job, f"result {job}"), job_ids[:4]))
        self.w.record_result("RUN-1", job_ids[4], None, failure="timeout")
        eligible = self.w.resume("RUN-1")
        self.assertIn(job_ids[4], eligible); self.assertNotIn(job_ids[0], eligible)
        self.w.record_result("RUN-1", job_ids[4], "recovered")
        job = self.s.read_json(self.s.root / "runs" / "RUN-1" / "jobs" / f"{job_ids[4]}.json")
        self.assertEqual(job["status"], "SUCCEEDED"); self.assertEqual(len(job["attempts"]), 2)
        self.assertEqual(self.w.validate_run("RUN-1"), [])

    def test_no_alternative_is_a_successful_semantic_output_with_provenance(self):
        self.w.dry_run("RUN-1")
        job_id = "RUN-1-explore-0001"
        recorded = self.w.record_result("RUN-1", job_id, "No natural alternative found.")
        attempt = recorded["attempts"][0]
        self.assertEqual(recorded["status"], "SUCCEEDED")
        self.assertEqual(attempt["status"], "SUCCEEDED")
        self.assertEqual(attempt["operation"], "exploration")
        self.assertEqual(attempt["material_treatment"]["dispatch"], recorded["dispatch"])
        self.assertTrue((self.s.root / attempt["raw_response_path"]).exists())

    def test_interrupted_running_attempt_is_preserved_before_resume(self):
        self.w.dry_run("RUN-1")
        job_id = "RUN-1-ordinary-0001"
        self.w.mark_running("RUN-1", job_id)
        eligible = self.w.resume("RUN-1")
        job = self.s.read_json(self.s.root / "runs" / "RUN-1" / "jobs" / f"{job_id}.json")
        self.assertEqual(job["status"], "RETRYABLE")
        self.assertEqual(job["attempts"][0]["failure"], "interrupted before result recording")
        self.assertIn(job_id, eligible)


if __name__ == "__main__": unittest.main()
