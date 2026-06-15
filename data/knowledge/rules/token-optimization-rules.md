# Token Optimization Rules

## 目的

Claude Codeが不要なファイルを読みすぎず、必要な情報だけを使って効率よく判断・作業できるようにする。

このルールは、エージェント、スキル、文書作成、白書調査、システム開発、経営メモリ更新のすべてに適用する。

## 基本原則

- まず索引を見る。
- 次に要約を見る。
- 必要な場合だけ原文を見る。
- 関係ない案件フォルダを読まない。
- 大量ファイルを一括で読まない。
- 白書・統計・長文資料は、原文全文ではなく要約・用途・出典を優先する。
- 一度読んだ内容は、必要に応じて要約ファイルに戻す。

## 読み込み優先順位

```txt
1. 入口ルール
2. 索引
3. 要約
4. 対象ファイル
5. 原文・詳細資料
```

## 標準読み込み順

### 全作業共通

必ず最小限に留める。

```txt
CLAUDE.md
.claude/CLAUDE.md
.claude/agents/README.md
該当Agent定義
```

### 経営相談

```txt
data/memory/decision-principles.md
data/memory/company/README.md
必要な会社ファイルのみ
```

### 顧客案件

```txt
work/{project}/00_context/project-brief.md
work/{project}/00_context/meeting-notes.md
必要な範囲の business / proposal / documents のみ
```

### 提案書

```txt
data/templates/proposals/rules/proposal_design_rules.md
work/{project}/00_context/
work/{project}/01_business/
data/knowledge/public-data/source-index.md
必要な公的データ要約のみ
```

### 公的白書・統計

```txt
data/knowledge/public-data/source-index.md
data/knowledge/public-data/public-whitepapers-and-reports.md
必要な資料の summary / key-statistics のみ
```

## 読んではいけないもの

以下は、明確な必要がある場合以外は読まない。

- 関係ない `work/{project}/`
- `data/knowledge/public-data/` の大量原文
- 全白書PDF
- すべての過去ログ
- すべてのテンプレート
- すべての顧客カルテ
- すべてのGitログ

## Long Context Handling

長文資料を扱う場合は、以下の順に処理する。

1. 目的を決める。
2. 必要な章・項目だけを読む。
3. 要点を `summary.md` に保存する。
4. 提案で使える統計は `key-statistics.md` に分離する。
5. 原文全文の再読を避ける。

## Summary First Rule

長文資料や過去ログを追加する場合は、原則として以下を作る。

```txt
summary.md
key-points.md
use-cases.md
source.md
```

全文コピーは、ライセンス上問題ない場合のみ許可する。

## Agent Handoff Compression

Agent間の引き継ぎでは、全文を渡さない。

以下の形式で圧縮する。

```md
## Handoff Summary

- Goal:
- Facts:
- Hypotheses:
- Unknowns:
- Decisions:
- Target Files:
- Required Next Action:
```

## Token Budget Classes

作業前に、必要な読み込み量を分類する。

| Class | 説明 | 目安 |
|---|---|---|
| S | 既存文脈と1〜3ファイルで足りる | 短時間作業 |
| M | 5〜10ファイル程度を読む | 通常作業 |
| L | 複数フォルダ・長文資料を読む | 事前に対象を絞る |
| XL | 白書、過去ログ、複数案件を横断 | 分割実行する |

## Escalation Rule

L以上の作業では、いきなり全文を読まない。

まず以下を出す。

- 読む対象
- 読まない対象
- 作業単位
- 保存先
- 想定成果物

## Completion Rule

作業後、再利用価値のある情報は以下へ戻す。

- `data/memory/`：判断、顧客文脈、会社理解
- `data/knowledge/`：外部知識、白書、標準、ルール
- `data/templates/`：再利用テンプレート
- `work/{project}/99_logs/`：案件固有の判断・課題

## 禁止

- 関係ないフォルダを網羅的に読むこと
- 白書や長文資料を毎回全文読むこと
- 同じ情報を複数ファイルに重複保存すること
- Handoffで長文全文を渡すこと
- 検索せずに全ファイルを読むこと
- 要約を作らずに長文原文だけ保存すること
