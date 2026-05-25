# CucurLitBase Skills

这个仓库整理了用于访问和分析 CucurLitBase 的 Codex skills。当前版本面向两个核心需求：稳定查询数据库 API，以及生成研究者可读的深度文献证据报告。

## 包含的 skills

- `cucurlitbase-api`: 查询 CucurLitBase REST API，支持物种、性状、基因、PMID 列表，以及基因、物种、性状、PMID 的单条件或双条件检索。
- `cucurlitbase-report`: 将 API 查询结果整理为固定格式的用户报告。
- `cucurlitbase-gene-report`: 面向某物种某基因生成深度调研报告，包含 PubMed 期刊/年份/标题补充、证据表、机制分类、证据强度、图表、DOCX 渲染、同表型相关基因比较、句子级机制链和外源数据库拓展规范。

## 安装方式

将 `skills/` 下的 skill 文件夹复制到本机 Codex skills 目录：

```powershell
Copy-Item -Recurse -Force .\skills\cucurlitbase-api C:\Users\<your-user>\.codex\skills\
Copy-Item -Recurse -Force .\skills\cucurlitbase-report C:\Users\<your-user>\.codex\skills\
Copy-Item -Recurse -Force .\skills\cucurlitbase-gene-report C:\Users\<your-user>\.codex\skills\
```

也可以直接解压发布包：

```text
dist/cucurlitbase-skills-20260525.zip
```

## 基础使用示例

查询支持的物种：

```bash
python skills/cucurlitbase-api/scripts/query_cucurlitbase.py list species
```

查询西瓜中某基因的证据：

```bash
python skills/cucurlitbase-api/scripts/query_cucurlitbase.py search --species Watermelon --gene PAL --output report --limit 10
```

生成单基因深度报告：

```bash
python skills/cucurlitbase-gene-report/scripts/build_gene_report.py --species Watermelon --gene PAL --output-dir outputs/watermelon_pal_deep --limit -1
```

生成带同表型相关基因背景的深度报告：

```bash
python skills/cucurlitbase-gene-report/scripts/build_gene_report.py --species Watermelon --gene PAL --output-dir outputs/watermelon_pal_deep --limit -1 --include-trait-peer-genes
```

渲染最终 DOCX：

```bash
python skills/cucurlitbase-gene-report/scripts/render_markdown_docx.py --markdown outputs/watermelon_pal_deep/final_report.md --output-docx outputs/watermelon_pal_deep/final_report.docx
```

运行质量检查：

```bash
python skills/cucurlitbase-gene-report/scripts/check_gene_report_quality.py --report-md outputs/watermelon_pal_deep/final_report.md --evidence-json outputs/watermelon_pal_deep/data/evidence_enriched.json
```

## 深度报告能力

`cucurlitbase-gene-report` 当前要求报告具备：

- 中文学术标题和多级章节结构。
- Evidence Table 中保留原文、中文翻译、论文标题、期刊、年份、PMID、机制分类、证据强度和机制链。
- 图表编号与题注，例如 `Fig. 1.`，并在正文中引用。
- 性状分布、机制分布、证据强度、年代折线、性状-机制热图、性状-证据强度热图、PMID-性状矩阵。
- 同表型下其他基因的比较背景。
- 数据不足时，按规范补充 UniProt/Swiss-Prot、NCBI 等外源数据库信息；GeneCards 不作为默认自动化来源。
- 句子级机制推理链，例如 `Gene -> evidence event -> mechanism context -> trait`。

## 注意事项

- CucurLitBase 是核心证据源，外源数据库只能作为补充，不能替代文献证据。
- 机制分类和机制链是初筛结果，正式报告中必须结合原文句子和论文方法复核。
- BFT 树只在获得真实层级数据时绘制，不能根据 trait 名称自行推断层级。
- 低证据场景下应降低结论强度，不应扩写成无法支撑的机制结论。
