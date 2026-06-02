from __future__ import annotations

import argparse
import json
import sys

try:
    from .client import (
        collections_search,
        associated_by_reference,
        combined_auto,
        geo_summary,
        intervals_search,
        occs_refs,
        occs_strata_summary,
        occs_taxa_summary,
        opinions_search,
        occurrences_search,
        pretty_result,
        references_search,
        request,
        strata_search,
        specimens_search,
        taxa_opinions,
        taxa_search,
        taxon_lookup,
    )
    from .outputs import bibliography_pack, pack_validation_report, research_summary_markdown
    from .research import (
        evidence_quality_report,
        interval_context_pack,
        locality_context_pack,
        reference_evidence_pack,
        taxa_compare_pack,
        taxon_fact_card,
        taxonomy_dispute_report,
    )
except ImportError:
    from client import (  # type: ignore[no-redef]
        collections_search,
        associated_by_reference,
        combined_auto,
        geo_summary,
        intervals_search,
        occs_refs,
        occs_strata_summary,
        occs_taxa_summary,
        opinions_search,
        occurrences_search,
        pretty_result,
        references_search,
        request,
        strata_search,
        specimens_search,
        taxa_opinions,
        taxa_search,
        taxon_lookup,
    )
    from outputs import bibliography_pack, pack_validation_report, research_summary_markdown  # type: ignore[no-redef]
    from research import (  # type: ignore[no-redef]
        evidence_quality_report,
        interval_context_pack,
        locality_context_pack,
        reference_evidence_pack,
        taxa_compare_pack,
        taxon_fact_card,
        taxonomy_dispute_report,
    )


def parse_param_pairs(values: list[str]) -> dict[str, str]:
    params: dict[str, str] = {}
    for item in values:
        if "=" not in item:
            raise SystemExit(f"Invalid --param value: {item!r}. Use key=value.")
        key, value = item.split("=", 1)
        params[key] = value
    return params


def add_common_timeout(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--timeout", type=int, default=30)


def load_json_input(path: str) -> dict:
    if path == "-":
        payload = json.load(sys.stdin)
    else:
        with open(path, "r", encoding="utf-8") as file:
            payload = json.load(file)
    if not isinstance(payload, dict):
        raise SystemExit("Input JSON must be an object.")
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pbdb")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("request", help="Call an arbitrary PBDB API path")
    p.add_argument("path")
    p.add_argument("--param", action="append", default=[], help="Query parameter as key=value")
    add_common_timeout(p)

    p = sub.add_parser("taxon", help="Lookup a taxon by name or taxon_no")
    p.add_argument("--name")
    p.add_argument("--taxon-no")
    p.add_argument("--show")
    add_common_timeout(p)

    p = sub.add_parser("taxa", help="Search taxonomic names")
    p.add_argument("--base-name")
    p.add_argument("--taxon-name")
    p.add_argument("--taxon-id")
    p.add_argument("--rank")
    p.add_argument("--limit", type=int, default=50)
    p.add_argument("--show", default="attr")
    add_common_timeout(p)

    p = sub.add_parser("taxa-opinions", help="Search opinions attached to a taxon")
    p.add_argument("--base-name")
    p.add_argument("--taxon-name")
    p.add_argument("--taxon-id")
    p.add_argument("--limit", type=int, default=50)
    p.add_argument("--show")
    add_common_timeout(p)

    p = sub.add_parser("opinions", help="Search taxonomic opinions")
    p.add_argument("--opinion-id")
    p.add_argument("--author")
    p.add_argument("--pubyr")
    p.add_argument("--created-since")
    p.add_argument("--modified-since")
    p.add_argument("--limit", type=int, default=50)
    p.add_argument("--show")
    add_common_timeout(p)

    p = sub.add_parser("occurrences", help="Search occurrences")
    p.add_argument("--base-name")
    p.add_argument("--taxon-name")
    p.add_argument("--interval")
    p.add_argument("--country")
    p.add_argument("--state")
    p.add_argument("--limit", type=int, default=50)
    p.add_argument("--show", default="coords,attr")
    add_common_timeout(p)

    p = sub.add_parser("occs-taxa", help="Summarize taxa from selected occurrences")
    p.add_argument("--base-name")
    p.add_argument("--taxon-name")
    p.add_argument("--interval")
    p.add_argument("--country")
    p.add_argument("--state")
    p.add_argument("--rank")
    p.add_argument("--limit", type=int, default=50)
    p.add_argument("--show", default="attr")
    add_common_timeout(p)

    p = sub.add_parser("occs-refs", help="Search references associated with selected occurrences")
    p.add_argument("--base-name")
    p.add_argument("--taxon-name")
    p.add_argument("--interval")
    p.add_argument("--country")
    p.add_argument("--state")
    p.add_argument("--limit", type=int, default=50)
    p.add_argument("--show", default="attr")
    add_common_timeout(p)

    p = sub.add_parser("occs-strata", help="Summarize strata from selected occurrences")
    p.add_argument("--base-name")
    p.add_argument("--taxon-name")
    p.add_argument("--interval")
    p.add_argument("--country")
    p.add_argument("--state")
    p.add_argument("--limit", type=int, default=50)
    add_common_timeout(p)

    p = sub.add_parser("geo-summary", help="Geographic summary for occurrences or collections")
    p.add_argument("--record-type", choices=["occs", "colls"], default="occs")
    p.add_argument("--level", type=int, default=2)
    p.add_argument("--base-name")
    p.add_argument("--taxon-name")
    p.add_argument("--interval")
    p.add_argument("--country")
    p.add_argument("--state")
    add_common_timeout(p)

    p = sub.add_parser("collections", help="Search collections")
    p.add_argument("--base-name")
    p.add_argument("--taxon-name")
    p.add_argument("--interval")
    p.add_argument("--country")
    p.add_argument("--state")
    p.add_argument("--limit", type=int, default=50)
    p.add_argument("--show", default="loc,time,strat,ref")
    add_common_timeout(p)

    p = sub.add_parser("specimens", help="Search fossil specimens")
    p.add_argument("--base-name")
    p.add_argument("--taxon-name")
    p.add_argument("--interval")
    p.add_argument("--country")
    p.add_argument("--state")
    p.add_argument("--limit", type=int, default=50)
    p.add_argument("--show")
    add_common_timeout(p)

    p = sub.add_parser("references", help="Search references")
    p.add_argument("--ref-id")
    p.add_argument("--ref-match")
    p.add_argument("--ref-author")
    p.add_argument("--ref-title")
    p.add_argument("--ref-doi")
    p.add_argument("--pub-title")
    p.add_argument("--all-records", action="store_true")
    p.add_argument("--limit", type=int, default=50)
    p.add_argument("--show", default="attr")
    add_common_timeout(p)

    p = sub.add_parser("intervals", help="Search intervals")
    p.add_argument("--name")
    p.add_argument("--limit", type=int, default=50)
    add_common_timeout(p)

    p = sub.add_parser("strata", help="Search strata")
    p.add_argument("--name")
    p.add_argument("--limit", type=int, default=50)
    add_common_timeout(p)

    p = sub.add_parser("auto", help="Autocomplete names across PBDB record types")
    p.add_argument("--name", required=True)
    p.add_argument("--record-type")
    p.add_argument("--limit", type=int, default=10)
    add_common_timeout(p)

    p = sub.add_parser("associated", help="List records associated with a reference")
    p.add_argument("--ref-id", required=True)
    p.add_argument("--record-type", choices=["txn", "opn", "col", "all"], default="all")
    p.add_argument("--show")
    add_common_timeout(p)

    p = sub.add_parser("fact-card", help="Build a multi-query taxon fact card")
    p.add_argument("--name", required=True)
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--geo-level", type=int, default=2)
    add_common_timeout(p)

    p = sub.add_parser("reference-pack", help="Build an evidence pack for a PBDB reference")
    p.add_argument("--ref-id", required=True)
    p.add_argument("--record-type", choices=["txn", "opn", "col", "all"], default="all")
    add_common_timeout(p)

    p = sub.add_parser("dispute-report", help="Build a taxonomic opinion/dispute report")
    p.add_argument("--name", required=True)
    p.add_argument("--limit", type=int, default=25)
    add_common_timeout(p)

    p = sub.add_parser("compare-pack", help="Build a comparative evidence pack for 2-5 taxa")
    p.add_argument("--name", action="append", required=True, help="Taxon name. Repeat 2-5 times.")
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--geo-level", type=int, default=2)
    add_common_timeout(p)

    p = sub.add_parser("interval-pack", help="Build a geological interval context pack")
    p.add_argument("--interval", required=True)
    p.add_argument("--limit", type=int, default=25)
    p.add_argument("--geo-level", type=int, default=2)
    add_common_timeout(p)

    p = sub.add_parser("locality-pack", help="Build a locality, region, or stratum context pack")
    p.add_argument("--country")
    p.add_argument("--state")
    p.add_argument("--interval")
    p.add_argument("--base-name")
    p.add_argument("--stratum-name")
    p.add_argument("--limit", type=int, default=25)
    p.add_argument("--geo-level", type=int, default=2)
    add_common_timeout(p)

    p = sub.add_parser("quality-report", help="Build an evidence quality report for a PBDB query scope")
    p.add_argument("--name")
    p.add_argument("--interval")
    p.add_argument("--country")
    p.add_argument("--state")
    p.add_argument("--limit", type=int, default=25)
    add_common_timeout(p)

    p = sub.add_parser("bibliography", help="Extract a bibliography from an evidence pack JSON file")
    p.add_argument("--input", default="-", help="Evidence pack JSON file, or - for stdin")
    p.add_argument("--limit", type=int, default=100)

    p = sub.add_parser("validate-pack", help="Validate reproducibility metadata in an evidence pack JSON file")
    p.add_argument("--input", default="-", help="Evidence pack JSON file, or - for stdin")

    p = sub.add_parser("markdown-summary", help="Render a generic Markdown research summary from an evidence pack JSON file")
    p.add_argument("--input", default="-", help="Evidence pack JSON file, or - for stdin")
    p.add_argument("--title")
    p.add_argument("--max-references", type=int, default=10)
    p.add_argument("--max-queries", type=int, default=20)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "request":
        result = request(args.path, parse_param_pairs(args.param), timeout=args.timeout)
    elif args.command == "taxon":
        result = taxon_lookup(name=args.name, taxon_no=args.taxon_no, show=args.show, timeout=args.timeout)
    elif args.command == "taxa":
        result = taxa_search(
            base_name=args.base_name,
            taxon_name=args.taxon_name,
            taxon_id=args.taxon_id,
            rank=args.rank,
            limit=args.limit,
            show=args.show,
            timeout=args.timeout,
        )
    elif args.command == "taxa-opinions":
        result = taxa_opinions(
            base_name=args.base_name,
            taxon_name=args.taxon_name,
            taxon_id=args.taxon_id,
            limit=args.limit,
            show=args.show,
            timeout=args.timeout,
        )
    elif args.command == "opinions":
        result = opinions_search(
            opinion_id=args.opinion_id,
            author=args.author,
            pubyr=args.pubyr,
            created_since=args.created_since,
            modified_since=args.modified_since,
            limit=args.limit,
            show=args.show,
            timeout=args.timeout,
        )
    elif args.command == "occurrences":
        result = occurrences_search(
            base_name=args.base_name,
            taxon_name=args.taxon_name,
            interval=args.interval,
            country=args.country,
            state=args.state,
            limit=args.limit,
            show=args.show,
            timeout=args.timeout,
        )
    elif args.command == "occs-taxa":
        result = occs_taxa_summary(
            base_name=args.base_name,
            taxon_name=args.taxon_name,
            interval=args.interval,
            country=args.country,
            state=args.state,
            rank=args.rank,
            limit=args.limit,
            show=args.show,
            timeout=args.timeout,
        )
    elif args.command == "occs-refs":
        result = occs_refs(
            base_name=args.base_name,
            taxon_name=args.taxon_name,
            interval=args.interval,
            country=args.country,
            state=args.state,
            limit=args.limit,
            show=args.show,
            timeout=args.timeout,
        )
    elif args.command == "occs-strata":
        result = occs_strata_summary(
            base_name=args.base_name,
            taxon_name=args.taxon_name,
            interval=args.interval,
            country=args.country,
            state=args.state,
            limit=args.limit,
            timeout=args.timeout,
        )
    elif args.command == "geo-summary":
        result = geo_summary(
            record_type=args.record_type,
            level=args.level,
            base_name=args.base_name,
            taxon_name=args.taxon_name,
            interval=args.interval,
            country=args.country,
            state=args.state,
            timeout=args.timeout,
        )
    elif args.command == "collections":
        result = collections_search(
            base_name=args.base_name,
            taxon_name=args.taxon_name,
            interval=args.interval,
            country=args.country,
            state=args.state,
            limit=args.limit,
            show=args.show,
            timeout=args.timeout,
        )
    elif args.command == "specimens":
        result = specimens_search(
            base_name=args.base_name,
            taxon_name=args.taxon_name,
            interval=args.interval,
            country=args.country,
            state=args.state,
            limit=args.limit,
            show=args.show,
            timeout=args.timeout,
        )
    elif args.command == "references":
        result = references_search(
            ref_id=args.ref_id,
            ref_match=args.ref_match,
            ref_author=args.ref_author,
            ref_title=args.ref_title,
            ref_doi=args.ref_doi,
            pub_title=args.pub_title,
            all_records=args.all_records or None,
            limit=args.limit,
            show=args.show,
            timeout=args.timeout,
        )
    elif args.command == "intervals":
        result = intervals_search(name=args.name, limit=args.limit, timeout=args.timeout)
    elif args.command == "strata":
        result = strata_search(name=args.name, limit=args.limit, timeout=args.timeout)
    elif args.command == "auto":
        result = combined_auto(name=args.name, record_type=args.record_type, limit=args.limit, timeout=args.timeout)
    elif args.command == "associated":
        result = associated_by_reference(ref_id=args.ref_id, record_type=args.record_type, show=args.show, timeout=args.timeout)
    elif args.command == "fact-card":
        result = taxon_fact_card(name=args.name, limit=args.limit, geo_level=args.geo_level, timeout=args.timeout)
        sys.stdout.write(json.dumps(result, ensure_ascii=False, indent=2))
        sys.stdout.write("\n")
        return 0
    elif args.command == "reference-pack":
        result = reference_evidence_pack(ref_id=args.ref_id, record_type=args.record_type, timeout=args.timeout)
        sys.stdout.write(json.dumps(result, ensure_ascii=False, indent=2))
        sys.stdout.write("\n")
        return 0
    elif args.command == "dispute-report":
        result = taxonomy_dispute_report(name=args.name, limit=args.limit, timeout=args.timeout)
        sys.stdout.write(json.dumps(result, ensure_ascii=False, indent=2))
        sys.stdout.write("\n")
        return 0
    elif args.command == "compare-pack":
        result = taxa_compare_pack(names=args.name, limit=args.limit, geo_level=args.geo_level, timeout=args.timeout)
        sys.stdout.write(json.dumps(result, ensure_ascii=False, indent=2))
        sys.stdout.write("\n")
        return 0
    elif args.command == "interval-pack":
        result = interval_context_pack(interval=args.interval, limit=args.limit, geo_level=args.geo_level, timeout=args.timeout)
        sys.stdout.write(json.dumps(result, ensure_ascii=False, indent=2))
        sys.stdout.write("\n")
        return 0
    elif args.command == "locality-pack":
        result = locality_context_pack(
            country=args.country,
            state=args.state,
            interval=args.interval,
            base_name=args.base_name,
            stratum_name=args.stratum_name,
            limit=args.limit,
            geo_level=args.geo_level,
            timeout=args.timeout,
        )
        sys.stdout.write(json.dumps(result, ensure_ascii=False, indent=2))
        sys.stdout.write("\n")
        return 0
    elif args.command == "quality-report":
        result = evidence_quality_report(
            name=args.name,
            interval=args.interval,
            country=args.country,
            state=args.state,
            limit=args.limit,
            timeout=args.timeout,
        )
        sys.stdout.write(json.dumps(result, ensure_ascii=False, indent=2))
        sys.stdout.write("\n")
        return 0
    elif args.command == "bibliography":
        result = bibliography_pack(load_json_input(args.input), limit=args.limit)
        sys.stdout.write(json.dumps(result, ensure_ascii=False, indent=2))
        sys.stdout.write("\n")
        return 0
    elif args.command == "validate-pack":
        result = pack_validation_report(load_json_input(args.input))
        sys.stdout.write(json.dumps(result, ensure_ascii=False, indent=2))
        sys.stdout.write("\n")
        return 0
    elif args.command == "markdown-summary":
        sys.stdout.write(
            research_summary_markdown(
                load_json_input(args.input),
                title=args.title,
                max_references=args.max_references,
                max_queries=args.max_queries,
            )
        )
        return 0
    else:
        raise AssertionError(args.command)

    pretty = pretty_result(result)
    sys.stdout.write(pretty)
    if not pretty.endswith("\n"):
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
