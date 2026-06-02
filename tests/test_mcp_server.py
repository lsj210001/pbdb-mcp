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
                "taxon_fact_card",
                "reference_evidence_pack",
                "taxonomy_dispute_report",
                "taxa_compare_pack",
                "interval_context_pack",
                "locality_context_pack",
                "evidence_quality_report",
                "bibliography_pack",
                "pack_validation_report",
                "research_summary_markdown",
            },
        )

    def test_tool_schema_is_json_serializable(self):
        json.dumps(_tool_schema())


if __name__ == "__main__":
    unittest.main()
