from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen


PBDB_BASE_URL = "https://paleobiodb.org/data1.2/"
DEFAULT_TIMEOUT = 30
USER_AGENT = "xhs-research-pbdb/1.0"


@dataclass
class PBDBResponse:
    url: str
    content_type: str
    status: int
    body: Any
    raw_text: str


def _normalize_params(params: dict[str, Any] | None) -> dict[str, str]:
    cleaned: dict[str, str] = {}
    if not params:
        return cleaned

    for key, value in params.items():
        if value is None:
            continue
        if isinstance(value, bool):
            cleaned[key] = "true" if value else "false"
        elif isinstance(value, (list, tuple, set)):
            cleaned[key] = ",".join(str(item) for item in value if item is not None)
        else:
            cleaned[key] = str(value)
    return cleaned


def build_url(path: str, params: dict[str, Any] | None = None) -> str:
    base = urljoin(PBDB_BASE_URL, path.lstrip("/"))
    query = urlencode(_normalize_params(params), doseq=False)
    return f"{base}?{query}" if query else base


def request(path: str, params: dict[str, Any] | None = None, timeout: int = DEFAULT_TIMEOUT) -> PBDBResponse:
    url = build_url(path, params)
    req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})

    try:
        with urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            content_type = resp.headers.get_content_type()
            text = raw.decode(resp.headers.get_content_charset() or "utf-8", errors="replace")
            try:
                body = json.loads(text)
            except json.JSONDecodeError:
                body = text
            return PBDBResponse(url=url, content_type=content_type, status=resp.status, body=body, raw_text=text)
    except HTTPError as err:
        payload = err.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"PBDB HTTP {err.code} for {url}: {payload}") from err
    except URLError as err:
        raise RuntimeError(f"PBDB request failed for {url}: {err.reason}") from err


def pretty_result(result: PBDBResponse) -> str:
    if isinstance(result.body, (dict, list)):
        return json.dumps(result.body, ensure_ascii=False, indent=2)
    return result.raw_text


def taxon_lookup(name: str | None = None, taxon_no: str | int | None = None, show: str | None = None, timeout: int = DEFAULT_TIMEOUT) -> PBDBResponse:
    params: dict[str, Any] = {}
    if name is not None:
        params["name"] = name
    if taxon_no is not None:
        params["taxon_no"] = taxon_no
    if show is not None:
        params["show"] = show
    return request("taxa/single.json", params=params, timeout=timeout)


def occurrences_search(
    *,
    base_name: str | None = None,
    taxon_name: str | None = None,
    interval: str | None = None,
    country: str | None = None,
    state: str | None = None,
    limit: int | None = 50,
    show: str | None = "coords,attr",
    timeout: int = DEFAULT_TIMEOUT,
) -> PBDBResponse:
    params: dict[str, Any] = {}
    if base_name is not None:
        params["base_name"] = base_name
    if taxon_name is not None:
        params["taxon_name"] = taxon_name
    if interval is not None:
        params["interval"] = interval
    if country is not None:
        params["country"] = country
    if state is not None:
        params["state"] = state
    if limit is not None:
        params["limit"] = limit
    if show is not None:
        params["show"] = show
    return request("occs/list.json", params=params, timeout=timeout)


def collections_search(
    *,
    base_name: str | None = None,
    taxon_name: str | None = None,
    interval: str | None = None,
    country: str | None = None,
    state: str | None = None,
    limit: int | None = 50,
    show: str | None = "loc,time,strat,ref",
    timeout: int = DEFAULT_TIMEOUT,
) -> PBDBResponse:
    params: dict[str, Any] = {}
    if base_name is not None:
        params["base_name"] = base_name
    if taxon_name is not None:
        params["taxon_name"] = taxon_name
    if interval is not None:
        params["interval"] = interval
    if country is not None:
        params["country"] = country
    if state is not None:
        params["state"] = state
    if limit is not None:
        params["limit"] = limit
    if show is not None:
        params["show"] = show
    return request("colls/list.json", params=params, timeout=timeout)


def references_search(
    *,
    ref_id: str | int | None = None,
    ref_match: str | None = None,
    ref_author: str | None = None,
    ref_title: str | None = None,
    ref_doi: str | None = None,
    pub_title: str | None = None,
    all_records: bool | None = None,
    limit: int | None = 50,
    show: str | None = "attr",
    timeout: int = DEFAULT_TIMEOUT,
) -> PBDBResponse:
    params: dict[str, Any] = {}
    if ref_id is not None:
        params["ref_id"] = ref_id
    if ref_match is not None:
        params["ref_match"] = ref_match
    if ref_author is not None:
        params["ref_author"] = ref_author
    if ref_title is not None:
        params["ref_title"] = ref_title
    if ref_doi is not None:
        params["ref_doi"] = ref_doi
    if pub_title is not None:
        params["pub_title"] = pub_title
    if all_records is not None:
        params["all_records"] = all_records
    if limit is not None:
        params["limit"] = limit
    if show is not None:
        params["show"] = show
    return request("refs/list.json", params=params, timeout=timeout)


def intervals_search(*, name: str | None = None, limit: int | None = 50, timeout: int = DEFAULT_TIMEOUT) -> PBDBResponse:
    params: dict[str, Any] = {}
    if name is not None:
        params["name"] = name
    if limit is not None:
        params["limit"] = limit
    return request("intervals/list.json", params=params, timeout=timeout)


def strata_search(*, name: str | None = None, interval: str | None = None, limit: int | None = 50, timeout: int = DEFAULT_TIMEOUT) -> PBDBResponse:
    params: dict[str, Any] = {}
    if name is not None:
        params["name"] = name
    if interval is not None:
        params["interval"] = interval
    if limit is not None:
        params["limit"] = limit
    return request("strata/list.json", params=params, timeout=timeout)
