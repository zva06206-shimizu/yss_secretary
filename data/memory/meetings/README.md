# Meetings（会議・経営相談の記録）

会議・経営相談の議事録を全社レベルで残す。Skill `15-facilitate-meetings-and-decisions` の保存先。

## ルール

- 1会議 = 1ファイル。命名は `YYYY-MM-DD-{topic}.md`。
- 決定事項・ToDo・未決事項・共有事項の4つに仕分けて残す。
- ToDo と決定事項は `data/memory/company/action-ledger.md` へ起票し、ここからは参照にとどめる（二重管理しない）。
- 案件固有の会議は `work/{project}/99_logs/` に置き、全社判断に関わるものだけここに残す。
- 人事・財務に関わる内容は要約にとどめる。

## 議事録フォーマット

```md
# {日付} {会議名}

- 目的／ゴール：
- 参加者：

## 決定事項（→ action-ledger Decisions）
## ToDo（→ action-ledger アクション一覧）
## 未決事項（→ action-ledger Open Decisions）
## 共有事項（記録のみ）
```
