# -*- coding: utf-8 -*-
"""
Testes Unitários para a SPEC-935-R226: Internal Audit Harness
"""

import unittest
from sdd.spec_engine import spec_registry, spec_verifier
from benchmarks.internal_audit_harness import InternalAuditHarness


class TestR226InternalAuditHarness(unittest.TestCase):

    def setUp(self):
        self.harness = InternalAuditHarness()

    def test_spec_r226_registered(self):
        spec = spec_registry.get("SPEC-935-R226")
        self.assertIsNotNone(spec, "SPEC-935-R226 deve estar registrada no SpecRegistry")
        self.assertEqual(spec.status, "green")

    def test_generate_audit_certificate(self):
        cert = self.harness.generate_audit_certificate()
        self.assertIn("certificate_id", cert)
        self.assertIn("signature_sha256", cert)
        self.assertEqual(cert["status"], "internal_audit_passed")

    def test_verify_internal_integrity(self):
        res = self.harness.verify_internal_integrity()
        self.assertTrue(res["is_auditable"])
        self.assertIn("certificate", res)

    def test_spec_verifier_execution(self):
        spec = spec_registry.get("SPEC-935-R226")
        if spec:
            spec.add_criterion("Harness Interno Auditável validado", lambda out: out.get("audit") is True)
        res = spec_verifier.verify("SPEC-935-R226", {"audit": True})
        self.assertTrue(res["verified"])
        self.assertEqual(res["status"], "green")


if __name__ == "__main__":
    unittest.main()
