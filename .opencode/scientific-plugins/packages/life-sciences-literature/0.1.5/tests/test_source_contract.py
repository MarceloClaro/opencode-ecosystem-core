"""Exhaustive skill coverage, citation safety, redaction, and exact raw bytes."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
REGISTRY = json.loads((ROOT / "references" / "source-links.json").read_text(encoding="utf-8"))


def _load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CONTRACT = _load("literature_contract_tests", ROOT / "scripts" / "literature_source_contract.py")
VALIDATOR = _load("literature_validator_tests", ROOT / "scripts" / "validate_source_contract.py")
BIORXIV = _load(
    "literature_biorxiv_tests", SKILLS / "biorxiv-skill" / "scripts" / "rest_request.py"
)
ENTREZ = _load(
    "literature_entrez_tests",
    SKILLS / "ncbi-entrez-skill" / "scripts" / "ncbi_entrez.py",
)
PMC = _load("literature_pmc_tests", SKILLS / "ncbi-pmc-skill" / "scripts" / "ncbi_pmc.py")


def _response(
    data: Any,
    *,
    raw: bytes | None = None,
    url: str = "https://example.org/record",
    content_type: str = "application/json",
    status: int = 200,
) -> Mock:
    response = Mock()
    response.status_code = status
    response.url = url
    response.headers = {"content-type": content_type}
    response.encoding = "utf-8"
    response.content = raw if raw is not None else json.dumps(data).encode("utf-8")
    response.text = response.content.decode("utf-8", errors="replace")
    response.json.return_value = data
    response.raise_for_status.return_value = None
    return response


class ExhaustiveSkillCoverage(unittest.TestCase):
    def test_all_three_skills_are_registered_exactly(self) -> None:
        actual = {path.parent.name for path in SKILLS.glob("*/SKILL.md")}
        self.assertEqual({"biorxiv-skill", "ncbi-entrez-skill", "ncbi-pmc-skill"}, actual)
        self.assertEqual(actual, set(REGISTRY["skills"]))

    def test_complete_plugin_validator(self) -> None:
        self.assertEqual([], VALIDATOR.validate())

    def test_entrez_citations_cover_pubmed_while_pmc_remains_separate(self) -> None:
        entrez_mappings = REGISTRY["skills"]["ncbi-entrez-skill"]["record_url_templates"]
        pmc_mappings = REGISTRY["skills"]["ncbi-pmc-skill"]["record_url_templates"]
        self.assertEqual({"PMID", "DOI"}, {item["identifier_type"] for item in entrez_mappings})
        self.assertEqual(
            {"PMCID", "DOI", "PMID"}, {item["identifier_type"] for item in pmc_mappings}
        )

    def test_all_runtime_clients_apply_contract_and_preserve_raw_bytes(self) -> None:
        for skill in REGISTRY["skills"]:
            clients = [
                path
                for path in (SKILLS / skill / "scripts").glob("*.py")
                if not path.name.startswith("test_")
            ]
            self.assertTrue(clients, skill)
            for client in clients:
                text = client.read_text(encoding="utf-8")
                self.assertIn("apply_source_contract", text, client.name)
                self.assertIn("write_bytes", text, client.name)

    def test_plugin_remains_standalone(self) -> None:
        for script in [
            ROOT / "scripts" / "literature_source_contract.py",
            *SKILLS.glob("*/scripts/*.py"),
        ]:
            if script.name.startswith("test_"):
                continue
            text = script.read_text(encoding="utf-8")
            self.assertNotIn("database_source_contract", text)
            self.assertNotIn("life-science-research", text)


class CanonicalUrlSafety(unittest.TestCase):
    def test_all_registry_templates_construct_expected_urls(self) -> None:
        cases = (
            (
                "biorxiv-skill",
                {"doi": "10.1101/2020.09.09.20191205"},
                None,
                "https://doi.org/10.1101/2020.09.09.20191205",
            ),
            (
                "ncbi-entrez-skill",
                {"pmid": "22966082"},
                "pubmed",
                "https://pubmed.ncbi.nlm.nih.gov/22966082/",
            ),
            (
                "ncbi-entrez-skill",
                {"doi": "10.1093/nar/gkr1184"},
                "pubmed",
                "https://doi.org/10.1093/nar/gkr1184",
            ),
            (
                "ncbi-pmc-skill",
                {"pmcid": "pmc3257301"},
                None,
                "https://pmc.ncbi.nlm.nih.gov/articles/PMC3257301/",
            ),
            (
                "ncbi-pmc-skill",
                {"doi": "10.1093/nar/gkr1184"},
                None,
                "https://doi.org/10.1093/nar/gkr1184",
            ),
            (
                "ncbi-pmc-skill",
                {"pmid": "22966082"},
                None,
                "https://pubmed.ncbi.nlm.nih.gov/22966082/",
            ),
        )
        for skill, record, db, expected in cases:
            with self.subTest(skill=skill, record=record, db=db):
                self.assertEqual(
                    expected, CONTRACT.canonical_record_url(skill, record, database=db)
                )

    def test_entrez_scalar_identifiers_require_exact_database(self) -> None:
        cases = (
            ("pubmed", "https://pubmed.ncbi.nlm.nih.gov/3257301/"),
            ("pmc", None),
            ("gene", None),
            ("protein", None),
            ("nucleotide", None),
            (None, None),
        )
        for db, expected in cases:
            with self.subTest(database=db):
                self.assertEqual(
                    expected,
                    CONTRACT.canonical_record_url(
                        "ncbi-entrez-skill", {"id": "3257301"}, database=db
                    ),
                )

    def test_literature_entrez_does_not_map_nonpublication_accessions(self) -> None:
        for database in (None, "gds", "geoprofiles", "pubmed"):
            with self.subTest(database=database):
                self.assertIsNone(
                    CONTRACT.canonical_record_url(
                        "ncbi-entrez-skill",
                        {"accession": "GSE60450"},
                        database=database,
                    ),
                )

    def test_entrez_dict_id_and_uid_fallbacks_require_exact_database(self) -> None:
        cases = (
            ("pubmed", {"uid": "22966082"}, "https://pubmed.ncbi.nlm.nih.gov/22966082/"),
            ("pmc", {"id": "3257301"}, None),
            ("gene", {"uid": 7157}, None),
            ("protein", {"uid": "22966082"}, None),
            ("nucleotide", {"id": "3257301"}, None),
            (None, {"uid": "22966082"}, None),
        )
        for db, summary, expected in cases:
            with self.subTest(database=db, summary=summary):
                output = {
                    "ok": True,
                    "summary": {
                        **summary,
                        "title": "Substantive record",
                        "canonical_url": "https://attacker.example/fake-record",
                        "canonical_urls": ["javascript:alert('unsafe')"],
                    },
                }
                if db is not None:
                    output["database"] = db
                result = CONTRACT.apply_source_contract(output, "ncbi-entrez-skill")
                if expected is None:
                    self.assertNotIn("canonical_url", result["summary"])
                    self.assertNotIn("canonical_urls", result["summary"])
                    self.assertNotIn("canonical_url", result["sources"][0])
                    self.assertNotIn("canonical_urls", result["sources"][0])
                else:
                    self.assertEqual(expected, result["summary"]["canonical_url"])
                    self.assertEqual(expected, result["sources"][0]["canonical_url"])
                    self.assertNotIn("canonical_urls", result["summary"])

    def test_entrez_uid_fallback_keeps_explicit_multi_mapping_urls(self) -> None:
        result = CONTRACT.apply_source_contract(
            {
                "ok": True,
                "database": "pubmed",
                "summary": {
                    "uid": "22966082",
                    "pmcid": "PMC3257301",
                    "doi": "10.1093/nar/gkr1184",
                    "title": "A database record",
                    "canonical_url": "https://attacker.example/fake-record",
                    "canonical_urls": ["javascript:alert('unsafe')"],
                },
            },
            "ncbi-entrez-skill",
        )
        expected = [
            "https://pubmed.ncbi.nlm.nih.gov/22966082/",
            "https://doi.org/10.1093/nar/gkr1184",
        ]
        self.assertEqual(expected[0], result["summary"]["canonical_url"])
        self.assertEqual(expected, result["summary"]["canonical_urls"])
        self.assertEqual(expected, result["sources"][0]["canonical_urls"])
        self.assertNotIn("pmc.ncbi.nlm.nih.gov", json.dumps(result))

    def test_unsupported_and_hostile_identifiers_do_not_create_links(self) -> None:
        cases = (
            ("biorxiv-skill", {"doi": "../../secret"}, None),
            ("biorxiv-skill", {"doi": "10.1234/../private"}, None),
            ("biorxiv-skill", {"id": "10.1234/example"}, None),
            ("ncbi-entrez-skill", {"pmid": "42&token=secret"}, "pubmed"),
            ("ncbi-entrez-skill", {"pmcid": "PMC12/../../../"}, "pmc"),
            ("ncbi-entrez-skill", {"accession": "GSE123?token=secret"}, "gds"),
            ("ncbi-entrez-skill", {"id": True}, "pubmed"),
            ("unknown-skill", {"pmid": "123"}, "pubmed"),
        )
        for skill, record, db in cases:
            with self.subTest(skill=skill, record=record):
                self.assertIsNone(CONTRACT.canonical_record_url(skill, record, database=db))


class ProvenanceSanitization(unittest.TestCase):
    def test_all_sensitive_aliases_are_redacted(self) -> None:
        sensitive = (
            "api_key",
            "apiKey",
            "apikey",
            "accessToken",
            "authToken",
            "bearerToken",
            "refreshToken",
            "clientSecret",
            "queryText",
            "searchTerm",
            "filterQuery",
            "sequenceData",
            "patientQuery",
            "subject",
            "diagnosis",
            "expression",
            "prompt",
            "email",
            "terms",
            "expr",
            "q",
            "q0",
            "q1",
            "sessionid",
            "PHPSESSID",
            "sid",
            "sas",
            "WebEnv",
            "webenv",
            "private_key",
            "authorization",
            "password",
            "signature",
        )
        query = "&".join(f"{name}=private-{index}" for index, name in enumerate(sensitive))
        result = CONTRACT.sanitize_request_url(
            f"https://user:password@example.org/search?{query}&retmax=10#hidden"
        )
        self.assertIsNotNone(result)
        self.assertNotIn("user:password", result)
        self.assertNotIn("hidden", result)
        values = parse_qs(urlsplit(result).query)
        for index, name in enumerate(sensitive):
            with self.subTest(name=name):
                self.assertEqual(["REDACTED"], values[name])
                self.assertNotIn(f"private-{index}", result)
        self.assertEqual(["10"], values["retmax"])

    def test_rejects_invalid_non_http_urls(self) -> None:
        for value in (
            None,
            "",
            "file:///etc/passwd",
            "javascript:alert(1)",
            "https://",
            "//example.org",
        ):
            with self.subTest(url=value):
                self.assertIsNone(CONTRACT.sanitize_request_url(value))


class EvidenceClassification(unittest.TestCase):
    def test_entrez_esummary_uid_record_gets_pubmed_canonical_url(self) -> None:
        body = {
            "header": {"type": "esummary", "version": "0.3"},
            "result": {
                "uids": ["22966082"],
                "22966082": {
                    "uid": "22966082",
                    "pubdate": "2011 Dec 19",
                    "title": "Database resources of the National Center for Biotechnology Information",
                    "canonical_url": "https://attacker.example/fake-record",
                    "canonical_urls": ["javascript:alert('unsafe')"],
                },
            },
        }
        response = _response(
            body,
            url=(
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
                "?db=pubmed&id=22966082&retmode=json"
            ),
        )
        with patch.object(ENTREZ.requests, "get", return_value=response):
            result = ENTREZ.execute(
                {
                    "endpoint": "esummary",
                    "params": {"db": "pubmed", "id": "22966082", "retmode": "json"},
                    "record_path": "result.22966082",
                    "response_format": "json",
                }
            )
        expected = "https://pubmed.ncbi.nlm.nih.gov/22966082/"
        self.assertTrue(result["ok"], result)
        self.assertEqual(expected, result["summary"]["canonical_url"])
        self.assertNotIn("canonical_urls", result["summary"])
        self.assertEqual(expected, result["sources"][0]["canonical_url"])

    def test_evidence_sources_are_claim_supporting_and_canonical(self) -> None:
        output = {
            "ok": True,
            "records": [{"doi": "10.1101/2020.09.09.20191205", "title": "A study"}],
        }
        result = CONTRACT.apply_source_contract(
            output,
            "biorxiv-skill",
            "https://api.biorxiv.org/details?queryText=patient-secret",
        )
        self.assertTrue(result["sources"][0]["supports_claim"])
        self.assertEqual("evidence", result["sources"][0]["kind"])
        self.assertEqual(
            "https://doi.org/10.1101/2020.09.09.20191205",
            result["records"][0]["canonical_url"],
        )
        self.assertNotIn("patient-secret", json.dumps(result["sources"]))

    def test_canonical_only_payload_is_checked_after_reserved_fields_are_removed(self) -> None:
        output = CONTRACT.apply_source_contract(
            {
                "ok": True,
                "summary": {
                    "canonical_url": "https://attacker.example/fake-record",
                    "canonical_urls": ["javascript:alert('unsafe')"],
                },
            },
            "ncbi-entrez-skill",
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
        )
        self.assertEqual({}, output["summary"])
        self.assertNotIn("sources", output)
        self.assertFalse(output["checked_sources"][0]["supports_claim"])
        self.assertEqual("empty", output["checked_sources"][0]["reason"])

    def test_real_records_override_stale_top_level_empty_indicators(self) -> None:
        cases = (
            {
                "record_count_returned": 0,
                "records": [
                    {"doi": "10.1101/2020.09.09.20191205", "title": "A study"},
                ],
            },
            {
                "records": [],
                "summary": {
                    "payload": {
                        "results": [
                            {"doi": "10.1101/2020.09.09.20191205", "title": "A study"},
                        ]
                    }
                },
            },
        )
        for payload in cases:
            with self.subTest(payload=payload):
                output = CONTRACT.apply_source_contract(
                    {"ok": True, **payload},
                    "biorxiv-skill",
                    "https://api.biorxiv.org/details/biorxiv/2026-08-06/2026-08-07/0/json",
                )
                self.assertTrue(output["sources"][0]["supports_claim"])
                self.assertNotIn("checked_sources", output)

    def test_reserved_canonical_fields_are_removed_beyond_annotation_limit(self) -> None:
        records = [{"title": f"record {index}"} for index in range(101)]
        records[100]["canonical_url"] = "https://attacker.example/fake-record"
        records[100]["canonical_urls"] = ["javascript:alert('unsafe')"]
        nested = records[100]
        for _ in range(8):
            nested["nested"] = {}
            nested = nested["nested"]
        nested["canonical_url"] = "https://attacker.example/deep-record"
        output = CONTRACT.apply_source_contract(
            {"ok": True, "records": records},
            "biorxiv-skill",
            "https://api.biorxiv.org/details/biorxiv/2026-08-06/2026-08-07/0/json",
        )
        self.assertNotIn("canonical_url", output["records"][100])
        self.assertNotIn("canonical_urls", output["records"][100])
        nested = output["records"][100]
        for _ in range(8):
            nested = nested["nested"]
        self.assertNotIn("canonical_url", nested)

    def test_reserved_canonical_fields_are_removed_from_existing_sources(self) -> None:
        upstream = {
            "name": "Upstream",
            "url": "https://example.org/evidence",
            "kind": "evidence",
            "supports_claim": True,
            "canonical_url": "https://attacker.example/fake-record",
            "canonical_urls": ["javascript:alert('unsafe')"],
        }
        checked = {
            "name": "Checked",
            "url": "https://example.org/check",
            "kind": "checked",
            "supports_claim": False,
            "canonical_url": "https://attacker.example/fake-check",
            "canonical_urls": ["javascript:alert('unsafe')"],
        }
        output = CONTRACT.apply_source_contract(
            {
                "ok": True,
                "records": [{"doi": "10.1101/2020.09.09.20191205", "title": "A study"}],
                "sources": [upstream],
                "checked_sources": [checked],
            },
            "biorxiv-skill",
            "https://api.biorxiv.org/details/biorxiv/2026-08-06/2026-08-07/0/json",
        )
        for item in (output["sources"][0], output["checked_sources"][0]):
            self.assertNotIn("canonical_url", item)
            self.assertNotIn("canonical_urls", item)
        self.assertEqual(
            "https://doi.org/10.1101/2020.09.09.20191205",
            output["sources"][-1]["canonical_url"],
        )

    def test_zero_strings_collection_shapes_and_deep_records(self) -> None:
        for count in ("0", "  0  ", "+0", "-0", "00", "0.0", ".0", "0e12"):
            with self.subTest(zero_count=count):
                output = CONTRACT.apply_source_contract(
                    {
                        "ok": True,
                        "summary": {"eSearchResult": {"Count": count, "IdList": ""}},
                    },
                    "ncbi-entrez-skill",
                )
                self.assertNotIn("sources", output)
                self.assertEqual("empty", output["checked_sources"][0]["reason"])

        for value in ("malformed", 7):
            with self.subTest(malformed_records=value):
                output = CONTRACT.apply_source_contract(
                    {"ok": True, "records": value},
                    "biorxiv-skill",
                )
                self.assertNotIn("sources", output)
                self.assertEqual("empty", output["checked_sources"][0]["reason"])

        for value in ([{"doi": "10.1101/2020.09.09.20191205"}], {"uid": "22966082"}):
            with self.subTest(valid_records=value):
                output = CONTRACT.apply_source_contract(
                    {"ok": True, "records": value},
                    "biorxiv-skill",
                )
                self.assertTrue(output["sources"][0]["supports_claim"])

        entrez = CONTRACT.apply_source_contract(
            {
                "ok": True,
                "database": "pubmed",
                "summary": {"Count": "0", "IdList": "22966082"},
            },
            "ncbi-entrez-skill",
        )
        self.assertTrue(entrez["sources"][0]["supports_claim"])

        deep: dict[str, Any] = {
            "records": [{"doi": "10.1101/2020.09.09.20191205", "title": "A study"}]
        }
        for index in range(10):
            deep = {f"wrapper_{index}": deep}
        output = CONTRACT.apply_source_contract(
            {"ok": True, "summary": {"Count": "0", "payload": deep}},
            "biorxiv-skill",
        )
        self.assertTrue(output["sources"][0]["supports_claim"])

        cycle: dict[str, Any] = {}
        cycle["self"] = cycle
        self.assertEqual("empty", CONTRACT._summary_mode(cycle))

    def test_record_collections_suppress_only_structural_metadata(self) -> None:
        metadata_only = (
            {"records": [{"__typename": "Article"}]},
            {"records": [{"__type": {"name": "Article", "fields": [{"name": "doi"}]}}]},
            {"summary": {"results": [{"schema": "v1"}]}},
            {"summary": {"items": [{"extensions": {"tracing": {"duration": 23}}}]}},
            {
                "records": [
                    {
                        "cursor": "next-page",
                        "meta": {"page": 1},
                        "metadata": {"version": "v1"},
                    }
                ]
            },
            {"records": [{"payload": [{"metadata": {"schema": "v1"}}]}]},
            {"records": [{"data": None}]},
        )
        for payload in metadata_only:
            with self.subTest(metadata_only=payload):
                output = CONTRACT.apply_source_contract(
                    {"ok": True, **payload},
                    "biorxiv-skill",
                    "https://api.biorxiv.org/details/biorxiv/2026-08-01/2026-08-07/0/json",
                )
                self.assertNotIn("sources", output)
                self.assertFalse(output["checked_sources"][0]["supports_claim"])
                self.assertEqual("empty", output["checked_sources"][0]["reason"])

        evidence_bearing = (
            {
                "records": [
                    {
                        "__typename": "Article",
                        "doi": "10.1101/2020.09.09.20191205",
                    }
                ]
            },
            {
                "summary": {
                    "results": [
                        {
                            "schema": "v1",
                            "record": {"doi": "10.1101/2020.09.09.20191205"},
                        }
                    ]
                }
            },
            {
                "summary": {
                    "items": [
                        {
                            "extensions": {"tracing": {"duration": 23}},
                            "data": {"records": [{"doi": "10.1101/2020.09.09.20191205"}]},
                        }
                    ]
                }
            },
        )
        for payload in evidence_bearing:
            with self.subTest(evidence_bearing=payload):
                output = CONTRACT.apply_source_contract(
                    {"ok": True, **payload},
                    "biorxiv-skill",
                    "https://api.biorxiv.org/details/biorxiv/2026-08-01/2026-08-07/0/json",
                )
                self.assertTrue(output["sources"][0]["supports_claim"])
                self.assertNotIn("checked_sources", output)

        cycle: dict[str, Any] = {}
        cycle["metadata"] = [cycle]
        self.assertFalse(CONTRACT._has_collection_value([cycle]))
        cycle["record"] = {"doi": "10.1101/2020.09.09.20191205"}
        self.assertTrue(CONTRACT._has_collection_value([cycle]))

    def test_http_200_diagnostics_are_not_evidence_but_real_sibling_records_are(self) -> None:
        diagnostic_cases = (
            ({"error": "not found"}, "failure"),
            (
                {
                    "errors": [
                        {
                            "message": "not found",
                            "details": {"code": "missing", "retryable": False},
                        }
                    ]
                },
                "failure",
            ),
            ({"warning": "partial response"}, "metadata"),
            (
                {"warnings": ["partial response", {"message": "retry later"}]},
                "metadata",
            ),
            (
                {"messages": ["no matching records", {"message": "try another query"}]},
                "metadata",
            ),
            (
                {
                    "payload": {
                        "errors": [
                            {
                                "message": "not found",
                                "details": {"records": [{"doi": "10.1101/2020.09.09.20191205"}]},
                            }
                        ]
                    }
                },
                "failure",
            ),
        )
        for summary, reason in diagnostic_cases:
            with self.subTest(summary=summary):
                output = CONTRACT.apply_source_contract(
                    {"ok": True, "status_code": 200, "summary": summary},
                    "biorxiv-skill",
                    "https://api.biorxiv.org/details/biorxiv/2026-08-01/2026-08-07/0/json",
                )
                self.assertNotIn("sources", output)
                self.assertFalse(output["checked_sources"][0]["supports_claim"])
                self.assertEqual(reason, output["checked_sources"][0]["reason"])

        evidence_summaries = (
            {
                "error": "one record could not be expanded",
                "records": [{"doi": "10.1101/2020.09.09.20191205", "title": "A study"}],
            },
            {
                "payload": {
                    "errors": [
                        {
                            "message": "ignored diagnostic identifier",
                            "doi": "10.1101/2025.01.01.123456",
                        }
                    ],
                    "response": {
                        "records": [
                            {
                                "doi": "10.1101/2020.09.09.20191205",
                                "title": "A study",
                            }
                        ]
                    },
                }
            },
        )
        for summary in evidence_summaries:
            with self.subTest(summary=summary):
                output = CONTRACT.apply_source_contract(
                    {"ok": True, "status_code": 200, "summary": summary},
                    "biorxiv-skill",
                    "https://api.biorxiv.org/details/biorxiv/2026-08-01/2026-08-07/0/json",
                )
                self.assertTrue(output["sources"][0]["supports_claim"])
                self.assertEqual(
                    "https://doi.org/10.1101/2020.09.09.20191205",
                    output["sources"][0]["canonical_url"],
                )
                self.assertNotIn("checked_sources", output)

    def test_empty_metadata_connectivity_and_failures_never_become_evidence(
        self,
    ) -> None:
        cases = (
            ({"ok": True, "records": [], "record_count_returned": 0}, None),
            ({"ok": True, "records": [True]}, None),
            ({"ok": True, "summary": {"results": [True]}}, None),
            ({"ok": True, "summary": {"status": "ok", "version": "1"}}, None),
            ({"ok": True, "summary": {"service": {"status": "ok", "count": 0}}}, None),
            ({"ok": True, "summary": {"results": [], "total": 0}}, None),
            (
                {
                    "ok": True,
                    "summary": {"data": None, "extensions": {"tracing": {"duration": 23}}},
                },
                None,
            ),
            (
                {
                    "ok": True,
                    "endpoint": "einfo",
                    "summary": {"dbinfo": "service details"},
                },
                None,
            ),
            (
                {"ok": True, "endpoint": "egquery", "summary": {"result": "routing"}},
                None,
            ),
            (
                {
                    "ok": True,
                    "endpoint": "espell",
                    "summary": {"correction": "spelling"},
                },
                None,
            ),
            (
                {"ok": True, "path": "fields", "summary": {"field": "schema details"}},
                None,
            ),
            ({"ok": True, "summary": {"__typename": "Query"}}, None),
            ({"ok": True, "summary": {"__type": {"name": "Query"}}}, None),
            ({"ok": True, "summary": {"__schema": {"queryType": "Query"}}}, None),
            ({"ok": True, "summary": {"title": "endpoint status"}}, "connectivity"),
        )
        for output, mode in cases:
            with self.subTest(output=output, mode=mode):
                result = CONTRACT.apply_source_contract(
                    output,
                    "ncbi-entrez-skill",
                    "https://eutils.ncbi.nlm.nih.gov/?api_key=secret",
                    mode=mode,
                )
                self.assertNotIn("sources", result)
                self.assertFalse(result["checked_sources"][0]["supports_claim"])
                self.assertEqual("checked", result["checked_sources"][0]["kind"])
        failed = {"ok": False, "error": {"code": "network"}}
        self.assertEqual(failed, CONTRACT.apply_source_contract(failed, "ncbi-entrez-skill"))

    def test_scalar_pubmed_search_ids_keep_shape_and_use_publication_urls(self) -> None:
        result = CONTRACT.apply_source_contract(
            {"ok": True, "database": "pubmed", "records": ["3257301"]},
            "ncbi-entrez-skill",
        )
        self.assertEqual(["3257301"], result["records"])
        self.assertEqual(
            "https://pubmed.ncbi.nlm.nih.gov/3257301/",
            result["sources"][0]["canonical_url"],
        )

    def test_biorxiv_publication_linkage_exposes_both_safe_doi_urls(self) -> None:
        result = CONTRACT.apply_source_contract(
            {
                "ok": True,
                "records": [
                    {
                        "preprint_doi": "10.1101/2020.09.09.20191205",
                        "published_doi": "10.1038/s41586-020-2649-2",
                        "published_doi_url": "https://evil.example/?api_key=secret",
                        "title": "A linked paper",
                    }
                ],
            },
            "biorxiv-skill",
            "https://api.biorxiv.org/pubs/biorxiv/2020-03-01/2020-03-30/0",
        )
        urls = [
            "https://doi.org/10.1101/2020.09.09.20191205",
            "https://doi.org/10.1038/s41586-020-2649-2",
        ]
        self.assertEqual(urls[0], result["records"][0]["canonical_url"])
        self.assertEqual(urls, result["records"][0]["canonical_urls"])
        self.assertEqual(urls, result["sources"][0]["canonical_urls"])
        self.assertNotIn("evil.example", json.dumps(result["sources"]))

    def test_biorxiv_documented_details_and_pubs_fields_emit_both_doi_urls(self) -> None:
        preprint_url = "https://doi.org/10.1101/2020.09.09.20191205"
        published_url = "https://doi.org/10.1038/s41586-020-2649-2"
        for endpoint, record in (
            (
                "details",
                {
                    "doi": "10.1101/2020.09.09.20191205",
                    "published": "10.1038/s41586-020-2649-2",
                },
            ),
            (
                "pubs",
                {
                    "biorxiv_doi": "10.1101/2020.09.09.20191205",
                    "published_doi": "10.1038/s41586-020-2649-2",
                },
            ),
        ):
            with self.subTest(endpoint=endpoint):
                result = CONTRACT.apply_source_contract(
                    {"ok": True, "records": [{**record, "title": "A linked paper"}]},
                    "biorxiv-skill",
                    f"https://api.biorxiv.org/{endpoint}/biorxiv/example",
                )
                self.assertEqual(preprint_url, result["records"][0]["canonical_url"])
                self.assertEqual(
                    [preprint_url, published_url],
                    result["records"][0]["canonical_urls"],
                )
                self.assertEqual(
                    [preprint_url, published_url],
                    result["sources"][0]["canonical_urls"],
                )

    def test_orchestration_propagates_only_evidence_bearing_sources(self) -> None:
        valid = {
            "name": "PubMed",
            "url": "https://pubmed.ncbi.nlm.nih.gov/1/",
            "kind": "evidence",
            "supports_claim": True,
        }
        checked = {
            "name": "Checked",
            "url": "https://example.org/",
            "kind": "checked",
            "supports_claim": False,
        }
        malformed = {
            "name": "Unsupported",
            "url": "https://example.org/",
            "kind": "evidence",
            "supports_claim": False,
        }
        self.assertEqual(
            [valid],
            CONTRACT.evidence_sources(
                {
                    "ok": True,
                    "sources": [valid, checked, malformed],
                    "checked_sources": [checked],
                },
                {"ok": True, "sources": [valid]},
                {"ok": False, "sources": [valid]},
            ),
        )


class BiorxivOriginSafety(unittest.TestCase):
    def test_rejects_unregistered_base_and_absolute_path_before_network(self) -> None:
        payloads = (
            {"base_url": "https://example.org", "path": "details"},
            {
                "base_url": "https://api.biorxiv.org",
                "path": "https://example.org/details",
            },
        )
        for payload in payloads:
            with (
                self.subTest(payload=payload),
                patch.object(BIORXIV.requests, "Session") as factory,
            ):
                output = BIORXIV.execute(payload)
            self.assertFalse(output["ok"])
            self.assertEqual("invalid_input", output["error"]["code"])
            self.assertNotIn("sources", output)
            self.assertNotIn("checked_sources", output)
            factory.assert_not_called()

    def test_rejects_cross_host_final_response_and_closes_session(self) -> None:
        response = _response(
            {"collection": [{"doi": "10.1101/2020.09.09.20191205"}]},
            url="https://example.org/details",
        )
        with patch.object(BIORXIV.requests, "Session") as factory:
            session = factory.return_value
            session.request.return_value = response
            output = BIORXIV.execute({"base_url": "https://api.biorxiv.org", "path": "details"})
        self.assertFalse(output["ok"])
        self.assertEqual("invalid_response", output["error"]["code"])
        self.assertNotIn("sources", output)
        self.assertNotIn("checked_sources", output)
        session.request.assert_called_once_with(
            "GET",
            "https://api.biorxiv.org/details",
            params={},
            timeout=30,
            allow_redirects=False,
        )
        session.close.assert_called_once_with()

    def test_closes_session_after_success(self) -> None:
        response = _response(
            {"collection": [{"doi": "10.1101/2020.09.09.20191205"}]},
            url="https://api.biorxiv.org/details",
        )
        with patch.object(BIORXIV.requests, "Session") as factory:
            session = factory.return_value
            session.request.return_value = response
            output = BIORXIV.execute({"base_url": "https://api.biorxiv.org", "path": "details"})
        self.assertTrue(output["ok"], output)
        self.assertIn("sources", output)
        session.close.assert_called_once_with()


class RawOutputPreservation(unittest.TestCase):
    def test_biorxiv_preserves_json_http_bytes_exactly(self) -> None:
        raw = b'{ "collection" : [ { "doi" : "10.1101/2020.09.09.20191205" } ] }\n'
        body = {"collection": [{"doi": "10.1101/2020.09.09.20191205"}]}
        response = _response(body, raw=raw, url="https://api.biorxiv.org/details?api_key=secret")
        with (
            tempfile.TemporaryDirectory() as directory,
            patch.object(BIORXIV.requests, "Session") as factory,
        ):
            session = factory.return_value
            session.request.return_value = response
            path = str(Path(directory) / "preprint.json")
            output = BIORXIV.execute(
                {
                    "base_url": "https://api.biorxiv.org",
                    "path": "details/biorxiv/doi",
                    "save_raw": True,
                    "raw_output_path": path,
                }
            )
            self.assertEqual(raw, Path(path).read_bytes())
            self.assertIn("sources", output)
            self.assertNotIn("secret", json.dumps(output["sources"]))

    def test_entrez_preserves_original_json_xml_and_fasta_bytes(self) -> None:
        cases = (
            (
                {"esearchresult": {"idlist": ["22966082"]}},
                b'{ "esearchresult": { "idlist": ["22966082"] } }\n',
                "application/json",
                "json",
            ),
            (
                None,
                b"\xef\xbb\xbf<result><record>caf\xc3\xa9</record></result>\n",
                "application/xml",
                "xml",
            ),
            (None, b">NP_000537.3 TP53\r\nMEEPQSDPSV\r\n", "text/plain", "text"),
        )
        for body, raw, content_type, response_format in cases:
            with self.subTest(format=response_format), tempfile.TemporaryDirectory() as directory:
                response = _response(body, raw=raw, content_type=content_type)
                response.text = raw.decode("utf-8-sig")
                path = str(Path(directory) / f"result.{response_format}")
                with patch.object(ENTREZ.requests, "get", return_value=response):
                    output = ENTREZ.execute(
                        {
                            "endpoint": "efetch",
                            "params": {"db": "pubmed"},
                            "response_format": response_format,
                            "save_raw": True,
                            "raw_output_path": path,
                        }
                    )
                self.assertTrue(output["ok"], output)
                self.assertEqual(raw, Path(path).read_bytes())

    def test_pmc_preserves_each_metadata_response_and_adds_page_sidecars(self) -> None:
        listing = b"<ListBucketResult><CommonPrefixes><Prefix>PMC3257301.1/</Prefix></CommonPrefixes><CommonPrefixes><Prefix>PMC3257301.2/</Prefix></CommonPrefixes></ListBucketResult>"
        first = b'{ "pmcid" : "PMC3257301", "version" : 1, "citation" : "First" }\n'
        second = b'{"pmcid":"PMC3257301", "version":2,"citation":"Second"}\r\n'
        responses = [
            _response(None, raw=listing, content_type="application/xml"),
            _response(json.loads(first), raw=first),
            _response(json.loads(second), raw=second),
        ]
        with (
            tempfile.TemporaryDirectory() as directory,
            patch.object(PMC.requests, "Session") as factory,
        ):
            factory.return_value.get.side_effect = responses
            path = str(Path(directory) / "metadata.json")
            output = PMC.execute(
                {
                    "params": {"id": "PMC3257301"},
                    "max_items": 2,
                    "save_raw": True,
                    "raw_output_path": path,
                }
            )
            self.assertTrue(output["ok"], output)
            self.assertEqual(first, Path(path).read_bytes())
            self.assertEqual(path, output["raw_page_paths"][0])
            self.assertTrue(output["raw_page_paths"][1].endswith("metadata.page-2.json"))
            self.assertEqual(second, Path(output["raw_page_paths"][1]).read_bytes())
            self.assertTrue(output["sources"][0]["supports_claim"])
            factory.assert_called_once_with()
            factory.return_value.close.assert_called_once_with()

    def test_pmc_empty_resolution_is_checked_only(self) -> None:
        listing = b"<ListBucketResult></ListBucketResult>"
        with patch.object(PMC.requests, "Session") as factory:
            factory.return_value.get.return_value = _response(
                None, raw=listing, content_type="application/xml"
            )
            output = PMC.execute({"params": {"id": "PMC3257301"}})
        self.assertEqual([], output["records"])
        self.assertNotIn("sources", output)
        self.assertFalse(output["checked_sources"][0]["supports_claim"])
        factory.assert_called_once_with()
        factory.return_value.close.assert_called_once_with()

    def test_network_failures_never_leak_secret_or_query_exception_text(self) -> None:
        failure = BIORXIV.requests.RequestException(
            "https://example.org/?api_key=top-secret&queryText=patient-name"
        )
        with patch.object(BIORXIV.requests, "Session") as factory:
            factory.return_value.request.side_effect = failure
            output = BIORXIV.execute({"base_url": "https://api.biorxiv.org", "path": "details"})
        self.assertFalse(output["ok"])
        self.assertNotIn("top-secret", json.dumps(output))
        self.assertNotIn("patient-name", json.dumps(output))


if __name__ == "__main__":
    unittest.main()
