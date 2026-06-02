import unittest
from unittest.mock import patch

from pbdb_mcp.client import PBDBResponse
from pbdb_mcp.research import reference_evidence_pack, taxon_fact_card, taxonomy_dispute_report


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


if __name__ == "__main__":
    unittest.main()
