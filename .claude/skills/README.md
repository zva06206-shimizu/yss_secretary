# Skills

経営者の右腕AIが使うスキル群。秘書ハブ（`.claude/agents/secretary-hub.md` の Classification）が依頼を分類し、該当スキルへ振り分ける。`/<skill-name>` でユーザーが直接呼ぶこともできる。

## 経営運用（右腕の中核）

| Skill | 役割 | いつ使うか |
|---|---|---|
| `13-record-executive-context` | 経営文脈の記録 | 経営相談・会社/人/KPIの更新を `data/memory/` に残す |
| `14-analyze-numbers-and-act` | 数字を読み打ち手化 | KPI予実の差異を分解し、原因・打ち手まで落とす |
| `15-facilitate-meetings-and-decisions` | 会議の前後を回す | アジェンダ整理、決定・ToDo・未決の抽出と起票 |
| `16-evaluate-roi-and-cost` | 費用対効果の判断 | 投資・施策・採用をコスト・効果・回収期間で評価 |
| `17-plan-people-and-org` | 人・組織の設計 | 採用要件・教育計画・属人化解消・役割設計 |
| `18-watch-market-and-competitors` | 外部環境の定点観測 | 競合・業界・制度の変化を機会／脅威に翻訳 |
| `19-manage-business-risks` | 経営リスク管理 | 資金繰り・取引先依存・法令等を棚卸し対策 |
| `12-design-business-data-accumulation` | 業務データ設計 | 蓄積すべきデータと保存設計を決める |

関連コマンド：`/executive-review`（定例点検）、`/learn-company`、`/decide-implementation-scope`。
関連メモリ：`data/memory/company/` の `kpi-actuals.md`・`action-ledger.md`・`strategy-roadmap.md`・`current-issues.md`・`organization-and-people.md`・`market-watch.md`・`risk-register.md`、および `data/memory/meetings/`・`decisions/`・`consultations/`・`learnings/`・`clients/`。

## システム開発（必要な場合のみ）

| Skill | 役割 |
|---|---|
| `00-start-project` | 案件の起票・初期化 |
| `01-research-company` | 企業・業界調査 |
| `02-requirements-interview` | ヒアリング |
| `03-create-requirements-doc` | 要件定義 |
| `04-design-screens-functions` | 画面・機能設計 |
| `05-create-test-design` | テスト設計 |
| `06-build-html-mockup` | HTMLモック |
| `07-implement-laravel` | 実装 |
| `08-run-tests-and-fix` | テスト・修正 |
| `09-record-user-feedback` | フィードバック記録 |
| `10-sync-docs-after-change` | 変更後のドキュメント整合 |
| `11-review-maintainability` | 保守性レビュー |
| `audit-source-registry` | 出典レジストリ監査 |

関連コマンド：`/create-rough-system-mockup`、`/review-rough-mockup`。

## 原則

- システム化は打ち手の一つ。先に運用・教育・ルールで解けないか考える。
- 事実・仮説・未確認を分ける。学びは `data/` に戻す。
- 作業単位ごとに Git commit / push を行う。
