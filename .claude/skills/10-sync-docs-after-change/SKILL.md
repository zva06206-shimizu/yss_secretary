# Sync Docs After Change

## 目的

仕様変更、利用者指摘、テストNG、実装修正後に、関連ドキュメントと実装の整合性を回復する。

## 手順

1. 変更内容を `00_project-control/change-log.md` に記録する。
2. 要件定義の修正要否を確認する。
3. 画面設計・機能設計・DB設計の修正要否を確認する。
4. HTMLモックの修正要否を確認する。
5. テストケースの修正要否を確認する。
6. Laravel実装の修正要否を確認する。
7. `03_design/screen-function-matrix.md` を更新する。
8. `08_issues/issue-management.md` のステータスを更新する。
9. Git commit / push を行う。

## 完了条件

- 実装、設計、テスト、課題管理、変更履歴の整合性が取れている。
