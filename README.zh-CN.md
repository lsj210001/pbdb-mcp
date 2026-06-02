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
pbdb occurrences --base-name Tyrannosaurus --limit 10 --show coords,attr
pbdb collections --base-name Tyrannosaurus --limit 10
pbdb references --ref-id 4205 --show attr
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

- `pbdb_request`：调用 `https://paleobiodb.org/data1.2/` 下任意 PBDB API 路径。
- `taxon_lookup`：按 `name` 或 `taxon_no` 查询分类单元。
- `occurrences_search`：按分类单元、地质年代、国家或州/省查询化石 occurrence。
- `collections_search`：按分类单元、地质年代、国家或州/省查询 fossil collection。
- `references_search`：按 `ref_id`、作者、标题、DOI、出版物标题或匹配文本查询参考文献。
- `intervals_search`：查询地质年代区间。
- `strata_search`：查询地层单位。

## 研究注意事项

PBDB 是一个持续更新的科学数据库。为了保证研究可复现，应保存每个结论对应的 API 路径和查询参数。

Occurrence 数量代表数据库中的化石记录数量，不等于古生物在真实历史中的丰度。基于 PBDB 数据做重要判断时，应通过 `rid` / `ref_id` 追溯到来源参考文献。

`refs/list.json` 不能直接接受 `base_name`。如果要找某个分类单元背后的参考文献，应先查询 occurrences 或 collections，收集 `rid`，再用 `references --ref-id` 查询文献详情。

## 开发

运行测试：

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

运行一次真实 PBDB smoke test：

```bash
python3 -m pbdb_mcp.cli taxon --name Tyrannosaurus --show attr
```
