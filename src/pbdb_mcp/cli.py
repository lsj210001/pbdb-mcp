from __future__ import annotations

import argparse
import sys

try:
    from .client import (
        collections_search,
        intervals_search,
        occurrences_search,
        pretty_result,
        references_search,
        request,
        strata_search,
        taxon_lookup,
    )
except ImportError:
    from client import (  # type: ignore[no-redef]
        collections_search,
        intervals_search,
        occurrences_search,
        pretty_result,
        references_search,
        request,
        strata_search,
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

    p = sub.add_parser("occurrences", help="Search occurrences")
    p.add_argument("--base-name")
    p.add_argument("--taxon-name")
    p.add_argument("--interval")
    p.add_argument("--country")
    p.add_argument("--state")
    p.add_argument("--limit", type=int, default=50)
    p.add_argument("--show", default="coords,attr")
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

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "request":
        result = request(args.path, parse_param_pairs(args.param), timeout=args.timeout)
    elif args.command == "taxon":
        result = taxon_lookup(name=args.name, taxon_no=args.taxon_no, show=args.show, timeout=args.timeout)
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
    else:
        raise AssertionError(args.command)

    pretty = pretty_result(result)
    sys.stdout.write(pretty)
    if not pretty.endswith("\n"):
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
