# Review PR Quality Skill

## Purpose

Claude Codeが実装変更、リファクタ、ドキュメント変更、テンプレート追加を行った後に、PR相当の品質レビューを行う。

レビューでは、変更を小さく保つこと、差分の目的を明確にすること、blocking / should-fix / nit を分けることを重視する。

## When to Use

- コード変更後
- `.claude/`, `work/`, `data/` の構造変更後
- Git commit前
- 顧客提出物に関わるテンプレート変更後
- GitHub ActionsやHook変更後
- 複数ファイルを変更した後
- 変更が大きくなりすぎた可能性があるとき

## Must Read

- `data/knowledge/references/engineering-practices/README.md`
- `data/knowledge/rules/maintainability-rule.md`
- `data/knowledge/rules/token-optimization-rules.md`
- 変更対象ファイルのみ

## Do Not Read By Default

- 関係ない案件フォルダ
- 全テンプレート
- 全ログ
- 全白書
- 全Git履歴

## Review Principles

1. 変更目的を一文で説明できるか確認する。
2. 1つの変更に複数目的が混ざっていないか確認する。
3. 機能追加とリファクタを混ぜていないか確認する。
4. 差分が大きすぎる場合は分割を提案する。
5. 変更に対して必要なテスト・検証があるか確認する。
6. 構成方針 `.claude / work / data` と矛盾していないか確認する。
7. レビューコメントは blocking / should-fix / nit に分ける。

## Severity Definition

| Severity | Meaning | Action |
|---|---|---|
| blocking | このまま完了・提出・merge扱いにできない | 必ず修正 |
| should-fix | 今回直すべきだが、状況により後続対応も可 | 原則修正 |
| nit | 軽微な改善・表現・整理 | 任意 |

## Checklist

### Scope

- [ ] 変更目的が明確である
- [ ] 1コミットに複数目的が混ざっていない
- [ ] ファイル移動と内容変更が混在しすぎていない
- [ ] 変更範囲が必要最小限である

### Repository Structure

- [ ] `.claude/` は操作盤として保たれている
- [ ] 案件成果物は `work/` に置かれている
- [ ] 共通知識・記憶・テンプレートは `data/` に置かれている
- [ ] 旧パス参照が増えていない

### Maintainability

- [ ] 変更理由が分かる
- [ ] 影響範囲が分かる
- [ ] 将来の変更に耐えられる
- [ ] 同じ意味のファイルが重複していない

### Safety

- [ ] 機密情報が含まれていない
- [ ] 個人情報の扱いが適切である
- [ ] Hook / Actions が破壊的動作をしない
- [ ] 自動コミットや自動更新が無限ループしない

### Test / Validation

- [ ] CIで確認できる
- [ ] スクリプトは構文チェックできる
- [ ] GitHub Actionsのパスが正しい
- [ ] 参照先ファイルが実在する

### Token Efficiency

- [ ] 不要な全文読み込みを促していない
- [ ] 長文資料は索引・要約優先になっている
- [ ] Agent間Handoffが圧縮形式になっている

## Output Format

```md
# PR Quality Review

## Change Summary

## Overall Result

OK / Needs Improvement / NG

## Findings

| Severity | Area | Finding | Required Action |
|---|---|---|---|

## Blocking Items

## Should Fix

## Nit

## Suggested Split

## Validation Needed

## Final Judgment
```

## Completion Rule

blocking がある場合は、完了扱いにしない。

should-fix がある場合は、修正するか、後続Issue/Actionとして記録する。

レビュー結果は、必要に応じて `work/{project}/99_logs/` または `data/logs/` に保存する。
