from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

try:
    from .client import (
        PBDBResponse,
        associated_by_reference,
        collections_search,
        geo_summary,
        occs_refs,
        occs_strata_summary,
        occurrences_search,
        references_search,
        specimens_search,
        taxa_opinions,
        taxa_search,
        taxon_lookup,
    )
except ImportError:
    from client import (  # type: ignore[no-redef]
        PBDBResponse,
        associated_by_reference,
        collections_search,
        geo_summary,
        occs_refs,
        occs_strata_summary,
        occurrences_search,
        references_search,
        specimens_search,
        taxa_opinions,
        taxa_search,
        taxon_lookup,
    )


def _records(response: PBDBResponse) -> list[dict[str, Any]]:
    if isinstance(response.body, dict):
        records = response.body.get("records", [])
        if isinstance(records, list):
            return [record for record in records if isinstance(record, dict)]
    return []


def _query(name: str, response: PBDBResponse) -> dict[str, Any]:
    return {"name": name, "url": response.url, "record_count": len(_records(response))}


def _response_payload(name: str, response: PBDBResponse) -> dict[str, Any]:
    return {"query": _query(name, response), "records": _records(response)}


def _unique_values(records: list[dict[str, Any]], keys: tuple[str, ...], limit: int = 12) -> list[Any]:
    values: list[Any] = []
    for record in records:
        for key in keys:
            value = record.get(key)
            if value not in (None, "", "__") and value not in values:
                values.append(value)
                break
        if len(values) >= limit:
            break
    return values


def _age_range(records: list[dict[str, Any]]) -> dict[str, float] | None:
    early_values: list[float] = []
    late_values: list[float] = []
    for record in records:
        for key, target in (("eag", early_values), ("lag", late_values)):
            value = record.get(key)
            try:
                if value is not None:
                    target.append(float(value))
            except (TypeError, ValueError):
                continue
    if not early_values and not late_values:
        return None
    result: dict[str, float] = {}
    if early_values:
        result["max_ma"] = max(early_values)
    if late_values:
        result["min_ma"] = min(late_values)
    return result


def _reference_ids(records: list[dict[str, Any]], limit: int = 12) -> list[str]:
    ids: list[str] = []
    for record in records:
        value = record.get("rid") or record.get("oid")
        if isinstance(value, str) and value.startswith("ref:") and value not in ids:
            ids.append(value)
        if len(ids) >= limit:
            break
    return ids


def taxon_fact_card(
    *,
    name: str,
    limit: int = 10,
    geo_level: int = 2,
    timeout: int = 30,
) -> dict[str, Any]:
    taxon = taxon_lookup(name=name, show="attr", timeout=timeout)
    taxa = taxa_search(base_name=name, limit=limit, show="attr", timeout=timeout)
    opinions = taxa_opinions(base_name=name, limit=limit, timeout=timeout)
    occurrences = occurrences_search(base_name=name, limit=limit, show="coords,attr", timeout=timeout)
    collections = collections_search(base_name=name, limit=limit, timeout=timeout)
    specimens = specimens_search(base_name=name, limit=limit, timeout=timeout)
    references = occs_refs(base_name=name, limit=limit, show="attr", timeout=timeout)
    strata = occs_strata_summary(base_name=name, limit=limit, timeout=timeout)
    geography = geo_summary(record_type="occs", base_name=name, level=geo_level, timeout=timeout)

    occurrence_records = _records(occurrences)
    collection_records = _records(collections)
    specimen_records = _records(specimens)
    reference_records = _records(references)
    strata_records = _records(strata)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input": {"name": name, "limit": limit, "geo_level": geo_level},
        "summary": {
            "accepted_or_matching_taxon": _records(taxon)[:1],
            "taxa_count": len(_records(taxa)),
            "opinion_count": len(_records(opinions)),
            "occurrence_count_sample": len(occurrence_records),
            "collection_count_sample": len(collection_records),
            "specimen_count_sample": len(specimen_records),
            "reference_count_sample": len(reference_records),
            "age_range_ma_from_occurrences": _age_range(occurrence_records),
            "countries_from_collections": _unique_values(collection_records, ("cc2", "cc3", "country")),
            "intervals_from_occurrences": _unique_values(occurrence_records, ("oei", "eag")),
            "strata_or_lithologies": _unique_values(strata_records, ("sfm", "sgr", "smb", "lth")),
            "reference_ids": _reference_ids(reference_records),
            "specimen_examples": specimen_records[: min(5, len(specimen_records))],
        },
        "evidence": {
            "taxon": _response_payload("taxon_lookup", taxon),
            "taxa": _response_payload("taxa_search", taxa),
            "taxonomic_opinions": _response_payload("taxa_opinions", opinions),
            "occurrences": _response_payload("occurrences_search", occurrences),
            "collections": _response_payload("collections_search", collections),
            "specimens": _response_payload("specimens_search", specimens),
            "references": _response_payload("occs_refs", references),
            "strata": _response_payload("occs_strata_summary", strata),
            "geography": _response_payload("geo_summary", geography),
        },
        "research_notes": [
            "Occurrence and collection counts in this card are sample sizes from the current query limit, not true abundance.",
            "PBDB is a live database; use the included query URLs for reproducibility.",
            "Use reference records and taxonomic opinions before making confident classification or reconstruction claims.",
        ],
    }


def reference_evidence_pack(
    *,
    ref_id: str | int,
    record_type: str = "all",
    timeout: int = 30,
) -> dict[str, Any]:
    reference = references_search(ref_id=ref_id, show="attr", timeout=timeout)
    associated = associated_by_reference(ref_id=ref_id, record_type=record_type, show="countries", timeout=timeout)
    associated_records = _records(associated)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input": {"ref_id": ref_id, "record_type": record_type},
        "summary": {
            "reference": _records(reference)[:1],
            "associated_record_count": len(associated_records),
            "associated_taxa": [record for record in associated_records if str(record.get("oid", "")).startswith("txn:")],
            "associated_opinions": [record for record in associated_records if str(record.get("oid", "")).startswith("opn:")],
            "associated_collections": [record for record in associated_records if str(record.get("oid", "")).startswith("col:")],
        },
        "evidence": {
            "reference": _response_payload("references_search", reference),
            "associated_records": _response_payload("associated_by_reference", associated),
        },
        "research_notes": [
            "Associated records show PBDB records linked to this reference, not every claim made in the publication.",
            "Use the reference metadata and associated records as a starting point for paper-level fact checking.",
        ],
    }


def taxonomy_dispute_report(
    *,
    name: str,
    limit: int = 25,
    timeout: int = 30,
) -> dict[str, Any]:
    taxon = taxon_lookup(name=name, show="attr", timeout=timeout)
    opinions = taxa_opinions(base_name=name, limit=limit, timeout=timeout)
    opinion_records = _records(opinions)
    reference_ids = _reference_ids(opinion_records, limit=limit)
    references: list[dict[str, Any]] = []
    reference_queries: list[dict[str, Any]] = []
    for ref_id in reference_ids[:10]:
        response = references_search(ref_id=ref_id.removeprefix("ref:"), show="attr", timeout=timeout)
        reference_queries.append(_query(f"references_search:{ref_id}", response))
        references.extend(_records(response))

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input": {"name": name, "limit": limit},
        "summary": {
            "taxon": _records(taxon)[:1],
            "opinion_count": len(opinion_records),
            "statuses": _unique_values(opinion_records, ("sta",), limit=20),
            "parent_taxa_named_in_opinions": _unique_values(opinion_records, ("prl", "par"), limit=20),
            "opinion_authors": _unique_values(opinion_records, ("oat",), limit=20),
            "opinion_years": _unique_values(opinion_records, ("opy",), limit=20),
            "reference_ids": reference_ids,
            "references": references,
        },
        "evidence": {
            "taxon": _response_payload("taxon_lookup", taxon),
            "opinions": _response_payload("taxa_opinions", opinions),
            "reference_queries": reference_queries,
        },
        "research_notes": [
            "Taxonomic opinions represent database records used to build PBDB's taxonomic hierarchy; they may include superseded opinions.",
            "Do not convert opinion history into a definitive dispute claim without reading the referenced papers.",
        ],
    }
