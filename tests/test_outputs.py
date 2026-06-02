import unittest

from pbdb_mcp.outputs import bibliography_pack, pack_validation_report, research_summary_markdown


def sample_pack():
    return {
        "generated_at": "2026-06-02T00:00:00+00:00",
        "input": {"name": "Tyrannosaurus"},
        "manifest": {
            "workflow": "taxon_fact_card",
            "pbdb_base_url": "https://paleobiodb.org/data1.2/",
        },
        "summary": {
            "age_range_ma_from_occurrences": {"max_ma": 72.2, "min_ma": 66.0},
            "reference_count_sample": 1,
        },
        "evidence": {
            "references": {
                "query": {
                    "name": "occs_refs",
                    "url": "https://paleobiodb.org/data1.2/occs/refs.json?base_name=Tyrannosaurus&limit=1",
                    "endpoint": "occs/refs.json",
                    "params": {"base_name": "Tyrannosaurus", "limit": "1"},
                    "record_count": 1,
                },
                "records": [
                    {
                        "oid": "ref:4205",
                        "atr": "Russell",
                        "pby": "1970",
                        "tit": "Tyrannosaurs from the Late Cretaceous of western Canada",
                        "pbt": "National Museum of Natural Sciences, Publications in Paleontology",
                    }
                ],
            }
        },
        "research_notes": ["Use PBDB query URLs for reproducibility."],
    }


class OutputsTest(unittest.TestCase):
    def test_bibliography_pack_extracts_reference_metadata(self):
        bibliography = bibliography_pack(sample_pack())

        self.assertEqual(bibliography["reference_count"], 1)
        self.assertEqual(bibliography["references"][0]["ref_id"], "ref:4205")
        self.assertEqual(bibliography["references"][0]["year"], "1970")

    def test_pack_validation_report_accepts_reproducible_pack(self):
        report = pack_validation_report(sample_pack())

        self.assertEqual(report["overall"], "valid")
        self.assertEqual(report["metrics"]["query_count"], 1)
        self.assertTrue(report["metrics"]["has_manifest"])

    def test_pack_validation_report_flags_missing_query_urls(self):
        report = pack_validation_report({"summary": {}})

        codes = {flag["code"] for flag in report["flags"]}
        self.assertEqual(report["overall"], "invalid")
        self.assertIn("missing_query_urls", codes)
        self.assertIn("missing_evidence", codes)

    def test_research_summary_markdown_renders_sections(self):
        markdown = research_summary_markdown(sample_pack(), title="Test Summary")

        self.assertIn("# Test Summary", markdown)
        self.assertIn("## References", markdown)
        self.assertIn("ref:4205", markdown)
        self.assertIn("## Reproducible Queries", markdown)


if __name__ == "__main__":
    unittest.main()
