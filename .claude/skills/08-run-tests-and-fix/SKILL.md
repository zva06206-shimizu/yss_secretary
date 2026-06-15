# Run Tests and Fix

## 目的

テストケースに従ってテストを実行し、NGを記録・修正・再テストする。

## 手順

1. `04_test/test-cases/` と `04_test/test-design.md` を確認する。
2. LaravelのUnit/Featureテスト、必要に応じてPlaywright E2Eテストを実行する。
3. 結果を `04_test/test-result.md` に記録する。
4. NGは `08_issues/issue-management.md` に起票する。
5. 原因を分類する。
   - 要件漏れ
   - 設計漏れ
   - 実装不具合
   - テストケース不備
   - データ不備
   - 環境不備
6. 必要に応じて要件・設計・モック・テスト・実装を遡及修正する。
7. 回帰テストを行う。

## 完了条件

- テスト結果が記録されている。
- NGが課題管理表に起票されている。
- 修正後の再テスト結果が残っている。
