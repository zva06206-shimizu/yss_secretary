# Agents

## 目的

このディレクトリは、Claude Codeが経営者の右腕として動くためのエージェント定義を管理する。

エージェントは増やしすぎない。判断、振り分け、顧客理解、提案設計、品質・リスク確認に絞る。

## 基本原則

- すべての作業は `secretary-hub` から開始する。
- 判断が必要な作業は `executive-partner` を使う。
- 顧客文脈が必要な作業は `client-context` を使う。
- 提案設計は `proposal-designer` を使う。
- 実装判断が済んだシステム化の構築は `system-builder` を使う。
- 重要な判断、顧客提出物、システム化、費用、リスクが絡む場合は `quality-risk-reviewer` を通す。
- 作業成果物は `.claude/` に保存しない。
- 案件成果物は `work/`、共通記憶・知識は `data/` に保存する。
- トークン最適化ルール `data/knowledge/rules/token-optimization-rules.md` を必ず守る。

## Agent Registry

| Agent | Main Role | Use When | Primary Output |
|---|---|---|---|
| `secretary-hub` | 入口・分類・振り分け | すべての依頼 | 依頼分類、担当Agent/Skill、保存先 |
| `executive-partner` | 経営判断・反証 | 経営相談、投資判断、優先順位 | 判断整理、選択肢比較、次アクション |
| `client-context` | 顧客理解 | 顧客情報、会議メモ、提案前整理 | 顧客文脈、課題、未確認事項 |
| `proposal-designer` | 提案設計 | 提案書、ROI、稟議通過設計 | 提案ストーリー、根拠、構成案 |
| `system-builder` | システム構築の司令塔 | 実装判断後の設計〜実装〜テスト | 動く実装、更新済み設計書、テスト結果 |
| `quality-risk-reviewer` | 品質・反証・リスク | 重要判断、提出前、実装前 | 問題点、リスク、修正案 |

## Standard Flow

### 経営相談

```txt
secretary-hub
↓
executive-partner
↓
quality-risk-reviewer
↓
data/memory 更新
```

### 顧客ヒアリング・会議メモ整理

```txt
secretary-hub
↓
client-context
↓
必要なら executive-partner
↓
work/{project}/00_context 更新
必要なら data/memory/clients 更新
```

### 営業提案書

```txt
secretary-hub
↓
client-context
↓
proposal-designer
↓
quality-risk-reviewer
↓
work/{project}/02_proposal 更新
```

### システム化相談

```txt
secretary-hub
↓
client-context
↓
executive-partner または proposal-designer
↓
quality-risk-reviewer
↓
実装判断OKなら system-builder（設計〜実装〜テスト）
↓
work/{project}/04_system 等を更新、設計書と整合
```

### 記憶更新

```txt
secretary-hub
↓
executive-partner または client-context
↓
data/memory 更新
```

## Review Gate

以下の場合は `quality-risk-reviewer` を必ず通す。

- 顧客に提出する資料
- 費用やROIを含む提案
- 経営判断に影響する助言
- システム化するかどうかの判断
- 個人情報、権限、監査ログ、AI利用が関係する設計
- 既存方針と矛盾する可能性がある変更
- 大きな投資、採用、契約、撤退判断

## Token Efficiency Rule

詳細ルールは `data/knowledge/rules/token-optimization-rules.md` に従う。

エージェントは、必要なファイルだけ読む。

### Always Read

- `CLAUDE.md`
- `.claude/CLAUDE.md`
- `.claude/agents/README.md`
- `data/knowledge/rules/token-optimization-rules.md`
- 該当Agent定義

### Read Only When Needed

- `data/memory/company/`
- `data/memory/clients/`
- `data/knowledge/public-data/`
- `data/templates/`
- `work/{project}/`

### Do Not Read By Default

- 関係ない案件フォルダ
- 大量の白書本文
- すべてのテンプレート
- すべての過去ログ

## Handoff Rule

Agent間で引き継ぐ場合、全文を渡さない。

以下を必ず渡す。

```md
## Handoff Summary

- Request Type:
- Goal:
- Current Facts:
- Hypotheses:
- Unknowns:
- Decisions:
- Required Output:
- Target Files:
- Review Needed: Yes / No
```

## Completion Rule

作業完了時は、以下を残す。

- 更新した `work/` ファイル
- 更新した `data/` ファイル
- 判断理由
- 未確認事項
- 次アクション
- 必要なら `quality-risk-reviewer` のレビュー結果

## Prohibited

- 入口なしで専門Agentから開始すること
- すべてのAgentを毎回使うこと
- 必要ないファイルを大量に読むこと
- Agentの判断を記録せずに成果物だけ作ること
- リスク確認なしに顧客提出物を完成扱いにすること
- Handoffで長文全文を渡すこと
