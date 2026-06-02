# Changelog

All notable changes to `pbdb-mcp` are documented here.

## v0.6.0 - Compact MCP Tool Surface

Released: 2026-06-02

### Added

- Added compact default MCP tool surface with 10 grouped tools:
  - `pbdb_request`
  - `taxon_tool`
  - `occurrence_tool`
  - `collection_tool`
  - `specimen_tool`
  - `reference_tool`
  - `taxonomy_tool`
  - `geology_tool`
  - `context_pack`
  - `pack_output_tool`
- Added `PBDB_MCP_TOOL_MODE=full` compatibility mode to expose all legacy fine-grained MCP tools.

### Changed

- Default MCP `tools/list` now returns compact grouped tools instead of all fine-grained tools.
- CLI commands remain fine-grained and unchanged.
- Package version, server version, research manifest version, and user agent updated to `0.6.0`.

### Compatibility

- Legacy MCP tools are still available with `PBDB_MCP_TOOL_MODE=full`.
- Default compact mode is intended for day-to-day agent use.
- Full mode is intended for compatibility, debugging, and exact legacy workflows.

### Verified

- 23 unit tests passed.
- Python compile check passed.
- Default MCP stdio smoke test returned 10 tools and successfully called `taxon_tool`.
- Full-mode MCP stdio smoke test returned 27 tools and successfully called legacy `taxon_lookup`.
- Public repository scan found no sensitive-keyword or platform-specific content matches.

## v0.5.0 - Reproducible Research Outputs

Released: 2026-06-02

### Added

- Added top-level `manifest` to composite evidence packs, recording:
  - package name and version
  - PBDB base URL
  - workflow name
  - original input
  - generated timestamp
  - query URL, endpoint, parsed parameters, and record count for each PBDB query
- Added `bibliography_pack` for extracting structured reference metadata from an existing evidence pack.
- Added `pack_validation_report` for checking reproducibility metadata and source coverage.
- Added `research_summary_markdown` for rendering generic Markdown research summaries.
- Added CLI commands:
  - `pbdb bibliography`
  - `pbdb validate-pack`
  - `pbdb markdown-summary`

### Changed

- Composite tools now preserve richer reproducibility metadata while keeping existing evidence fields.
- Bibliography extraction only treats real reference metadata records as bibliography entries.

### Verified

- 22 unit tests passed.
- Python compile check passed.
- Real PBDB CLI smoke test generated a `0.5.0` manifest and processed it with bibliography, validation, and Markdown output commands.
- MCP stdio smoke test returned 27 tools and successfully called output tools.
- Public repository scan found no sensitive-keyword or platform-specific content matches.

## v0.4.0 - Neutral Research Workflow Packs

Released: 2026-06-02

### Added

- Added `taxa_compare_pack` for comparing 2-5 taxa using sampled PBDB evidence.
- Added `interval_context_pack` for geological interval context.
- Added `locality_context_pack` for locality, region, taxon-filtered, or stratum context.
- Added `evidence_quality_report` for sampled evidence-quality assessment.

### Changed

- Kept composite workflows platform-neutral and focused on PBDB research infrastructure.
- Updated English and Chinese documentation with workflow examples and boundaries.
- Clarified that project-specific editorial workflows should live outside this repository.
- Corrected `strata_search` behavior: it searches strata by name; use `occs_strata_summary` for interval-scoped strata summaries.

### Verified

- 18 unit tests passed.
- Python compile check passed.
- Real PBDB CLI smoke test covered `compare-pack`, `interval-pack`, `locality-pack`, and `quality-report`.
- MCP stdio smoke test returned 24 tools and successfully called `evidence_quality_report`.
- Public repository scan found no platform-specific content matches.

## v0.3.0 - Composite Research Evidence Packs

Released: 2026-06-02

### Added

- Added `taxon_fact_card` for multi-query taxon evidence cards.
- Added `reference_evidence_pack` for reference-centered evidence tracing.
- Added `taxonomy_dispute_report` for taxonomic opinion and dispute-boundary reporting.
- Added `src/pbdb_mcp/research.py` for composite research workflows.

### Changed

- Composite tools return structured JSON evidence packs rather than public-facing prose.
- Each composite workflow preserves query URLs for reproducibility.
- Documentation clarified that interpretation and audience-specific rewriting belong outside the data layer.

### Verified

- 13 unit tests passed.
- Python compile check passed.
- Real PBDB smoke tests covered fact cards, reference packs, and dispute reports.
- MCP stdio smoke test returned 20 tools and successfully called `reference_evidence_pack`.

## v0.2.0 - PBDB Evidence Chain Tools

Released: 2026-06-02

### Added

- Added evidence-chain API wrappers:
  - `taxa_search`
  - `taxa_opinions`
  - `opinions_search`
  - `occs_taxa_summary`
  - `occs_refs`
  - `occs_strata_summary`
  - `geo_summary`
  - `specimens_search`
  - `combined_auto`
  - `associated_by_reference`

### Changed

- Expanded MCP tool surface from basic PBDB lookup to evidence tracing across taxa, occurrences, strata, geography, specimens, references, and reference-associated records.
- Documentation added guidance for tracing references through occurrences and collections.

### Verified

- 10 unit tests passed.
- Real PBDB smoke tests covered taxa, taxonomic opinions, occurrence references, specimens, geography summary, associated records, and autocomplete.
- MCP stdio smoke test returned 17 tools and successfully called `combined_auto`.
