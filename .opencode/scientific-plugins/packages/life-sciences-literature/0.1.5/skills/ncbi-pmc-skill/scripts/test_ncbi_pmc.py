from __future__ import annotations

import json
import unittest
from unittest.mock import Mock, call, patch

import ncbi_pmc


def response(*, data=None, text: str = "", status_code: int = 200) -> Mock:
    result = Mock()
    result.status_code = status_code
    result.text = text
    result.json.return_value = data
    result.raise_for_status.return_value = None
    return result


class PmcCloudTest(unittest.TestCase):
    @patch("ncbi_pmc.requests.Session")
    def test_returns_current_versioned_metadata_and_file_urls(self, factory: Mock) -> None:
        session = factory.return_value
        session.get.side_effect = [
            response(
                text=(
                    "<ListBucketResult>"
                    "<CommonPrefixes><Prefix>PMC3257301.1/</Prefix></CommonPrefixes>"
                    "</ListBucketResult>"
                )
            ),
            response(
                data={
                    "pmcid": "PMC3257301",
                    "version": 1,
                    "citation": "Example citation",
                    "is_pmc_openaccess": True,
                    "is_retracted": False,
                    "license_code": "CC BY",
                    "pdf_url": "s3://pmc-oa-opendata/PMC3257301.1/PMC3257301.1.pdf?md5=x",
                    "xml_url": "s3://pmc-oa-opendata/PMC3257301.1/PMC3257301.1.xml?md5=y",
                    "media_urls": [],
                }
            ),
        ]

        output = ncbi_pmc.execute({"params": {"id": "PMC3257301"}, "max_items": 10})

        self.assertTrue(output["ok"])
        self.assertEqual(output["source"], "ncbi-pmc-cloud")
        self.assertEqual(output["record_count_available"], 1)
        record = output["records"][0]
        self.assertEqual(record["license_code"], "CC BY")
        self.assertFalse(record["is_retracted"])
        self.assertEqual(
            record["pdf_url"],
            "https://pmc-oa-opendata.s3.amazonaws.com/PMC3257301.1/PMC3257301.1.pdf?md5=x",
        )
        factory.assert_called_once_with()
        session.close.assert_called_once_with()

    @patch("ncbi_pmc.requests.Session")
    def test_reuses_one_session_across_identifier_versions_and_metadata(
        self, factory: Mock
    ) -> None:
        session = factory.return_value
        session.get.side_effect = [
            response(data={"esearchresult": {"idlist": ["3257301"], "count": "1"}}),
            response(
                text=(
                    "<ListBucketResult>"
                    "<CommonPrefixes><Prefix>PMC3257301.1/</Prefix></CommonPrefixes>"
                    "<CommonPrefixes><Prefix>PMC3257301.2/</Prefix></CommonPrefixes>"
                    "</ListBucketResult>"
                )
            ),
            response(data={"pmcid": "PMC3257301", "version": 1}),
            response(data={"pmcid": "PMC3257301", "version": 2}),
        ]

        output = ncbi_pmc.execute(
            {"params": {"id": "10.1000/example", "retmax": 4}, "timeout_sec": 17}
        )

        self.assertTrue(output["ok"], output)
        self.assertEqual(output["record_count_returned"], 2)
        factory.assert_called_once_with()
        self.assertEqual(
            session.get.call_args_list,
            [
                call(
                    ncbi_pmc.PMC_ESEARCH_URL,
                    params=ncbi_pmc._ncbi_common_params(
                        {
                            "db": "pmc",
                            "term": '"10.1000/example"[doi]',
                            "retmode": "json",
                            "retmax": 4,
                        }
                    ),
                    timeout=17,
                ),
                call(
                    ncbi_pmc.PMC_S3_BASE_URL,
                    params={
                        "list-type": "2",
                        "prefix": "PMC3257301.",
                        "delimiter": "/",
                    },
                    timeout=17,
                ),
                call(
                    f"{ncbi_pmc.PMC_S3_BASE_URL}/metadata/PMC3257301.1.json",
                    timeout=17,
                ),
                call(
                    f"{ncbi_pmc.PMC_S3_BASE_URL}/metadata/PMC3257301.2.json",
                    timeout=17,
                ),
            ],
        )
        session.close.assert_called_once_with()

    @patch("ncbi_pmc.requests.Session")
    def test_closes_session_when_version_metadata_is_missing(self, factory: Mock) -> None:
        session = factory.return_value
        session.get.return_value = response(status_code=404)

        output = ncbi_pmc.execute({"params": {"id": "PMC3257301.1"}})

        self.assertTrue(output["ok"], output)
        self.assertEqual(output["records"], [])
        self.assertEqual(output["warnings"], ["No PMC Cloud metadata was found for PMC3257301.1."])
        session.get.return_value.raise_for_status.assert_not_called()
        factory.assert_called_once_with()
        session.close.assert_called_once_with()

    @patch("ncbi_pmc.requests.Session")
    def test_closes_session_when_version_listing_is_invalid(self, factory: Mock) -> None:
        session = factory.return_value
        session.get.return_value = response(text="<invalid")

        output = ncbi_pmc.execute({"params": {"id": "PMC3257301"}})

        self.assertFalse(output["ok"])
        self.assertEqual(output["error"]["code"], "invalid_response")
        factory.assert_called_once_with()
        session.close.assert_called_once_with()

    @patch("ncbi_pmc.requests.Session")
    def test_invalid_input_does_not_create_session(self, factory: Mock) -> None:
        with self.assertRaisesRegex(ValueError, "`params.id` is required"):
            ncbi_pmc.execute({"params": {}})

        factory.assert_not_called()

    @patch.dict("ncbi_pmc.os.environ", {"NCBI_API_KEY": "top-secret"}, clear=False)
    @patch("ncbi_pmc.requests.Session")
    def test_http_errors_do_not_expose_ncbi_api_key(self, factory: Mock) -> None:
        session = factory.return_value
        failed_response = Mock(status_code=429)
        failure = ncbi_pmc.requests.HTTPError(
            "429 for https://eutils.ncbi.nlm.nih.gov/?api_key=top-secret",
            response=failed_response,
        )
        session.get.return_value.raise_for_status.side_effect = failure

        output = ncbi_pmc.execute({"params": {"id": "10.1000/example"}})

        self.assertFalse(output["ok"])
        self.assertEqual(output["error"]["message"], "PMC identifier lookup returned HTTP 429.")
        self.assertEqual(session.get.call_args.kwargs["params"]["api_key"], "top-secret")
        self.assertNotIn("top-secret", json.dumps(output))
        factory.assert_called_once_with()
        session.close.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
