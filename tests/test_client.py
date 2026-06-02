import json
import unittest
from unittest.mock import patch

from pbdb_mcp.client import (
    PBDBResponse,
    associated_by_reference,
    build_url,
    combined_auto,
    occs_refs,
    pretty_result,
    references_search,
    specimens_search,
    strata_search,
    taxa_opinions,
    taxa_search,
)


class FakeResponse:
    status = 200
    headers = None

    def __init__(self, payload: dict):
        self._payload = payload
        self.headers = self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return json.dumps(self._payload).encode("utf-8")

    def get_content_type(self):
        return "application/json"

    def get_content_charset(self):
        return "utf-8"


class ClientTest(unittest.TestCase):
    def test_build_url_encodes_parameters(self):
        url = build_url("occs/list.json", {"base_name": "Tyrannosaurus rex", "show": ["coords", "attr"], "limit": 1})
        self.assertEqual(
            url,
            "https://paleobiodb.org/data1.2/occs/list.json?base_name=Tyrannosaurus+rex&show=coords%2Cattr&limit=1",
        )

    def test_references_search_uses_ref_id(self):
        seen_urls = []

        def fake_urlopen(request, timeout):
            seen_urls.append(request.full_url)
            return FakeResponse({"records": [{"oid": "ref:4205"}]})

        with patch("pbdb_mcp.client.urlopen", fake_urlopen):
            result = references_search(ref_id=4205, limit=1)

        self.assertIn("ref_id=4205", seen_urls[0])
        self.assertIn("limit=1", seen_urls[0])
        self.assertEqual(result.body["records"][0]["oid"], "ref:4205")

    def test_taxa_search_uses_taxa_list_path(self):
        seen_urls = []

        def fake_urlopen(request, timeout):
            seen_urls.append(request.full_url)
            return FakeResponse({"records": [{"oid": "txn:38613"}]})

        with patch("pbdb_mcp.client.urlopen", fake_urlopen):
            taxa_search(base_name="Tyrannosaurus", limit=3)

        self.assertIn("/taxa/list.json?", seen_urls[0])
        self.assertIn("base_name=Tyrannosaurus", seen_urls[0])

    def test_taxa_opinions_uses_taxa_opinions_path(self):
        seen_urls = []

        def fake_urlopen(request, timeout):
            seen_urls.append(request.full_url)
            return FakeResponse({"records": [{"oid": "opn:1"}]})

        with patch("pbdb_mcp.client.urlopen", fake_urlopen):
            taxa_opinions(base_name="Tyrannosaurus", limit=3)

        self.assertIn("/taxa/opinions.json?", seen_urls[0])

    def test_occurrence_references_use_occs_refs_path(self):
        seen_urls = []

        def fake_urlopen(request, timeout):
            seen_urls.append(request.full_url)
            return FakeResponse({"records": [{"oid": "ref:1"}]})

        with patch("pbdb_mcp.client.urlopen", fake_urlopen):
            occs_refs(base_name="Tyrannosaurus", limit=3)

        self.assertIn("/occs/refs.json?", seen_urls[0])

    def test_specimens_search_uses_specs_list_path(self):
        seen_urls = []

        def fake_urlopen(request, timeout):
            seen_urls.append(request.full_url)
            return FakeResponse({"records": [{"oid": "spm:1"}]})

        with patch("pbdb_mcp.client.urlopen", fake_urlopen):
            specimens_search(base_name="Tyrannosaurus", limit=3)

        self.assertIn("/specs/list.json?", seen_urls[0])

    def test_strata_search_rejects_interval_parameter(self):
        with self.assertRaises(ValueError):
            strata_search(interval="Late Cretaceous")

    def test_combined_helpers_use_expected_paths(self):
        seen_urls = []

        def fake_urlopen(request, timeout):
            seen_urls.append(request.full_url)
            return FakeResponse({"records": []})

        with patch("pbdb_mcp.client.urlopen", fake_urlopen):
            combined_auto(name="Tyranno", limit=3)
            associated_by_reference(ref_id=4205, record_type="all")

        self.assertIn("/combined/auto.json?", seen_urls[0])
        self.assertIn("/combined/associated.json?", seen_urls[1])
        self.assertIn("ref_id=4205", seen_urls[1])

    def test_pretty_result_formats_json(self):
        text = pretty_result(
            PBDBResponse(
                url="https://example.test",
                content_type="application/json",
                status=200,
                body={"records": [{"nam": "Tyrannosaurus"}]},
                raw_text="",
            )
        )
        self.assertIn('"Tyrannosaurus"', text)


if __name__ == "__main__":
    unittest.main()
