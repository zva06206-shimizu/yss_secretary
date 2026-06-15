# AI Data Design

## 目的

AI分析、AI検索、AI要約、AI分類に使うデータを、元データ、メタ情報、AI出力に分けて設計する。

## AI利用対象データ

| データID | データ名 | AI利用可否 | 個人情報 | 機密情報 | 利用目的 | 確認者 |
|---|---|---|---|---|---|---|
|  |  | Yes / No | Yes / No | Yes / No |  |  |

## 元データ管理項目

| 項目 | 内容 |
|---|---|
| source_id | 元データID |
| source_type | 議事録 / 問い合わせ / 作業記録 / メール / 添付資料 |
| created_by | 作成者 |
| created_at | 作成日時 |
| source_url | 元資料URL |
| confidentiality | 機密区分 |

## AI出力管理項目

| 項目 | 内容 |
|---|---|
| output_id | AI出力ID |
| source_id | 元データID |
| task_type | 要約 / 分類 / 抽出 / 検索インデックス |
| model_name | 利用モデル |
| prompt_version | プロンプト版数 |
| human_reviewed | 人による確認済みか |
| generated_at | 生成日時 |

## 注意

- AI出力は事実ではなく派生データとして扱う。
- 業務判断に使う場合は人の確認フラグを持たせる。
- 個人情報や機密情報をAIに投入する場合は、投入可否を設計時に明示する。
- AI出力を再生成できるよう、プロンプト版数とモデル名を残す。
