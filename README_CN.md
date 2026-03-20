<p align="right">
  <a href="README.md">🇬🇧 English</a>
</p>

# shuck-file

[![PyPI](https://img.shields.io/pypi/v/shuck-file)](https://pypi.org/project/shuck-file/)
[![MCP Registry](https://img.shields.io/badge/MCP_Registry-available-blue)](https://registry.modelcontextprotocol.io/servers/io.github.Shan-Zhu%2Fshuck-file)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Any file in, Markdown out — read only what matters.

**shuck-file** 将文档转换为干净的 Markdown，专为 AI agent 和大语言模型设计。小文件直接输出完整内容；大文件自动返回**文档地图**，包含章节摘要、token 估算和可操作的下一步建议——让 agent 按需提取，节省上下文窗口。

## 为什么选 shuck-file？

AI agent 需要一个**感知上下文**的桥梁：

- **小文件** → `shuck report.docx` → 直接输出完整 Markdown
- **大文件** → `shuck report.docx` → 返回文档地图，附带章节和提取选择
- **定向提取** → `shuck report.docx --sections s1,s3` → 只提取需要的关键部分
- **搜索** → `shuck report.docx --grep "revenue"` → 不读全文也能搜索

## 支持格式

| 格式 | 扩展名 | 依赖库 | 保留内容 |
|------|--------|--------|---------|
| Word | `.docx` | python-docx | 标题、粗斜体、列表、表格 |
| PDF | `.pdf` | pdfplumber | 文本内容、分页 |
| Excel | `.xlsx` | openpyxl | 所有工作表转为 Markdown 表格 |
| PowerPoint | `.pptx` | python-pptx | 标题、文本、表格、备注 |
| CSV | `.csv` | 标准库 | 所有行列转为表格 |

## 快速开始

```bash
pip install shuck-file
shuck report.docx
```

## 使用方法

### 自动路由（默认）

小文件直接输出，大文件返回文档地图。

```bash
# 小文件 → 直接输出 Markdown
shuck document.pdf

# 大文件 → 文档地图 + 下一步建议
shuck large-report.pdf
```

### 提取选项

```bash
# 强制完整输出（跳过地图模式）
shuck report.pdf --all

# 提取指定章节
shuck report.pdf --sections s1,s3

# 仅提取表格
shuck report.pdf --tables-only

# 文档内搜索
shuck report.pdf --grep "revenue"

# Token 预算（智能压缩）
shuck report.pdf --budget 4000

# 可组合使用
shuck report.pdf --sections s2,s3 --budget 2000
```

### Excel/CSV 专用

```bash
# 列名 + 类型
shuck data.xlsx --schema-only

# 列名 + 前 N 行预览
shuck data.xlsx --sample 5
```

### 高级子命令

```bash
# 强制地图模式（即使是小文件）
shuck probe document.docx

# 强制完整提取（等同 --all）
shuck pull document.docx
```

### 输出控制

```bash
# 写入文件
shuck document.pdf -o output.md

# 写入目录（自动命名）
shuck document.pdf -d ./converted/

# 跳过 YAML 头信息
shuck document.pdf --no-frontmatter

# 列出支持的格式
shuck --formats
```

### 地图模式输出

当文件较大时，shuck 返回一张文档地图：

```markdown
# Document Map: quarterly-report.pdf

**6 pages | ~12,400 tokens | 6 sections**

## Sections

| # | Title | Type | Tokens | Density |
|---|-------|------|--------|---------|
| s1 | Executive Summary | narrative | 450 | high |
| s2 | Q3 Financial Results | mixed | 2,800 | high |
| s3 | Revenue Breakdown | tabular | 3,200 | high |
| ...

## Next Steps

- `shuck quarterly-report.pdf --all` -- 完整文档 (~12,400 tokens)
- `shuck quarterly-report.pdf --sections s1,s2` -- 高密度章节 (~3,250 tokens)
- `shuck quarterly-report.pdf --grep "..."` -- 搜索关键词
```

### Claude Code 插件

安装为 Claude Code 插件后，使用 `/shuck` 命令：

```
/shuck path/to/document.xlsx
```

当你在对话中引用支持的文档格式时，技能会自动触发。

## 安装

### pip（推荐）

```bash
pip install shuck-file
```

安装后同时提供 `shuck` CLI 命令和 MCP Server。

### MCP Server

安装后，在任意支持 MCP 协议的 AI 工具中配置：

**Claude Code**

```bash
claude mcp add shuck-file -- shuck-file
```

**Cursor / Windsurf / 其他 MCP 客户端**

在 MCP 配置文件中添加：

```json
{
  "mcpServers": {
    "shuck-file": {
      "command": "shuck-file",
      "args": []
    }
  }
}
```

也可以直接在 [MCP Registry](https://registry.modelcontextprotocol.io/servers/io.github.Shan-Zhu%2Fshuck-file) 一键安装。

### Claude Code 插件

```bash
claude plugin add /path/to/shuck-file
```

### 源码安装

```bash
git clone https://github.com/Shan-Zhu/shuck-file.git
cd shuck-file
pip install -e .
```

## 架构

```
src/shuck_file/
├── cli.py                # CLI 入口
├── server.py             # MCP Server（FastMCP）
├── core/
│   ├── router.py          # 自动路由逻辑
│   ├── segmenter.py       # 文档分段
│   ├── mapper.py          # 地图模式渲染
│   ├── budget.py          # 智能压缩
│   ├── grep.py            # 文档内搜索
│   ├── frontmatter.py     # YAML 头信息
│   └── models.py          # 数据模型
├── extractors/
│   ├── base.py            # 提取器基类
│   ├── docx_ext.py        # Word 提取器
│   ├── pdf_ext.py         # PDF 提取器
│   ├── xlsx_ext.py        # Excel 提取器
│   ├── pptx_ext.py        # PowerPoint 提取器
│   └── csv_ext.py         # CSV 提取器
plugin/                    # Claude Code 插件包装层
tests/                     # 39 项测试
```

## 许可证

MIT
