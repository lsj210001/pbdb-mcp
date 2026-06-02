import json
import os
import unittest
from unittest.mock import patch

from pbdb_mcp.server import _tool_schema


class MCPServerTest(unittest.TestCase):
    def test_default_tool_schema_contains_compact_tools(self):
        with patch.dict(os.environ, {}, clear=True):
            names = {tool["name"] for tool in _tool_schema()}
        self.assertEqual(
            names,
            {
                "pbdb_request",
                "taxon_tool",
                "occurrence_tool",
                "collection_tool",
                "specimen_tool",
                "reference_tool",
                "taxonomy_tool",
                "geology_tool",
                "context_pack",
                "pack_output_tool",
            },
        )

    def test_full_tool_schema_contains_legacy_tools(self):
        with patch.dict(os.environ, {"PBDB_MCP_TOOL_MODE": "full"}):
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
        with patch.dict(os.environ, {}, clear=True):
            json.dumps(_tool_schema())
        with patch.dict(os.environ, {"PBDB_MCP_TOOL_MODE": "full"}):
            json.dumps(_tool_schema())


if __name__ == "__main__":
    unittest.main()
