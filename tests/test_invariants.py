import tempfile
import unittest
from pathlib import Path
from math_automation.store import Store


class PortableInvariants(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.root = Path(self.temp.name); self.s = Store(self.root); self.s.init("test")
        self.s.create_artifact("problem", "PROBLEM-Q4", {"statement": "Investigate whether a smooth rational quartic C subset P3 is an STCI."})
        self.s.create_artifact("representation", "REP-A", {"problem": "PROBLEM-Q4", "description": "surface-divisor framing"})
        self.s.create_artifact("representation", "REP-B", {"problem": "PROBLEM-Q4", "description": "deformation framing"})
        self.s.create_artifact("evidence", "E-1", {"claim": "A computation result", "kind": "computation"})
        self.s.create_node("NODE-A", "PROBLEM-Q4"); self.s.create_node("NODE-B", "PROBLEM-Q4")

    def tearDown(self): self.temp.cleanup()

    def test_nodes_diverge_and_messages_do_not_mutate(self):
        self.s.proposal("UP-A", "NODE-A", {"representations": ["REP-A"], "interpretation": "A local view"}); self.s.decide("UP-A", "accepted")
        before = self.s.node("NODE-B")
        self.s.message("MSG-1", "NODE-A", "NODE-B", ["E-1"], "consider this evidence")
        self.assertEqual(before, self.s.node("NODE-B"))
        self.assertNotEqual(self.s.node("NODE-A")["representations"], self.s.node("NODE-B")["representations"])

    def test_proposal_lifecycle_and_rejection_preservation(self):
        self.s.proposal("UP-B", "NODE-B", {"representations": ["REP-B"]}); self.s.decide("UP-B", "rejected")
        self.assertEqual(self.s.find("REP-B")["payload"]["description"], "deformation framing")
        self.assertEqual(self.s.read_json(self.root / "proposals" / "UP-B.json")["status"], "rejected")

    def test_context_has_no_global_outlook_and_operations_differ(self):
        c = self.s.context("CTX-1", "NODE-B", ["E-1", "REP-A"], "ordinary")
        ordinary = self.s.treatment("D-ORD", c["id"], "ordinary")
        explore = self.s.treatment("D-EXP", c["id"], "exploration", ["REP-A"])
        self.assertTrue(c["no_canonical_outlook"])
        self.assertNotEqual(ordinary["instruction"], explore["instruction"])
        self.assertIn("no natural alternative", explore["instruction"])

    def test_invocation_provenance_and_validation(self):
        c = self.s.context("CTX-2", "NODE-A", ["E-1"], "ordinary")
        self.s.treatment("D-2", c["id"], "ordinary")
        self.s.invocation("INV-1", "D-2", "A candidate observation.")
        self.assertEqual(self.s.validate(), [])


if __name__ == "__main__": unittest.main()
