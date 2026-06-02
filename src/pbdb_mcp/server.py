from __future__ import annotations

import json
import sys
from typing import Any, Dict


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


PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "pbdb-mcp"
SERVER_VERSION = "0.1.0"


def _read_message() -> dict[str, Any] | None:
    headers: dict[str, str] = {}
    while True:
        line = sys.stdin.buffer.readline()
        if not line:
            return None
        line = line.strip()
        if not line:
            break
        if b":" in line:
            key, value = line.split(b":", 1)
            headers[key.decode("ascii", errors="replace").lower()] = value.strip().decode("ascii", errors="replace")

    length = int(headers.get("content-length", "0"))
    if length <= 0:
        return None
    raw = sys.stdin.buffer.read(length)
    return json.loads(raw.decode("utf-8"))


def _write_message(payload: dict[str, Any]) -> None:
    raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    sys.stdout.buffer.write(f"Content-Length: {len(raw)}\r\n\r\n".encode("ascii"))
    sys.stdout.buffer.write(raw)
    sys.stdout.buffer.flush()


def _ok(id_value: Any, result: Any) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": id_value, "result": result}


def _error(id_value: Any, code: int, message: str, data: Any | None = None) -> dict[str, Any]:
    payload: Dict[str, Any] = {"code": code, "message": message}
    if data is not None:
        payload["data"] = data
    return {"jsonrpc": "2.0", "id": id_value, "error": payload}


def _tool_schema() -> list[dict[str, Any]]:
    return [
        {
            "name": "pbdb_request",
            "description": "Call an arbitrary PBDB API path under https://paleobiodb.org/data1.2/ and return the raw response.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path like taxa/single.json or occs/list.json"},
                    "params": {"type": "object", "additionalProperties": True},
                    "timeout": {"type": "integer", "minimum": 1, "maximum": 120},
                },
                "required": ["path"],
            },
        },
        {
            "name": "taxon_lookup",
            "description": "Look up a taxon by name or taxon_no.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "taxon_no": {"type": ["string", "integer"]},
                    "show": {"type": "string", "default": "attr"},
                    "timeout": {"type": "integer", "minimum": 1, "maximum": 120},
                },
            },
        },
        {
            "name": "occurrences_search",
            "description": "Search fossil occurrences by taxon, interval, or geography.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "base_name": {"type": "string"},
                    "taxon_name": {"type": "string"},
                    "interval": {"type": "string"},
                    "country": {"type": "string"},
                    "state": {"type": "string"},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 500},
                    "show": {"type": "string"},
                    "timeout": {"type": "integer", "minimum": 1, "maximum": 120},
                },
            },
        },
        {
            "name": "collections_search",
            "description": "Search fossil collections by taxon, interval, or geography.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "base_name": {"type": "string"},
                    "taxon_name": {"type": "string"},
                    "interval": {"type": "string"},
                    "country": {"type": "string"},
                    "state": {"type": "string"},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 500},
                    "show": {"type": "string"},
                    "timeout": {"type": "integer", "minimum": 1, "maximum": 120},
                },
            },
        },
        {
            "name": "references_search",
            "description": "Search PBDB references by ref_id, title, author, DOI, journal, or broad match text. To find references for a taxon, first get rid from occurrences or collections.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "ref_id": {"type": ["string", "integer"]},
                    "ref_match": {"type": "string"},
                    "ref_author": {"type": "string"},
                    "ref_title": {"type": "string"},
                    "ref_doi": {"type": "string"},
                    "pub_title": {"type": "string"},
                    "all_records": {"type": "boolean"},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 500},
                    "show": {"type": "string"},
                    "timeout": {"type": "integer", "minimum": 1, "maximum": 120},
                },
            },
        },
        {
            "name": "intervals_search",
            "description": "Search geological intervals.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 500},
                    "timeout": {"type": "integer", "minimum": 1, "maximum": 120},
                },
            },
        },
        {
            "name": "strata_search",
            "description": "Search stratigraphic units.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "interval": {"type": "string"},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 500},
                    "timeout": {"type": "integer", "minimum": 1, "maximum": 120},
                },
            },
        },
    ]


def _call_tool(name: str, args: dict[str, Any] | None) -> str:
    args = args or {}
    timeout = int(args.get("timeout", 30))

    if name == "pbdb_request":
        result = request(args["path"], params=args.get("params"), timeout=timeout)
    elif name == "taxon_lookup":
        result = taxon_lookup(name=args.get("name"), taxon_no=args.get("taxon_no"), show=args.get("show"), timeout=timeout)
    elif name == "occurrences_search":
        result = occurrences_search(
            base_name=args.get("base_name"),
            taxon_name=args.get("taxon_name"),
            interval=args.get("interval"),
            country=args.get("country"),
            state=args.get("state"),
            limit=args.get("limit", 50),
            show=args.get("show", "coords,attr"),
            timeout=timeout,
        )
    elif name == "collections_search":
        result = collections_search(
            base_name=args.get("base_name"),
            taxon_name=args.get("taxon_name"),
            interval=args.get("interval"),
            country=args.get("country"),
            state=args.get("state"),
            limit=args.get("limit", 50),
            show=args.get("show", "loc,time,strat,ref"),
            timeout=timeout,
        )
    elif name == "references_search":
        result = references_search(
            ref_id=args.get("ref_id"),
            ref_match=args.get("ref_match"),
            ref_author=args.get("ref_author"),
            ref_title=args.get("ref_title"),
            ref_doi=args.get("ref_doi"),
            pub_title=args.get("pub_title"),
            all_records=args.get("all_records"),
            limit=args.get("limit", 50),
            show=args.get("show", "attr"),
            timeout=timeout,
        )
    elif name == "intervals_search":
        result = intervals_search(name=args.get("name"), limit=args.get("limit", 50), timeout=timeout)
    elif name == "strata_search":
        result = strata_search(name=args.get("name"), interval=args.get("interval"), limit=args.get("limit", 50), timeout=timeout)
    else:
        raise KeyError(name)

    return pretty_result(result)


def main() -> int:
    while True:
        message = _read_message()
        if message is None:
            return 0

        method = message.get("method")
        msg_id = message.get("id")

        try:
            if method == "initialize":
                _write_message(
                    _ok(
                        msg_id,
                        {
                            "protocolVersion": PROTOCOL_VERSION,
                            "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
                            "capabilities": {"tools": {}},
                        },
                    )
                )
            elif method == "initialized":
                continue
            elif method == "tools/list":
                _write_message(_ok(msg_id, {"tools": _tool_schema()}))
            elif method == "tools/call":
                params = message.get("params") or {}
                tool_name = params.get("name")
                tool_args = params.get("arguments") or {}
                text = _call_tool(tool_name, tool_args)
                _write_message(
                    _ok(
                        msg_id,
                        {
                            "content": [{"type": "text", "text": text}],
                            "isError": False,
                        },
                    )
                )
            elif method in {"ping"}:
                _write_message(_ok(msg_id, {}))
            elif msg_id is not None:
                _write_message(_error(msg_id, -32601, f"Unknown method: {method}"))
        except Exception as exc:  # noqa: BLE001
            if msg_id is not None:
                _write_message(_error(msg_id, -32000, str(exc)))
            else:
                print(f"[pbdb-mcp] {exc}", file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
