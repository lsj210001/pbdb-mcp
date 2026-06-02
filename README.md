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
pbdb fact-card --name Tyrannosaurus --limit 3
pbdb reference-pack --ref-id 4205
pbdb dispute-report --name Tyrannosaurus --limit 5
pbdb compare-pack --name Tyrannosaurus --name Triceratops --limit 2
pbdb interval-pack --interval "Late Cretaceous" --limit 5
pbdb locality-pack --country US --state Montana --interval "Late Cretaceous" --limit 5
pbdb quality-report --name Tyrannosaurus --limit 10
pbdb fact-card --name Tyrannosaurus --limit 3 > tyrannosaurus-pack.json
pbdb bibliography --input tyrannosaurus-pack.json
pbdb validate-pack --input tyrannosaurus-pack.json
pbdb markdown-summary --input tyrannosaurus-pack.json --title "Tyrannosaurus PBDB Summary"
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

By default, the MCP server exposes a compact tool surface with 10 grouped tools:

- `pbdb_request`: call an arbitrary PBDB API path under `https://paleobiodb.org/data1.2/`.
- `taxon_tool`: taxon lookup, taxonomic-name search, and autocomplete.
- `occurrence_tool`: occurrence search plus occurrence-derived taxa, reference, strata, and geography summaries.
- `collection_tool`: collection search and collection geography summaries.
- `specimen_tool`: specimen search.
- `reference_tool`: reference search, reference-associated records, and reference evidence packs.
- `taxonomy_tool`: taxonomic opinions and taxonomic dispute reports.
- `geology_tool`: geological interval and stratigraphic-unit lookups.
- `context_pack`: composite taxon, comparison, interval, locality, and evidence-quality packs.
- `pack_output_tool`: bibliography, validation, and Markdown rendering for existing evidence packs.

The fine-grained legacy MCP tools are still available for compatibility. Set `PBDB_MCP_TOOL_MODE=full` before starting the MCP server to expose all legacy tools:

```bash
PBDB_MCP_TOOL_MODE=full pbdb-mcp
```

The CLI keeps all fine-grained commands regardless of MCP tool mode.

## Composite Workflow Tools

The composite tools are general research workflows, not platform-specific writing tools:

- Comparative workflows: use `taxa_compare_pack` to compare taxon records under the same sampling limit.
- Geological context workflows: use `interval_context_pack` to understand the PBDB record context around a named interval.
- Locality and stratum workflows: use `locality_context_pack` to inspect regional, state/province, interval, taxon, or stratum-scoped records.
- Evidence review workflows: use `evidence_quality_report` to surface low sample sizes, sparse references, broad age ranges, missing coordinate coverage, and taxonomy-review cautions.

Every composite result preserves source query URLs so downstream research notes, publications, or content workflows can cite and reproduce the PBDB calls.

## Reproducible Research Outputs

Composite evidence packs include a top-level `manifest` with:

- package name and version
- PBDB base URL
- workflow name
- original input
- generated timestamp
- every recorded query URL, endpoint, parsed parameters, and record count

Use local output tools to process an existing evidence pack without making additional PBDB requests:

- `bibliography_pack` / `pbdb bibliography`: extract reference metadata.
- `pack_validation_report` / `pbdb validate-pack`: check manifest, query URLs, evidence records, references, and age-range coverage.
- `research_summary_markdown` / `pbdb markdown-summary`: render a generic Markdown summary with scope, validation, references, reproducible queries, and caveats.

## Research Notes

PBDB is a live scientific database. For reproducible research, save the API path and query parameters used for every conclusion.

Occurrence counts are records in the fossil database, not direct measures of historical abundance. For claims based on PBDB data, trace important records through `rid` / `ref_id` to source references.

`refs/list.json` does not accept `base_name` directly. To find references behind a taxon-based claim, first query occurrences or collections, collect `rid`, then query `references --ref-id`.

For taxon-based reference tracing, prefer `occs_refs` first. For reference-based evidence tracing, use `associated_by_reference` with `record_type=all`.

The composite research tools return structured JSON evidence packs. They do not generate public-facing copy; keep interpretation, uncertainty, and audience-specific rewriting in a separate editorial layer.

The open-source package stays focused on PBDB data access, evidence tracing, comparative context, and evidence-quality assessment. Project-specific editorial workflows should live outside this repository.

## Development

Run tests:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Run a quick live smoke test:

```bash
python3 -m pbdb_mcp.cli taxon --name Tyrannosaurus --show attr
```
