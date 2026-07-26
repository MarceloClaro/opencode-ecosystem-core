# -*- coding: utf-8 -*-
"""
Testes Unitários para a SPEC-935-R227: Merkle Integrity Guard
"""

import unittest
from sdd.spec_engine import spec_registry, spec_verifier
from benchmarks.merkle_integrity_guard import MerkleIntegrityGuard


class TestR227MerkleIntegrityGuard(unittest.TestCase):

    def setUp(self):
        self.guard = MerkleIntegrityGuard()

    def test_spec_r227_registered(self):
        spec = spec_registry.get("SPEC-935-R227")
        self.assertIsNotNone(spec, "SPEC-935-R227 deve estar registrada no SpecRegistry")
        self.assertEqual(spec.status, "green")

    def test_compute_merkle_root(self):
        res = self.guard.compute_merkle_root()
        self.assertIn("merkle_root", res)
        self.assertGreater(len(res["merkle_root"]), 0)
        self.assertGreater(res["total_files"], 0)

    def test_verify_integrity_snapshot_matched(self):
        res = self.guard.compute_merkle_root()
        root = res["merkle_root"]
        verify = self.guard.verify_integrity_snapshot(root)
        self.assertTrue(verify["matched"])
        self.assertEqual(verify["status"], "integrity_verified")

    def test_verify_integrity_snapshot_tampered(self):
        verify = self.guard.verify_integrity_snapshot("0000000000000000000000000000000000000000000000000000000000000000")
        self.assertFalse(verify["matched"])
        self.assertEqual(verify["status"], "tampering_detected")

    def test_spec_verifier_execution(self):
        spec = spec_registry.get("SPEC-935-R227")
        if spec:
            spec.add_criterion("Merkle Integrity Guard validado", lambda out: out.get("merkle") is True)
        res = spec_verifier.verify("SPEC-935-R227", {"merkle": True})
        self.assertTrue(res["verified"])
        self.assertEqual(res["status"], "green")


if __name__ == "__main__":
    unittest.main()
