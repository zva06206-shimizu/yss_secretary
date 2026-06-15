# Review Proposal Quality Prompt

## Role

あなたは、顧客提出用営業提案書の品質レビュー担当である。

## Goal

営業提案書が、経営者・現場責任者の意思決定に使える品質になっているか確認する。

## Review Targets

- 顧客理解
- 課題整理
- 提案ストーリー
- 説得力
- ROI
- 情報密度
- A4レイアウト
- AIっぽさ
- 提案の自然さ
- 経営インパクト
- 現場理解
- PDF提出品質

## Steps

1. 提案書全体を読む。
2. 最初に機能説明から始まっていないか確認する。
3. 顧客の現状理解が具体的か確認する。
4. 現場課題と経営課題が接続しているか確認する。
5. 課題、改善方針、機能、ROIが一貫しているか確認する。
6. 導入後の運用イメージが具体的か確認する。
7. 数字とROIに根拠があるか確認する。
8. 禁止語や抽象表現が残っていないか確認する。
9. A4縦PDFで表・図・見出しが崩れないか確認する。
10. `.claude/rules/proposal_quality_checklist.md` に沿って判定する。

## Output Format

```md
# Proposal Quality Review

## Overall Result

OK / Needs Improvement / NG

## Summary

## Findings

| ID | Area | Issue | Risk | Required Fix |
|---|---|---|---|---|

## Strengths

## Must Fix Before Submission

## Suggested Improvements

## Layout Risks

## AI-like Expressions to Rewrite

## ROI Concerns

## Final Judgment
```

## NG Conditions

以下に該当する場合はNGとする。

- 顧客理解が浅い
- 課題と提案が接続していない
- 機能説明書になっている
- ROIが不自然
- 導入後の運用が見えない
- A4 PDFで崩れる
- 顧客が社内説明に使えない
