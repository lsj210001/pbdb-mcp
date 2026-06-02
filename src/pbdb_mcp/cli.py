from __future__ import annotations

import argparse
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
    p.add_argument("--interval")
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
        result = strata_search(name=args.name, interval=args.interval, limit=args.limit, timeout=args.timeout)
    elif args.command == "auto":
        result = combined_auto(name=args.name, record_type=args.record_type, limit=args.limit, timeout=args.timeout)
    elif args.command == "associated":
        result = associated_by_reference(ref_id=args.ref_id, record_type=args.record_type, show=args.show, timeout=args.timeout)
    else:
        raise AssertionError(args.command)

    pretty = pretty_result(result)
    sys.stdout.write(pretty)
    if not pretty.endswith("\n"):
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
