# Review Maintainability Skill

## Purpose

変更・改修に強い構造になっているかをレビューし、必要な設計・実装・テスト・ドキュメント修正を洗い出す。

## When to Use

- 要件定義完了時
- 画面/機能設計完了時
- Laravel実装前
- 大きな仕様変更前
- DB変更前
- 外部API追加前
- 本番リリース前

## Inputs

- `work/{project}/03_documents/`
- `work/{project}/04_system/design/`
- `work/{project}/04_system/tests/`
- `work/{project}/04_system/app/`
- `data/knowledge/maintainability/quality-gate.md`
- `data/knowledge/rules/maintainability-rule.md`

## Steps

1. 変更対象と変更理由を特定する。
2. 要件ID、画面ID、機能ID、テストIDの追跡可能性を確認する。
3. Controller、Service、Action、Policy、FormRequest、Modelの責務分離を確認する。
4. DB変更の安全性を確認する。
5. 外部サービス依存が局所化されているか確認する。
6. UIが `data/ui/` の共通部品を使っているか確認する。
7. 重要業務フローのテスト有無を確認する。
8. `data/knowledge/maintainability/quality-gate.md` と `data/knowledge/rules/maintainability-rule.md` に沿って判定する。
9. 課題を `work/{project}/99_logs/issue-log.md` に記録する。
10. 必要に応じてADRを追加する。

## Output

```md
## Maintainability Review

- Target Project:
- Review Scope:
- Overall Result: OK / Needs Improvement / NG

### Findings

| ID | Area | Finding | Risk | Required Action |
|---|---|---|---|---|

### Required Updates

- Requirements:
- Design:
- DB:
- API:
- Tests:
- UI:
- ADR:

### Next Action
```

## Quality Bar

実装だけで解決しない。必要なら設計、テスト、DB、UI、ADRまで遡って修正する。
