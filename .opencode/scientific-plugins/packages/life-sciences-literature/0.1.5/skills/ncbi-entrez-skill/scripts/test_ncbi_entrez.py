from __future__ import annotations

import json
import unittest
from unittest.mock import Mock, patch

import ncbi_entrez


class EntrezErrorTest(unittest.TestCase):
    @patch.dict("ncbi_entrez.os.environ", {"NCBI_API_KEY": "top-secret"}, clear=False)
    @patch("ncbi_entrez.requests.get")
    def test_http_errors_do_not_expose_ncbi_api_key(self, get: Mock) -> None:
        failed_response = Mock(status_code=500)
        failure = ncbi_entrez.requests.HTTPError(
            "500 for https://eutils.ncbi.nlm.nih.gov/?api_key=top-secret",
            response=failed_response,
        )
        get.return_value.raise_for_status.side_effect = failure

        output = ncbi_entrez.execute(
            {"endpoint": "esearch", "params": {"db": "pubmed", "term": "example"}}
        )

        self.assertFalse(output["ok"])
        self.assertEqual(output["error"]["message"], "NCBI Entrez returned HTTP 500.")
        self.assertEqual(get.call_args.kwargs["params"]["api_key"], "top-secret")
        self.assertNotIn("top-secret", json.dumps(output))

    @patch("ncbi_entrez.requests.get")
    def test_non_pubmed_databases_are_rejected_before_any_request(self, get: Mock) -> None:
        for database in ("gene", "protein", "nucleotide", "pmc", "gds", "geoprofiles", None):
            with self.subTest(database=database):
                with self.assertRaisesRegex(ValueError, "params.db=pubmed"):
                    ncbi_entrez.execute({"endpoint": "esearch", "params": {"db": database}})
        get.assert_not_called()

    @patch("ncbi_entrez.requests.get")
    def test_non_pubmed_link_origins_are_rejected_before_any_request(self, get: Mock) -> None:
        with self.assertRaisesRegex(ValueError, "params.dbfrom=pubmed"):
            ncbi_entrez.execute(
                {
                    "endpoint": "elink",
                    "params": {"db": "pubmed", "dbfrom": "gds", "id": "200000001"},
                }
            )
        get.assert_not_called()

    @patch("ncbi_entrez.requests.get")
    def test_non_pubmed_link_names_are_rejected_before_any_request(self, get: Mock) -> None:
        for linkname in (
            "gene_pubmed",
            "gds_pubmed",
            "pmc_pubmed",
            "pubmed_gene",
            "pubmed_pmc",
            "pubmed_pubmedevil",
            "",
            7157,
        ):
            with self.subTest(linkname=linkname):
                with self.assertRaisesRegex(ValueError, "PubMed-to-PubMed"):
                    ncbi_entrez.execute(
                        {
                            "endpoint": "elink",
                            "params": {"db": "pubmed", "linkname": linkname, "id": "7157"},
                        }
                    )
        get.assert_not_called()

    def test_pubmed_to_pubmed_link_names_remain_available(self) -> None:
        for linkname in ("pubmed_pubmed", "pubmed_pubmed_refs", "PUBMED_PUBMED_CITEDIN"):
            with self.subTest(linkname=linkname):
                parsed = ncbi_entrez.parse_input(
                    {
                        "endpoint": "elink",
                        "params": {"db": "pubmed", "linkname": linkname, "id": "7157"},
                    }
                )
                self.assertEqual(linkname, parsed["params"]["linkname"])

    def test_pubmed_database_names_are_case_insensitive(self) -> None:
        parsed = ncbi_entrez.parse_input(
            {"endpoint": "elink", "params": {"db": "PubMed", "dbfrom": "PUBMED"}}
        )
        self.assertEqual("PubMed", parsed["params"]["db"])


if __name__ == "__main__":
    unittest.main()
