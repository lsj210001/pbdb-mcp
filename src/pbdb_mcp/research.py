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
        occs_taxa_summary,
        occurrences_search,
        references_search,
        strata_search,
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
        occs_taxa_summary,
        occurrences_search,
        references_search,
        strata_search,
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


def _accepted_name(records: list[dict[str, Any]]) -> str | None:
    if not records:
        return None
    record = records[0]
    for key in ("nam", "taxon_name", "tnm", "name"):
        value = record.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def _coordinate_completeness(records: list[dict[str, Any]]) -> dict[str, Any]:
    if not records:
        return {"records_checked": 0, "records_with_coordinates": 0, "ratio": None}

    with_coordinates = 0
    for record in records:
        lat = record.get("lat") or record.get("la1") or record.get("latlng")
        lng = record.get("lng") or record.get("lo1") or record.get("latlng")
        if lat not in (None, "", "__") and lng not in (None, "", "__"):
            with_coordinates += 1

    return {
        "records_checked": len(records),
        "records_with_coordinates": with_coordinates,
        "ratio": round(with_coordinates / len(records), 3),
    }


def _quality_flags(
    *,
    input_scope: dict[str, Any],
    occurrence_records: list[dict[str, Any]],
    collection_records: list[dict[str, Any]],
    reference_records: list[dict[str, Any]],
    opinion_records: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    flags: list[dict[str, str]] = []
    age_range = _age_range(occurrence_records)
    coordinate_completeness = _coordinate_completeness(occurrence_records)

    if not any(value not in (None, "", []) for value in input_scope.values()):
        flags.append(
            {
                "code": "missing_scope",
                "severity": "warning",
                "message": "The query has no taxon, interval, or geography filter; conclusions may be too broad.",
            }
        )

    if not occurrence_records:
        flags.append(
            {
                "code": "no_occurrence_sample",
                "severity": "warning",
                "message": "The sampled query returned no occurrence records.",
            }
        )
    elif len(occurrence_records) < 3:
        flags.append(
            {
                "code": "low_occurrence_sample",
                "severity": "caution",
                "message": "The sampled query returned fewer than three occurrence records.",
            }
        )

    if not collection_records:
        flags.append(
            {
                "code": "no_collection_sample",
                "severity": "warning",
                "message": "The sampled query returned no collection records.",
            }
        )

    if len(reference_records) < 3:
        flags.append(
            {
                "code": "low_reference_sample",
                "severity": "caution",
                "message": "The sampled query returned fewer than three reference records.",
            }
        )

    if age_range and "max_ma" in age_range and "min_ma" in age_range and age_range["max_ma"] - age_range["min_ma"] > 20:
        flags.append(
            {
                "code": "broad_age_range",
                "severity": "caution",
                "message": "The sampled occurrences span more than 20 million years; avoid treating them as one narrow time slice.",
            }
        )

    ratio = coordinate_completeness["ratio"]
    if isinstance(ratio, float) and ratio < 0.5:
        flags.append(
            {
                "code": "low_coordinate_coverage",
                "severity": "caution",
                "message": "Fewer than half of sampled occurrence records include coordinates.",
            }
        )

    if opinion_records:
        statuses = _unique_values(opinion_records, ("sta",), limit=20)
        if len(statuses) > 1 or len(opinion_records) >= 5:
            flags.append(
                {
                    "code": "taxonomic_opinions_present",
                    "severity": "info",
                    "message": "Multiple taxonomic opinion records are present; check opinion history before making classification claims.",
                }
            )

    warning_count = sum(1 for flag in flags if flag["severity"] == "warning")
    caution_count = sum(1 for flag in flags if flag["severity"] == "caution")
    if warning_count:
        overall = "limited"
    elif caution_count >= 2:
        overall = "needs_review"
    elif caution_count == 1:
        overall = "usable_with_caution"
    else:
        overall = "usable"

    return {
        "overall": overall,
        "flags": flags,
        "metrics": {
            "occurrence_sample_size": len(occurrence_records),
            "collection_sample_size": len(collection_records),
            "reference_sample_size": len(reference_records),
            "opinion_sample_size": len(opinion_records or []),
            "age_range_ma_from_occurrences": age_range,
            "coordinate_completeness": coordinate_completeness,
        },
        "research_notes": [
            "Quality flags describe the sampled PBDB query result, not the full scientific literature.",
            "Use included query URLs and source references before turning sampled database patterns into claims.",
        ],
    }


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


def evidence_quality_report(
    *,
    name: str | None = None,
    interval: str | None = None,
    country: str | None = None,
    state: str | None = None,
    limit: int = 25,
    timeout: int = 30,
) -> dict[str, Any]:
    occurrences = occurrences_search(base_name=name, interval=interval, country=country, state=state, limit=limit, show="coords,attr", timeout=timeout)
    collections = collections_search(base_name=name, interval=interval, country=country, state=state, limit=limit, timeout=timeout)
    references = occs_refs(base_name=name, interval=interval, country=country, state=state, limit=limit, show="attr", timeout=timeout)
    opinions = taxa_opinions(base_name=name, limit=limit, timeout=timeout) if name else None

    occurrence_records = _records(occurrences)
    collection_records = _records(collections)
    reference_records = _records(references)
    opinion_records = _records(opinions) if opinions else []

    input_scope = {"name": name, "interval": interval, "country": country, "state": state}
    quality = _quality_flags(
        input_scope=input_scope,
        occurrence_records=occurrence_records,
        collection_records=collection_records,
        reference_records=reference_records,
        opinion_records=opinion_records,
    )

    evidence = {
        "occurrences": _response_payload("occurrences_search", occurrences),
        "collections": _response_payload("collections_search", collections),
        "references": _response_payload("occs_refs", references),
    }
    if opinions:
        evidence["taxonomic_opinions"] = _response_payload("taxa_opinions", opinions)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input": {"name": name, "interval": interval, "country": country, "state": state, "limit": limit},
        "summary": quality,
        "evidence": evidence,
    }


def taxa_compare_pack(
    *,
    names: list[str],
    limit: int = 10,
    geo_level: int = 2,
    timeout: int = 30,
) -> dict[str, Any]:
    cleaned_names = [name.strip() for name in names if name and name.strip()]
    if len(cleaned_names) < 2:
        raise ValueError("At least two taxon names are required.")
    if len(cleaned_names) > 5:
        raise ValueError("Compare at most five taxon names at a time.")

    cards = [taxon_fact_card(name=name, limit=limit, geo_level=geo_level, timeout=timeout) for name in cleaned_names]
    rows: list[dict[str, Any]] = []
    for card in cards:
        summary = card["summary"]
        evidence = card["evidence"]
        opinion_records = evidence["taxonomic_opinions"]["records"]
        quality = _quality_flags(
            input_scope={"name": card["input"]["name"]},
            occurrence_records=evidence["occurrences"]["records"],
            collection_records=evidence["collections"]["records"],
            reference_records=evidence["references"]["records"],
            opinion_records=opinion_records,
        )
        rows.append(
            {
                "input_name": card["input"]["name"],
                "accepted_or_matching_name": _accepted_name(summary["accepted_or_matching_taxon"]),
                "age_range_ma_from_occurrences": summary["age_range_ma_from_occurrences"],
                "occurrence_count_sample": summary["occurrence_count_sample"],
                "collection_count_sample": summary["collection_count_sample"],
                "reference_count_sample": summary["reference_count_sample"],
                "opinion_count": summary["opinion_count"],
                "countries_from_collections": summary["countries_from_collections"],
                "reference_ids": summary["reference_ids"],
                "quality_overall": quality["overall"],
                "quality_flags": quality["flags"],
            }
        )

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input": {"names": cleaned_names, "limit": limit, "geo_level": geo_level},
        "summary": {
            "comparison_rows": rows,
            "shared_caveats": [
                "Rows compare sampled PBDB query results under the same limit, not total fossil abundance.",
                "Differences in sampling, taxonomy, geography, and reference coverage can affect apparent patterns.",
            ],
        },
        "evidence": {"taxon_fact_cards": cards},
    }


def interval_context_pack(
    *,
    interval: str,
    limit: int = 25,
    geo_level: int = 2,
    timeout: int = 30,
) -> dict[str, Any]:
    occurrences = occurrences_search(interval=interval, limit=limit, show="coords,attr", timeout=timeout)
    taxa = occs_taxa_summary(interval=interval, limit=limit, show="attr", timeout=timeout)
    collections = collections_search(interval=interval, limit=limit, timeout=timeout)
    references = occs_refs(interval=interval, limit=limit, show="attr", timeout=timeout)
    strata = occs_strata_summary(interval=interval, limit=limit, timeout=timeout)
    geography = geo_summary(record_type="occs", interval=interval, level=geo_level, timeout=timeout)

    occurrence_records = _records(occurrences)
    collection_records = _records(collections)
    reference_records = _records(references)
    strata_records = _records(strata)
    taxon_records = _records(taxa)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input": {"interval": interval, "limit": limit, "geo_level": geo_level},
        "summary": {
            "taxa_count_sample": len(taxon_records),
            "occurrence_count_sample": len(occurrence_records),
            "collection_count_sample": len(collection_records),
            "reference_count_sample": len(reference_records),
            "age_range_ma_from_occurrences": _age_range(occurrence_records),
            "taxa_examples": taxon_records[: min(10, len(taxon_records))],
            "countries_from_collections": _unique_values(collection_records, ("cc2", "cc3", "country"), limit=20),
            "strata_or_lithologies": _unique_values(strata_records, ("sfm", "sgr", "smb", "lth"), limit=20),
            "reference_ids": _reference_ids(reference_records, limit=20),
            "quality": _quality_flags(
                input_scope={"interval": interval},
                occurrence_records=occurrence_records,
                collection_records=collection_records,
                reference_records=reference_records,
            ),
        },
        "evidence": {
            "occurrences": _response_payload("occurrences_search", occurrences),
            "taxa": _response_payload("occs_taxa_summary", taxa),
            "collections": _response_payload("collections_search", collections),
            "references": _response_payload("occs_refs", references),
            "strata": _response_payload("occs_strata_summary", strata),
            "geography": _response_payload("geo_summary", geography),
        },
        "research_notes": [
            "Interval context packs summarize sampled PBDB records for an interval; they do not reconstruct a complete paleoecosystem.",
            "Use reference and collection records to check whether apparent patterns reflect sampling intensity.",
        ],
    }


def locality_context_pack(
    *,
    country: str | None = None,
    state: str | None = None,
    interval: str | None = None,
    base_name: str | None = None,
    stratum_name: str | None = None,
    limit: int = 25,
    geo_level: int = 2,
    timeout: int = 30,
) -> dict[str, Any]:
    if not any((country, state, interval, base_name, stratum_name)):
        raise ValueError("Provide at least one locality, interval, taxon, or stratum filter.")

    occurrences = occurrences_search(base_name=base_name, interval=interval, country=country, state=state, limit=limit, show="coords,attr", timeout=timeout)
    taxa = occs_taxa_summary(base_name=base_name, interval=interval, country=country, state=state, limit=limit, show="attr", timeout=timeout)
    collections = collections_search(base_name=base_name, interval=interval, country=country, state=state, limit=limit, timeout=timeout)
    references = occs_refs(base_name=base_name, interval=interval, country=country, state=state, limit=limit, show="attr", timeout=timeout)
    geography = geo_summary(record_type="colls", base_name=base_name, interval=interval, country=country, state=state, level=geo_level, timeout=timeout)
    strata = strata_search(name=stratum_name, limit=limit, timeout=timeout) if stratum_name else None

    occurrence_records = _records(occurrences)
    collection_records = _records(collections)
    reference_records = _records(references)
    taxon_records = _records(taxa)
    strata_records = _records(strata) if strata else []

    evidence = {
        "occurrences": _response_payload("occurrences_search", occurrences),
        "taxa": _response_payload("occs_taxa_summary", taxa),
        "collections": _response_payload("collections_search", collections),
        "references": _response_payload("occs_refs", references),
        "geography": _response_payload("geo_summary", geography),
    }
    if strata:
        evidence["strata"] = _response_payload("strata_search", strata)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input": {
            "country": country,
            "state": state,
            "interval": interval,
            "base_name": base_name,
            "stratum_name": stratum_name,
            "limit": limit,
            "geo_level": geo_level,
        },
        "summary": {
            "taxa_count_sample": len(taxon_records),
            "occurrence_count_sample": len(occurrence_records),
            "collection_count_sample": len(collection_records),
            "reference_count_sample": len(reference_records),
            "age_range_ma_from_occurrences": _age_range(occurrence_records),
            "taxa_examples": taxon_records[: min(10, len(taxon_records))],
            "collection_names_or_numbers": _unique_values(collection_records, ("nam", "oid", "cid"), limit=20),
            "strata_matches": strata_records,
            "reference_ids": _reference_ids(reference_records, limit=20),
            "quality": _quality_flags(
                input_scope={"country": country, "state": state, "interval": interval, "base_name": base_name, "stratum_name": stratum_name},
                occurrence_records=occurrence_records,
                collection_records=collection_records,
                reference_records=reference_records,
            ),
        },
        "evidence": evidence,
        "research_notes": [
            "Locality context packs summarize sampled PBDB records for the supplied filters.",
            "Stratum lookup is included as a contextual lookup; occurrence and collection filters may not be restricted by stratum name unless PBDB supports the supplied filter combination.",
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
