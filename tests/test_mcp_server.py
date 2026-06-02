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
                "taxa_search",
                "taxa_opinions",
                "opinions_search",
                "occurrences_search",
                "occs_taxa_summary",
                "occs_refs",
                "occs_strata_summary",
                "geo_summary",
                "collections_search",
                "specimens_search",
                "references_search",
                "intervals_search",
                "strata_search",
                "combined_auto",
                "associated_by_reference",
            },
        )

    def test_tool_schema_is_json_serializable(self):
        json.dumps(_tool_schema())


if __name__ == "__main__":
    unittest.main()
