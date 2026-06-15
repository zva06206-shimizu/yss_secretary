# Design Business Data Accumulation Skill

## Purpose

業務システムで蓄積すべきデータを、DB設計、KPI、監査ログ、AI分析、権限、保存期間まで含めて設計する。

## When to Use

- 要件定義後
- DB設計前
- ダッシュボード設計前
- AI分析機能を設計するとき
- 監査ログや操作履歴が必要なとき
- 顧客提出用設計書にデータ活用方針を書くとき

## Inputs

- `work/{project}/03_documents/requirements-definition.md`
- `work/{project}/04_system/design/`
- `work/{project}/04_system/design/database/`
- `work/{project}/06_data/`
- `data/knowledge/rules/business-data-accumulation-rules.md`

## Steps

1. 対象業務を確認する。
2. 発生する業務データを洗い出す。
3. Master / Transaction / Log / KPI / AI Source / Derived に分類する。
4. `work/{project}/06_data/data-inventory.md` を作成・更新する。
5. KPIに使うデータを `work/{project}/06_data/kpi-definition.md` に定義する。
6. 監査が必要な操作を `work/{project}/06_data/audit-log-design.md` に定義する。
7. 入力品質ルールを `work/{project}/06_data/data-quality-rules.md` に記録する。
8. AI分析に使うデータを `work/{project}/06_data/ai-data-design.md` に分離する。
9. 保存期間と権限を `work/{project}/06_data/retention-and-permission.md` に記録する。
10. DB設計、画面設計、テストケースへ反映する。

## Output

```md
# Business Data Accumulation Design Result

## Data Categories

| Category | Count | Notes |
|---|---:|---|

## Required Tables

| Table | Purpose | Source Data | KPI Use | AI Use |
|---|---|---|---|---|

## KPI Candidates

## Audit Log Targets

## Permission / Retention Concerns

## Required Design Updates
```

## Quality Bar

- 画面表示用データだけで終わらせない。
- KPI、監査、AI分析、履歴、権限、保存期間まで確認する。
- AI出力を元データと同じ扱いにしない。
