import unittest
from unittest.mock import patch

from pbdb_mcp.client import PBDBResponse
from pbdb_mcp.research import (
    evidence_quality_report,
    interval_context_pack,
    locality_context_pack,
    reference_evidence_pack,
    taxa_compare_pack,
    taxon_fact_card,
    taxonomy_dispute_report,
)


def response(name, records):
    return PBDBResponse(
        url=f"https://example.test/{name}",
        content_type="application/json",
        status=200,
        body={"records": records},
        raw_text="",
    )


class ResearchTest(unittest.TestCase):
    @patch("pbdb_mcp.research.geo_summary")
    @patch("pbdb_mcp.research.occs_strata_summary")
    @patch("pbdb_mcp.research.occs_refs")
    @patch("pbdb_mcp.research.specimens_search")
    @patch("pbdb_mcp.research.collections_search")
    @patch("pbdb_mcp.research.occurrences_search")
    @patch("pbdb_mcp.research.taxa_opinions")
    @patch("pbdb_mcp.research.taxa_search")
    @patch("pbdb_mcp.research.taxon_lookup")
    def test_taxon_fact_card_contains_summary_and_query_urls(self, *mocks):
        (
            taxon_lookup_mock,
            taxa_search_mock,
            taxa_opinions_mock,
            occurrences_search_mock,
            collections_search_mock,
            specimens_search_mock,
            occs_refs_mock,
            occs_strata_summary_mock,
            geo_summary_mock,
        ) = mocks
        taxon_lookup_mock.return_value = response("taxon", [{"nam": "Tyrannosaurus", "rid": "ref:9259"}])
        taxa_search_mock.return_value = response("taxa", [{"nam": "Tyrannosaurus"}])
        taxa_opinions_mock.return_value = response("opinions", [{"sta": "belongs to", "rid": "ref:1"}])
        occurrences_search_mock.return_value = response("occs", [{"eag": 72.2, "lag": 66, "oei": "Late Maastrichtian", "rid": "ref:2"}])
        collections_search_mock.return_value = response("colls", [{"cc2": "CA", "rid": "ref:3"}])
        specimens_search_mock.return_value = response("specs", [{"oid": "spm:1", "smp": "femur"}])
        occs_refs_mock.return_value = response("refs", [{"oid": "ref:4205", "tit": "Reference"}])
        occs_strata_summary_mock.return_value = response("strata", [{"sfm": "Hell Creek"}])
        geo_summary_mock.return_value = response("geo", [{"oid": "clu:1"}])

        card = taxon_fact_card(name="Tyrannosaurus", limit=1)

        self.assertEqual(card["input"]["name"], "Tyrannosaurus")
        self.assertEqual(card["summary"]["age_range_ma_from_occurrences"], {"max_ma": 72.2, "min_ma": 66.0})
        self.assertEqual(card["summary"]["countries_from_collections"], ["CA"])
        self.assertEqual(card["summary"]["reference_ids"], ["ref:4205"])
        self.assertEqual(card["evidence"]["taxon"]["query"]["url"], "https://example.test/taxon")
        self.assertEqual(card["manifest"]["workflow"], "taxon_fact_card")
        self.assertEqual(card["manifest"]["version"], "0.5.0")

    @patch("pbdb_mcp.research.associated_by_reference")
    @patch("pbdb_mcp.research.references_search")
    def test_reference_evidence_pack_groups_associated_records(self, references_mock, associated_mock):
        references_mock.return_value = response("ref", [{"oid": "ref:4205"}])
        associated_mock.return_value = response(
            "associated",
            [{"oid": "txn:1"}, {"oid": "opn:1"}, {"oid": "col:1"}],
        )

        pack = reference_evidence_pack(ref_id=4205)

        self.assertEqual(len(pack["summary"]["associated_taxa"]), 1)
        self.assertEqual(len(pack["summary"]["associated_opinions"]), 1)
        self.assertEqual(len(pack["summary"]["associated_collections"]), 1)
        self.assertEqual(pack["manifest"]["workflow"], "reference_evidence_pack")

    @patch("pbdb_mcp.research.references_search")
    @patch("pbdb_mcp.research.taxa_opinions")
    @patch("pbdb_mcp.research.taxon_lookup")
    def test_taxonomy_dispute_report_collects_opinion_metadata(self, taxon_mock, opinions_mock, references_mock):
        taxon_mock.return_value = response("taxon", [{"nam": "Tyrannosaurus"}])
        opinions_mock.return_value = response(
            "opinions",
            [{"sta": "belongs to", "prl": "Tyrannosaurini", "oat": "Author", "opy": "2024", "rid": "ref:9"}],
        )
        references_mock.return_value = response("ref", [{"oid": "ref:9"}])

        report = taxonomy_dispute_report(name="Tyrannosaurus")

        self.assertEqual(report["summary"]["statuses"], ["belongs to"])
        self.assertEqual(report["summary"]["parent_taxa_named_in_opinions"], ["Tyrannosaurini"])
        self.assertEqual(report["summary"]["reference_ids"], ["ref:9"])
        self.assertEqual(report["manifest"]["workflow"], "taxonomy_dispute_report")

    @patch("pbdb_mcp.research.taxon_fact_card")
    def test_taxa_compare_pack_builds_rows_and_quality_flags(self, fact_card_mock):
        def card(name, limit, geo_level, timeout):
            return {
                "input": {"name": name},
                "summary": {
                    "accepted_or_matching_taxon": [{"nam": name}],
                    "age_range_ma_from_occurrences": {"max_ma": 72.0, "min_ma": 66.0},
                    "occurrence_count_sample": 1,
                    "collection_count_sample": 1,
                    "reference_count_sample": 1,
                    "opinion_count": 0,
                    "countries_from_collections": ["US"],
                    "reference_ids": ["ref:1"],
                },
                "evidence": {
                    "taxonomic_opinions": {"records": []},
                    "occurrences": {"records": [{"eag": 72, "lag": 66}]},
                    "collections": {"records": [{"cc2": "US"}]},
                    "references": {"records": [{"oid": "ref:1"}]},
                },
            }

        fact_card_mock.side_effect = card

        pack = taxa_compare_pack(names=["Tyrannosaurus", "Triceratops"], limit=1)

        rows = pack["summary"]["comparison_rows"]
        self.assertEqual([row["input_name"] for row in rows], ["Tyrannosaurus", "Triceratops"])
        self.assertEqual(rows[0]["quality_overall"], "needs_review")
        self.assertEqual(pack["evidence"]["taxon_fact_cards"][0]["input"]["name"], "Tyrannosaurus")
        self.assertEqual(pack["manifest"]["workflow"], "taxa_compare_pack")

    @patch("pbdb_mcp.research.geo_summary")
    @patch("pbdb_mcp.research.occs_strata_summary")
    @patch("pbdb_mcp.research.occs_refs")
    @patch("pbdb_mcp.research.collections_search")
    @patch("pbdb_mcp.research.occs_taxa_summary")
    @patch("pbdb_mcp.research.occurrences_search")
    def test_interval_context_pack_summarizes_interval(self, occs_mock, taxa_mock, collections_mock, refs_mock, strata_mock, geo_mock):
        occs_mock.return_value = response("occs", [{"eag": 72, "lag": 66, "lat": 1, "lng": 2}])
        taxa_mock.return_value = response("taxa", [{"nam": "Dinosauria"}])
        collections_mock.return_value = response("colls", [{"cc2": "US"}])
        refs_mock.return_value = response("refs", [{"oid": "ref:1"}])
        strata_mock.return_value = response("strata", [{"sfm": "Hell Creek"}])
        geo_mock.return_value = response("geo", [{"oid": "clu:1"}])

        pack = interval_context_pack(interval="Late Cretaceous", limit=1)

        self.assertEqual(pack["input"]["interval"], "Late Cretaceous")
        self.assertEqual(pack["summary"]["taxa_count_sample"], 1)
        self.assertEqual(pack["summary"]["strata_or_lithologies"], ["Hell Creek"])
        self.assertEqual(pack["evidence"]["geography"]["query"]["url"], "https://example.test/geo")
        self.assertEqual(pack["manifest"]["workflow"], "interval_context_pack")

    @patch("pbdb_mcp.research.strata_search")
    @patch("pbdb_mcp.research.geo_summary")
    @patch("pbdb_mcp.research.occs_refs")
    @patch("pbdb_mcp.research.collections_search")
    @patch("pbdb_mcp.research.occs_taxa_summary")
    @patch("pbdb_mcp.research.occurrences_search")
    def test_locality_context_pack_includes_strata_lookup(self, occs_mock, taxa_mock, collections_mock, refs_mock, geo_mock, strata_mock):
        occs_mock.return_value = response("occs", [{"eag": 72, "lag": 66}])
        taxa_mock.return_value = response("taxa", [{"nam": "Tyrannosaurus"}])
        collections_mock.return_value = response("colls", [{"nam": "Collection 1"}])
        refs_mock.return_value = response("refs", [{"oid": "ref:1"}])
        geo_mock.return_value = response("geo", [{"oid": "clu:1"}])
        strata_mock.return_value = response("strata", [{"nam": "Hell Creek Formation"}])

        pack = locality_context_pack(country="US", stratum_name="Hell Creek", limit=1)

        self.assertEqual(pack["input"]["country"], "US")
        self.assertEqual(pack["summary"]["strata_matches"][0]["nam"], "Hell Creek Formation")
        self.assertIn("strata", pack["evidence"])
        self.assertEqual(pack["manifest"]["workflow"], "locality_context_pack")

    @patch("pbdb_mcp.research.taxa_opinions")
    @patch("pbdb_mcp.research.occs_refs")
    @patch("pbdb_mcp.research.collections_search")
    @patch("pbdb_mcp.research.occurrences_search")
    def test_evidence_quality_report_flags_limited_samples(self, occs_mock, collections_mock, refs_mock, opinions_mock):
        occs_mock.return_value = response("occs", [{"eag": 100, "lag": 70}])
        collections_mock.return_value = response("colls", [])
        refs_mock.return_value = response("refs", [{"oid": "ref:1"}])
        opinions_mock.return_value = response("opinions", [{"sta": "belongs to"}])

        report = evidence_quality_report(name="Example", limit=1)

        codes = {flag["code"] for flag in report["summary"]["flags"]}
        self.assertIn("low_occurrence_sample", codes)
        self.assertIn("no_collection_sample", codes)
        self.assertIn("broad_age_range", codes)
        self.assertEqual(report["evidence"]["occurrences"]["query"]["url"], "https://example.test/occs")
        self.assertEqual(report["manifest"]["workflow"], "evidence_quality_report")


if __name__ == "__main__":
    unittest.main()
