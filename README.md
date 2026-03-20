# shuck-file

> Feed any document to your AI agent — in one command.
>
> 一条命令，把任何文档喂给你的 AI agent。

**shuck-file** converts documents to clean Markdown for AI agents and LLMs. Small files output directly; large files return a **document map** with section summaries, token counts, and actionable next steps — so agents only pull what they need.

**shuck-file** 将文档转换为干净的 Markdown，专为 AI agent 和大语言模型设计。小文件直接输出完整内容；大文件自动返回**文档地图**，包含章节摘要、token 估算和可操作的下一步建议——让 agent 按需提取，节省上下文窗口。

---

## Why shuck-file? / 为什么选 shuck-file？

AI agents can't read binary documents. They need a bridge that's **context-aware**:

AI agent 无法读取二进制文档，它们需要一个**感知上下文**的桥梁：

- **Small file / 小文件** → `shuck report.docx` → full Markdown on stdout / 直接输出完整 Markdown
- **Large file / 大文件** → `shuck report.docx` → document map with sections and extraction options / 返回文档地图，附带章节和提取选项
- **Targeted extraction / 定向提取** → `shuck report.docx --sections s1,s3` → only what you need / 只提取需要的部��
- **Search / 搜索** → `shuck report.docx --grep "revenue"` → find without reading everything / 不读全文也能搜索

## Supported Formats / 支持格式

| Format / 格式 | Extension / 扩展名 | Library / 依赖库 | What's Preserved / 保留内容 |
|--------|-----------|---------|-----------------|
| Word | `.docx` | python-docx | Headings, bold/italic, lists, tables / 标题、粗斜体、列表、表格 |
| PDF | `.pdf` | pdfplumber | Text content, page breaks / 文本内容、分页 |
| Excel | `.xlsx` | openpyxl | All sheets as Markdown tables / 所有工作表转为表格 |
| PowerPoint | `.pptx` | python-pptx | Titles, text, tables, speaker notes / 标题、文本、表格、备注 |
| CSV | `.csv` | stdlib | All rows/columns as a table / 所有行列转为表格 |

## Quick Start / 快速开始

```bash
git clone https://github.com/Shan-Zhu/shuck-file.git
pip install -r requirements.txt
python plugin/shuck.py report.docx
```

## Usage / 使用方法

### Auto-Routing (default) / 自动路由（默认）

Small files output directly, large files return a document map.

小文件直接输出，大文件返回文档地图。

```bash
# Small file → direct Markdown output / 小文件 → 直接输出 Markdown
shuck document.pdf

# Large file → document map with sections table + next steps / 大文件 → 文档地图 + 下一步建议
shuck large-report.pdf
```

### Extraction Options / 提取选项

```bash
# Force full output (bypass map mode) / 强制完整输出（跳过地图模式）
shuck report.pdf --all

# Extract specific sections / 提取指定章节
shuck report.pdf --sections s1,s3

# Tables only / 仅提取表格
shuck report.pdf --tables-only

# Search within document / 文档内搜索
shuck report.pdf --grep "revenue"

# Token budget (smart compression) / Token 预算（智能压缩）
shuck report.pdf --budget 4000

# Combinations work / 可组合使用
shuck report.pdf --sections s2,s3 --budget 2000
```

### Excel/CSV Specific / Excel/CSV 专用

```bash
# Column headers and types / 列名 + 类型
shuck data.xlsx --schema-only

# Headers + first N rows / 列名 + 前 N 行预览
shuck data.xlsx --sample 5
```

### Power User Subcommands / 高级子命令

```bash
# Force map mode (even on small files) / 强制地图模式（即使是小文件）
shuck probe document.docx

# Force full extraction (alias for --all) / 强制完整提取（等同 --all）
shuck pull document.docx
```

### Output Control / 输出控制

```bash
# Write to file / 写入文件
shuck document.pdf -o output.md

# Write to directory (auto-named) / 写入目录（自动命名）
shuck document.pdf -d ./converted/

# Skip YAML frontmatter / 跳过 YAML 头信息
shuck document.pdf --no-frontmatter

# List supported formats / 列出支持的格式
shuck --formats
```

### Map Mode Output / 地图模式输出

When a file is large, shuck returns a document map:

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

- `shuck quarterly-report.pdf --all` -- full document (~12,400 tokens)
- `shuck quarterly-report.pdf --sections s1,s2` -- high-density (~3,250 tokens)
- `shuck quarterly-report.pdf --grep "..."` -- search for keywords
```

### Claude Code Plugin / Claude Code 插件

Install as a Claude Code plugin, then use `/shuck`:

安装为 Claude Code 插件后，使用 `/shuck` 命令：

```
/shuck path/to/document.xlsx
```

The skill triggers automatically when you reference a supported document format.

当你在对话中引用支持的文档格式时，技能会自动触发。

## Installation / 安装

### As a Claude Code Plugin / 作为 Claude Code 插件

```bash
claude plugin add /path/to/shuck-file
```

### Standalone / 独立使用

```bash
git clone https://github.com/Shan-Zhu/shuck-file.git
cd shuck-file
pip install -r requirements.txt
```

### Minimal Install (by format) / 按格式最小安装

```bash
pip install python-docx      # .docx only / 仅 Word
pip install pdfplumber        # .pdf only / 仅 PDF
pip install openpyxl          # .xlsx only / 仅 Excel
pip install python-pptx       # .pptx only / 仅 PowerPoint
# .csv needs no extra dependencies / CSV 无需额外依赖
```

## Architecture / 架构

```
plugin/
├── shuck.py              # CLI entrypoint / 命令行入口
├── core/
│   ├── router.py          # Auto-routing logic / 自动路由逻辑
│   ├── segmenter.py       # Document segmentation / 文档分段
│   ├── mapper.py          # Map mode renderer / 地图模式渲染
│   ├── budget.py          # Smart compression / 智能压缩
│   ├── grep.py            # In-document search / 文档内搜索
│   ├── frontmatter.py     # YAML frontmatter / YAML 头信息
│   └── models.py          # Data models / 数据模型
├── extractors/
│   ├── base.py            # Base extractor ABC / 提取器基类
│   ├── docx_ext.py        # Word extractor
│   ├── pdf_ext.py         # PDF extractor
│   ├── xlsx_ext.py        # Excel extractor
│   ├── pptx_ext.py        # PowerPoint extractor
│   └── csv_ext.py         # CSV extractor
tests/
├── test_extractors.py     # 39 tests / 39 项测试
├── test_router.py
├── test_segmenter.py
├── test_budget.py
└── test_grep.py
```

## License / 许可证

MIT
