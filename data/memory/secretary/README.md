# Secretary Memory

経営者の右腕AI（秘書）の人格と、ユーザーとの継続的な関係を保存する場所。

ここにあるファイルは、毎セッション開始時に `SessionStart` フック（`.claude/hooks/load-secretary.sh`）で文脈へ読み込まれる。これにより、Claude Code は毎回「同じ秘書」として会話を続けられる。

## ファイル

| ファイル | 役割 |
|---|---|
| `secretary-profile.md` | 秘書の名前・呼び方・役割・性格・口調。初期セットアップで設定する。 |
| `conversation-log.md` | ユーザーとのやり取りで残すべき継続文脈（決め事・好み・呼び方・進行中の話題）。 |

## 名前の設定・変更

```bash
./data/tools/scripts/init-secretary.sh "秘書の名前"
```

既にプロフィールがある場合は名前だけ更新する。性格・口調を変えたいときは `secretary-profile.md` を直接編集する。

## 運用ルール

- 秘書は毎回、まず `secretary-profile.md` を読み、その名前・人格として振る舞う。
- 会話の中で今後も覚えておくべきこと（呼び方、好み、進行中の判断、約束）が出たら、`conversation-log.md` に1〜2行で追記する。
- 一時的な作業メモはここに書かない。案件は `work/`、会社理解は `data/memory/company/` に書く。
- 秘密情報・個人情報はここに保存しない。
