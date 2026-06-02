# pbdb-mcp

[中文说明](README.zh-CN.md)

`pbdb-mcp` is a lightweight Model Context Protocol server and CLI for the Paleobiology Database Data Service v1.2.

It exposes PBDB fossil data as agent-callable tools for paleontology research, fossil occurrence checks, taxon lookup, geological intervals, stratigraphic units, and reference tracing.

PBDB official documentation: <https://paleobiodb.org/data>

## Features

- No runtime dependencies beyond Python standard library.
- MCP stdio server for Codex, Claude Desktop, and other MCP clients.
- CLI for local shell workflows and reproducible queries.
- Thin wrappers over PBDB API paths, plus an escape-hatch `pbdb_request` tool.

## Install

From a local checkout:

```bash
pip install -e .
```

Run the MCP server:

```bash
pbdb-mcp
```

Run the CLI:

```bash
pbdb taxon --name Tyrannosaurus --show attr
pbdb taxa --base-name Tyrannosaurus --limit 3
pbdb taxa-opinions --base-name Tyrannosaurus --limit 3
pbdb occurrences --base-name Tyrannosaurus --limit 10 --show coords,attr
pbdb occs-taxa --base-name Tyrannosaurus --limit 10 --show attr
pbdb occs-refs --base-name Tyrannosaurus --limit 10 --show attr
pbdb occs-strata --base-name Tyrannosaurus --limit 10
pbdb geo-summary --record-type occs --base-name Tyrannosaurus --level 2
pbdb collections --base-name Tyrannosaurus --limit 10
pbdb specimens --base-name Tyrannosaurus --limit 10
pbdb references --ref-id 4205 --show attr
pbdb associated --ref-id 4205 --record-type all
pbdb auto --name Tyranno --limit 5
pbdb request taxa/single.json --param name=Tyrannosaurus --param show=attr
```

## MCP Configuration

Example Codex/Claude-style stdio configuration:

```toml
[mcp_servers.pbdb]
command = "python3"
args = ["-m", "pbdb_mcp.server"]
startup_timeout_sec = 10.0
```

If using an editable checkout without installing it first:

```toml
[mcp_servers.pbdb]
command = "python3"
args = ["/path/to/pbdb-mcp/src/pbdb_mcp/server.py"]
startup_timeout_sec = 10.0
```

For direct script execution, ensure `src` is on `PYTHONPATH` or install the package.

## MCP Tools

- `pbdb_request`: call an arbitrary PBDB API path under `https://paleobiodb.org/data1.2/`.
- `taxon_lookup`: look up a taxon by `name` or `taxon_no`.
- `taxa_search`: search taxonomic names by base name, taxon name, identifier, or rank.
- `taxa_opinions`: return taxonomic opinions attached to a selected taxon.
- `opinions_search`: search taxonomic opinions by identifier, author, publication year, or recent changes.
- `occurrences_search`: search fossil occurrences by taxon, interval, country, or state.
- `occs_taxa_summary`: summarize the taxonomic hierarchy represented by a selected set of occurrences.
- `occs_refs`: return references associated with a selected set of occurrences.
- `occs_strata_summary`: summarize strata associated with selected occurrences.
- `geo_summary`: return geographic cluster summaries for selected occurrences or collections.
- `collections_search`: search fossil collections by taxon, interval, country, or state.
- `specimens_search`: search PBDB fossil specimens by taxon, interval, or geography.
- `references_search`: search references by `ref_id`, author, title, DOI, publication title, or match text.
- `intervals_search`: search geological intervals.
- `strata_search`: search stratigraphic units.
- `combined_auto`: autocomplete names across PBDB record types.
- `associated_by_reference`: return taxa, opinions, and/or collections associated with a PBDB reference.

## Research Notes

PBDB is a live scientific database. For reproducible research, save the API path and query parameters used for every conclusion.

Occurrence counts are records in the fossil database, not direct measures of historical abundance. For claims based on PBDB data, trace important records through `rid` / `ref_id` to source references.

`refs/list.json` does not accept `base_name` directly. To find references behind a taxon-based claim, first query occurrences or collections, collect `rid`, then query `references --ref-id`.

For taxon-based reference tracing, prefer `occs_refs` first. For reference-based evidence tracing, use `associated_by_reference` with `record_type=all`.

## Development

Run tests:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Run a quick live smoke test:

```bash
python3 -m pbdb_mcp.cli taxon --name Tyrannosaurus --show attr
```
