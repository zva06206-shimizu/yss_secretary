# Audit Source Registry Skill

## Purpose

`knowledge/source-registry.yml` に登録された情報源が、Claude Codeの開発基盤に正しく反映されているか確認する。

## When to Use

- 新しい情報源を追加したとき
- プロジェクト開始時
- 月次更新時
- ルール・Skills・Agentsを更新したとき

## Steps

1. `knowledge/source-registry.yml` を読む。
2. `scripts/audit-source-registry.py` を実行する。
3. 登録件数、カテゴリ、重複ID、必須項目の有無を確認する。
4. `knowledge/source-audit.md` を更新する。
5. `knowledge/distilled-rules/source-usage-map.md` と矛盾がないか確認する。
6. 各情報源が以下のいずれかに反映されているか確認する。
   - `.claude/rules/`
   - `.claude/skills/`
   - `knowledge/distilled-rules/`
   - `design-system/`
   - `work/_template/`
7. 不足があれば課題として記録し、必要なファイルを更新する。
8. Git commit / push を行う。

## Output

以下の形式で報告する。

```md
## Source Registry Audit Result

- Total Sources:
- Categories:
- Missing Required Keys:
- Duplicate IDs:
- Rule Reflection Status:
- Issues:
- Updated Files:
- Git Commit:
```

## Quality Bar

- URL登録だけで完了にしない。
- 各ソースが工程・成果物・チェック項目に紐づいている状態を完了とする。
- 詳細情報は必要時に読み、常時コンテキストには蒸留ルールのみ残す。
