# pbdb-mcp

[English](README.md)

`pbdb-mcp` 是一个面向 Paleobiology Database Data Service v1.2 的轻量 MCP server 和命令行工具。

它可以把 PBDB 的化石数据暴露为 agent 可调用的工具，用于古生物研究、化石记录核查、分类单元查询、地质年代查询、地层单位查询和参考文献追溯。

PBDB 官方文档：<https://paleobiodb.org/data>

## 功能

- 运行时不依赖第三方 Python 包，只使用 Python 标准库。
- 提供 MCP stdio server，可用于 Codex、Claude Desktop 和其他 MCP client。
- 提供 CLI，适合本地 shell 工作流和可复现查询。
- 对 PBDB 常用 API 路径做轻量封装，同时保留 `pbdb_request` 作为通用请求入口。

## 安装

从本地仓库安装：

```bash
pip install -e .
```

启动 MCP server：

```bash
pbdb-mcp
```

使用 CLI：

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

## MCP 配置

Codex / Claude 风格的 stdio 配置示例：

```toml
[mcp_servers.pbdb]
command = "python3"
args = ["-m", "pbdb_mcp.server"]
startup_timeout_sec = 10.0
```

如果使用 editable checkout，但还没有安装包，可以直接指向脚本：

```toml
[mcp_servers.pbdb]
command = "python3"
args = ["/path/to/pbdb-mcp/src/pbdb_mcp/server.py"]
startup_timeout_sec = 10.0
```

直接运行脚本时，请确保 `src` 在 `PYTHONPATH` 中，或者先安装本包。

## MCP 工具

默认情况下，MCP server 暴露 10 个分组后的精简工具：

- `pbdb_request`：调用 `https://paleobiodb.org/data1.2/` 下任意 PBDB API 路径。
- `taxon_tool`：分类单元查询、分类名搜索和自动补全。
- `occurrence_tool`：occurrence 查询，以及 occurrence 派生的分类、参考文献、地层和地理汇总。
- `collection_tool`：collection 查询和 collection 地理汇总。
- `specimen_tool`：标本查询。
- `reference_tool`：参考文献查询、文献关联记录和文献证据包。
- `taxonomy_tool`：分类意见和分类争议报告。
- `geology_tool`：地质年代和地层单位查询。
- `context_pack`：分类单元、比较、地质年代、地区和证据质量组合包。
- `pack_output_tool`：对已有 evidence pack 生成 bibliography、validation 和 Markdown summary。

细粒度 legacy MCP 工具仍然保留用于兼容。启动 MCP server 前设置 `PBDB_MCP_TOOL_MODE=full` 可以暴露全部 legacy 工具：

```bash
PBDB_MCP_TOOL_MODE=full pbdb-mcp
```

CLI 不受 MCP tool mode 影响，仍保留全部细粒度命令。

## 组合工作流工具

组合工具是通用研究工作流，不是面向特定内容平台的写作工具：

- 比较研究：用 `taxa_compare_pack` 在相同采样上限下比较多个分类单元。
- 地质背景：用 `interval_context_pack` 查看某个地质年代在 PBDB 中的记录背景。
- 地区与地层背景：用 `locality_context_pack` 检查地区、州/省、地质年代、分类单元或地层相关记录。
- 证据审查：用 `evidence_quality_report` 提示样本量偏低、参考文献稀疏、年代范围过宽、坐标覆盖不足和分类意见需要复核等问题。

每个组合结果都会保留来源查询 URL，方便下游研究笔记、论文、报告或内容工作流复现 PBDB 查询。

## 可复现研究输出

组合 evidence pack 会包含顶层 `manifest`，其中记录：

- 包名和版本
- PBDB base URL
- workflow 名称
- 原始输入
- 生成时间
- 每条查询的 URL、endpoint、解析后的参数和记录数

可以使用本地输出工具处理已有 evidence pack；这些工具不会再次请求 PBDB：

- `bibliography_pack` / `pbdb bibliography`：抽取参考文献元数据。
- `pack_validation_report` / `pbdb validate-pack`：检查 manifest、query URL、evidence records、references 和 age-range 覆盖。
- `research_summary_markdown` / `pbdb markdown-summary`：生成包含 scope、validation、references、reproducible queries 和 caveats 的通用 Markdown 摘要。

## 研究注意事项

PBDB 是一个持续更新的科学数据库。为了保证研究可复现，应保存每个结论对应的 API 路径和查询参数。

Occurrence 数量代表数据库中的化石记录数量，不等于古生物在真实历史中的丰度。基于 PBDB 数据做重要判断时，应通过 `rid` / `ref_id` 追溯到来源参考文献。

`refs/list.json` 不能直接接受 `base_name`。如果要找某个分类单元背后的参考文献，应先查询 occurrences 或 collections，收集 `rid`，再用 `references --ref-id` 查询文献详情。

按类群追文献时优先使用 `occs_refs`。按文献反查证据链时，使用 `associated_by_reference` 并设置 `record_type=all`。

组合研究工具输出的是结构化 JSON 证据包，不直接生成面向公众的文案。解释、不确定性处理和面向特定受众的转译应放在单独的编辑层。

开源包本身聚焦 PBDB 数据访问、证据追溯、比较背景和证据质量评估。项目专用的编辑、选题或平台化工作流应放在本仓库之外。

## 开发

运行测试：

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

运行一次真实 PBDB smoke test：

```bash
python3 -m pbdb_mcp.cli taxon --name Tyrannosaurus --show attr
```
