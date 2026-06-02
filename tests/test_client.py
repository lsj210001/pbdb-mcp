import json
import unittest
from unittest.mock import patch

from pbdb_mcp.client import PBDBResponse, build_url, pretty_result, references_search


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
