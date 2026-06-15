# Consultations（経営相談ログ）

経営者からの相談を、会話で流さず構造化して残す。Skill `13-record-executive-context` の保存先。

## ルール

- 1相談 = 1ファイル。命名は `YYYY-MM-DD-{topic}.md`。
- 事実・仮説・未確認・判断・次アクションを分ける。
- 判断に至ったものは `decisions/` へ、実行ToDoは `company/action-ledger.md` へ起票する。
- 会社理解が深まったら `company/` の該当ファイルへ反映する。

## フォーマット

```md
# {日付} {相談テーマ}

- 背景・相談内容：
- 事実：
- 仮説：
- 未確認：
- 整理した論点：
- 助言・選択肢：
- 次アクション（→ action-ledger）：
```
