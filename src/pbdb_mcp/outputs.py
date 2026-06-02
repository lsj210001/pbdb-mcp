from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

try:
    from .research import _collect_queries
except ImportError:
    from research import _collect_queries  # type: ignore[no-redef]


def _walk(value: Any) -> list[Any]:
    items = [value]
    if isinstance(value, dict):
        for child in value.values():
            items.extend(_walk(child))
    elif isinstance(value, list):
        for child in value:
            items.extend(_walk(child))
    return items


def _records(value: Any) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for item in _walk(value):
        if isinstance(item, dict):
            candidate = item.get("records")
            if isinstance(candidate, list):
                records.extend(record for record in candidate if isinstance(record, dict))
    return records


def _reference_key(record: dict[str, Any]) -> str | None:
    value = record.get("oid")
    if isinstance(value, str) and value.startswith("ref:"):
        return value
    title = record.get("tit")
    year = record.get("pby") or record.get("opy")
    author = record.get("atr") or record.get("oat")
    if title:
        return "|".join(str(part) for part in (author, year, title) if part)
    return None


def _reference_entry(record: dict[str, Any]) -> dict[str, Any]:
    ref_id = record.get("oid") if isinstance(record.get("oid"), str) and str(record.get("oid")).startswith("ref:") else record.get("rid")
    return {
        "ref_id": ref_id,
        "author": record.get("atr") or record.get("oat") or record.get("al1"),
        "year": record.get("pby") or record.get("opy"),
        "title": record.get("tit"),
        "publication": record.get("pbt"),
        "doi": record.get("doi"),
        "record": record,
    }


def bibliography_pack(pack: dict[str, Any], limit: int = 100) -> dict[str, Any]:
    seen: set[str] = set()
    entries: list[dict[str, Any]] = []
    for record in _records(pack):
        key = _reference_key(record)
        if not key or key in seen:
            continue
        if not (str(record.get("oid", "")).startswith("ref:") or record.get("tit") or record.get("pbt") or record.get("doi")):
            continue
        seen.add(key)
        entries.append(_reference_entry(record))
        if len(entries) >= limit:
            break

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_workflow": (pack.get("manifest") or {}).get("workflow"),
        "source_generated_at": pack.get("generated_at"),
        "reference_count": len(entries),
        "references": entries,
        "research_notes": [
            "Bibliography entries are extracted from PBDB records present in the supplied evidence pack.",
            "A source publication may appear only if the underlying PBDB query returned reference metadata.",
        ],
    }


def pack_validation_report(pack: dict[str, Any]) -> dict[str, Any]:
    flags: list[dict[str, str]] = []
    evidence = pack.get("evidence")
    manifest = pack.get("manifest")
    records = _records(pack)
    queries = _collect_queries(pack)
    references = bibliography_pack(pack, limit=1000)["references"]

    if not isinstance(manifest, dict):
        flags.append({"code": "missing_manifest", "severity": "warning", "message": "The pack has no top-level manifest."})
    if not isinstance(evidence, dict):
        flags.append({"code": "missing_evidence", "severity": "error", "message": "The pack has no evidence object."})
    if not queries:
        flags.append({"code": "missing_query_urls", "severity": "error", "message": "The pack has no reproducible query URLs."})
    if queries and any("endpoint" not in query or "params" not in query for query in queries):
        flags.append({"code": "incomplete_query_metadata", "severity": "warning", "message": "Some queries lack endpoint or parameter metadata."})
    if not records:
        flags.append({"code": "no_records", "severity": "warning", "message": "The pack contains no PBDB records."})
    if not references:
        flags.append({"code": "no_reference_metadata", "severity": "caution", "message": "No reference metadata could be extracted from the pack."})

    summary = pack.get("summary") if isinstance(pack.get("summary"), dict) else {}
    has_age_range = isinstance(summary, dict) and bool(summary.get("age_range_ma_from_occurrences"))
    if not has_age_range:
        for item in _walk(summary):
            if isinstance(item, dict) and item.get("age_range_ma_from_occurrences"):
                has_age_range = True
                break
    if not has_age_range:
        flags.append({"code": "no_age_range_summary", "severity": "info", "message": "No occurrence-derived age range summary was found."})

    has_error = any(flag["severity"] == "error" for flag in flags)
    has_warning = any(flag["severity"] == "warning" for flag in flags)
    has_caution = any(flag["severity"] == "caution" for flag in flags)
    if has_error:
        overall = "invalid"
    elif has_warning:
        overall = "needs_repair"
    elif has_caution:
        overall = "usable_with_caution"
    else:
        overall = "valid"

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "overall": overall,
        "flags": flags,
        "metrics": {
            "query_count": len(queries),
            "record_count": len(records),
            "reference_count": len(references),
            "has_manifest": isinstance(manifest, dict),
            "has_evidence": isinstance(evidence, dict),
        },
    }


def _format_reference(entry: dict[str, Any]) -> str:
    parts = [part for part in (entry.get("author"), entry.get("year"), entry.get("title"), entry.get("publication")) if part]
    text = ". ".join(str(part) for part in parts)
    ref_id = entry.get("ref_id")
    doi = entry.get("doi")
    suffix = []
    if ref_id:
        suffix.append(str(ref_id))
    if doi:
        suffix.append(f"doi:{doi}")
    return f"{text} ({'; '.join(suffix)})" if suffix else text


def research_summary_markdown(pack: dict[str, Any], title: str | None = None, max_references: int = 10, max_queries: int = 20) -> str:
    manifest = pack.get("manifest") if isinstance(pack.get("manifest"), dict) else {}
    summary = pack.get("summary") if isinstance(pack.get("summary"), dict) else {}
    validation = pack_validation_report(pack)
    bibliography = bibliography_pack(pack, limit=max_references)
    queries = _collect_queries(pack)[:max_queries]

    heading = title or manifest.get("workflow") or "PBDB Research Summary"
    lines = [f"# {heading}", ""]
    lines.extend(
        [
            "## Scope",
            f"- Workflow: {manifest.get('workflow', 'unknown')}",
            f"- Generated at: {pack.get('generated_at') or manifest.get('generated_at', 'unknown')}",
            f"- PBDB base URL: {manifest.get('pbdb_base_url', 'unknown')}",
            "",
            "## Summary",
            f"```json\n{json.dumps(summary, ensure_ascii=False, indent=2)}\n```",
            "",
            "## Validation",
            f"- Overall: {validation['overall']}",
        ]
    )
    for flag in validation["flags"]:
        lines.append(f"- {flag['severity']}: {flag['code']} - {flag['message']}")

    lines.extend(["", "## References"])
    if bibliography["references"]:
        for entry in bibliography["references"]:
            lines.append(f"- {_format_reference(entry)}")
    else:
        lines.append("- No reference metadata extracted from the supplied pack.")

    lines.extend(["", "## Reproducible Queries"])
    if queries:
        for query in queries:
            lines.append(f"- `{query.get('name', 'query')}` `{query.get('endpoint', '')}` records={query.get('record_count', 'unknown')}: {query.get('url')}")
    else:
        lines.append("- No query URLs found.")

    notes = pack.get("research_notes")
    if isinstance(notes, list) and notes:
        lines.extend(["", "## Caveats"])
        for note in notes:
            lines.append(f"- {note}")

    return "\n".join(lines).rstrip() + "\n"
