# Convert Proposal to PDF Prompt

## Role

あなたは、営業提案書をA4縦PDFとして顧客提出できる品質に整える担当である。

## Goal

MarkdownまたはHTMLで作成した営業提案書を、A4縦PDFとして崩れなく出力する。

## Required Files

- Proposal Markdown or HTML
- `.claude/assets/proposal_print.css`
- `.claude/rules/a4_pdf_layout_rules.md`
- `.claude/rules/proposal_quality_checklist.md`

## Steps

1. 提案書Markdownを確認する。
2. 見出し、表、図、注記、カードの構造を確認する。
3. MarkdownをHTML化する。
4. `proposal_print.css` を適用する。
5. PDFを生成する。
6. 印刷プレビューを確認する。
7. 見出し孤立、表の横はみ出し、表・図の分断を確認する。
8. 問題があればHTMLまたはCSSを修正する。
9. 再度PDFを生成する。
10. 最終PDFを `outputs/proposals/{project}/` に保存する。
11. 修正ログを残す。

## Layout Checks

- A4縦になっているか
- 表紙が独立しているか
- 目次が読みやすいか
- 章ごとに自然に改ページされているか
- 表が横にはみ出していないか
- 図が途中で切れていないか
- KPIカードが分断されていないか
- Before / Afterが読みやすいか
- ROI表が小さすぎないか

## Output

```md
# PDF Conversion Result

- Source:
- CSS:
- Output PDF:
- Layout Issues:
- Fixes Applied:
- Final Status:
```
