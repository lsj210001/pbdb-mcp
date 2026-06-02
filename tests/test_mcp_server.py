import json
import unittest

from pbdb_mcp.server import _tool_schema


class MCPServerTest(unittest.TestCase):
    def test_tool_schema_contains_expected_tools(self):
        names = {tool["name"] for tool in _tool_schema()}
        self.assertEqual(
            names,
            {
                "pbdb_request",
                "taxon_lookup",
                "occurrences_search",
                "collections_search",
                "references_search",
                "intervals_search",
                "strata_search",
            },
        )

    def test_tool_schema_is_json_serializable(self):
        json.dumps(_tool_schema())


if __name__ == "__main__":
    unittest.main()
