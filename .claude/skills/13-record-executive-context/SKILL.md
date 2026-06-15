# Record Executive Context Skill

## Purpose

経営相談、会社情報、従業員情報、経営状況、顧客文脈をリポジトリ内に記録し、Claude Codeを経営者の右腕として強化する。

## When to Use

- 経営相談を受けたとき
- 会社の事業内容が更新されたとき
- 従業員や役割に変更があったとき
- 経営KPIや課題が共有されたとき
- 顧客や案件の重要な文脈が増えたとき
- 提案方針や判断軸が明確になったとき

## Inputs

- ユーザーの相談内容
- 会社情報
- 従業員・組織情報
- KPI・経営数値
- 顧客情報
- 案件情報
- 過去の提案・判断

## Steps

1. 情報を、事実、仮説、未確認に分ける。
2. 会社全体に関わる内容は `data/memory/company/` に記録する。
3. 経営者の判断軸は `data/memory/decision-principles.md` に反映する。
4. 経営相談は `data/memory/consultations/` に記録する。
5. 意思決定は `data/memory/decisions/` に記録する。
6. 顧客別の長期文脈は `data/memory/clients/` に分ける。
7. 案件に属する情報は `work/{project}/00_context/` に記録する。
8. KPIは `data/memory/company/management-kpi.md` または `work/{project}/01_business/kpi.md` に反映する。
9. 課題は `data/memory/company/current-issues.md` または `work/{project}/01_business/issues.md` に反映する。
10. 戦略や重点施策は `data/memory/company/strategy-roadmap.md` に反映する。
11. 必要に応じて `data/templates/`、`data/knowledge/`、`work/{project}/` にも反映する。

## Output

```md
# Executive Context Recording Result

## Recorded Facts

## Recorded Hypotheses

## Unknowns

## Updated Files

## Decisions

## Action Items

## Next Review Timing
```

## Quality Bar

- 経営相談を単なる会話ログで終わらせない。
- 次回の提案、設計、営業判断に使える形で保存する。
- 個人情報は必要最小限にする。
- 古い情報と新しい情報が混ざらないよう更新日を残す。
