# Simple Business OS Structure

## 結論

このリポジトリは、誰にでも説明できるように、トップレベルを極力減らす。

考え方はシンプルにする。

```txt
work = 案件で実際に動く場所
data = 案件をまたいで使う知識・記憶・部品・ログの保管場所
.claude = Claude Codeを動かす設定場所
```

つまり、基本構成は以下でよい。

```txt
system-create/
├── README.md
├── CLAUDE.md
├── .claude/
├── work/
└── data/
```

必要に応じて、実行ツールだけ `tools/` として分ける。ただし、最初は `data/tools/` に含めてもよい。

## 誰にでも説明する言い方

このリポジトリは、会社の仕事をClaude Codeで進めるための場所である。

- `work/` は、いま動いている仕事を入れる場所。
- `data/` は、次の仕事でも使う知識や記憶を入れる場所。
- `.claude/` は、Claude Codeにどう動いてもらうかを決める場所。

これだけで説明できる構成にする。

## 推奨トップレベル構成

```txt
system-create/
├── README.md
├── CLAUDE.md
├── .claude/
│   ├── settings.json
│   ├── agents/
│   ├── skills/
│   ├── hooks/
│   └── commands/
│
├── work/
│   ├── README.md
│   ├── _template/
│   ├── _archive/
│   └── {client-or-project}/
│       ├── 00_context/
│       ├── 01_business/
│       ├── 02_proposal/
│       ├── 03_documents/
│       ├── 04_system/
│       ├── 05_operation/
│       ├── 06_data/
│       └── 99_logs/
│
└── data/
    ├── README.md
    ├── memory/
    ├── knowledge/
    ├── ui/
    ├── templates/
    ├── tools/
    └── logs/
```

## 各フォルダの役割

### .claude/

Claude Codeの実行設定だけを置く。

置くもの:

- agents
- skills
- hooks
- settings
- commands

置かないもの:

- 顧客情報
- 経営メモリ本体
- 提案書本体
- 設計書本体
- システム実装本体

`.claude/` は、仕事の中身を置く場所ではない。Claude Codeの操作盤である。

### work/

案件・顧客・プロジェクトごとの業務本体を置く。

顧客理解、業務整理、提案、文書化、システム化、運用、データ活用は案件の中でつながっている。

そのため、トップレベルで細かく分けず、案件単位でまとめる。

#### work/{client-or-project}/

```txt
work/{client-or-project}/
├── 00_context/
├── 01_business/
├── 02_proposal/
├── 03_documents/
├── 04_system/
├── 05_operation/
├── 06_data/
└── 99_logs/
```

#### 00_context/

顧客・案件の前提を置く。

- client-profile.md
- project-brief.md
- meeting-notes.md
- relationship-context.md
- assumption-log.md

#### 01_business/

経営課題、業務課題、改善方針を置く。

- current-state.md
- issues.md
- workflow-as-is.md
- workflow-to-be.md
- kpi.md
- improvement-policy.md

#### 02_proposal/

営業提案書、ROI、見積前提を置く。

- sales-proposal.md
- executive-summary.md
- roi.md
- pricing.md
- proposal-review.md
- pdf/

#### 03_documents/

顧客提出文書を置く。

- requirements-definition.md
- system-design-document.md
- meeting-report.md
- report.md
- pdf/

#### 04_system/

システム設計・実装を置く。

- requirements/
- design/
- mockup/
- app/
- tests/
- release/

#### 05_operation/

導入後の運用、教育、改善を置く。

- operation-manual.md
- training-plan.md
- support-log.md
- improvement-log.md

#### 06_data/

案件内で発生する業務データ、KPI、監査ログ、AI分析元データを置く。

- data-inventory.md
- kpi-definition.md
- audit-log-design.md
- ai-data-design.md
- retention-policy.md

#### 99_logs/

案件内の履歴を置く。

- instruction-log.md
- decision-log.md
- change-log.md
- issue-log.md

### data/

案件をまたいで使うものをまとめる。

旧案の `memory/`, `knowledge/`, `ui/`, `tools/`, `logs/` は、トップレベルに分けすぎると説明が難しくなる。

そのため、まとめて `data/` に置く。

```txt
data/
├── memory/
├── knowledge/
├── ui/
├── templates/
├── tools/
└── logs/
```

#### data/memory/

会社や経営者に関する記憶を置く。

- 会社情報
- 事業内容
- 従業員・組織
- 経営KPI
- 経営相談
- 意思決定
- 顧客別の長期文脈
- 提案や開発で得た学び

#### data/knowledge/

公式知識、標準、参考情報を置く。

- Claude Code公式情報
- AI情報
- Laravel / MySQL / OWASP / IPA / WCAG
- 文書品質
- PDF組版
- 保守性
- セキュリティ

#### data/ui/

UI共通部品を置く。

これは業務ではない。

業務を画面化するときに使う部品である。

- デザインシステム
- ボタン
- フォーム
- テーブル
- モーダル
- ナビゲーション
- 管理画面UI
- スマホ対応UI

#### data/templates/

案件をまたいで再利用するテンプレートを置く。

- 提案書テンプレート
- 設計書テンプレート
- 議事録テンプレート
- ROIテンプレート
- 運用マニュアルテンプレート

ただし、案件で実際に作った成果物は `work/{project}/` に置く。

#### data/tools/

スクリプトや自動生成ツールを置く。

- PDF生成
- バリデーション
- 初期化スクリプト
- 監査スクリプト

#### data/logs/

リポジトリ全体の実行ログを置く。

- git-sync.log
- hook-events.log
- claude-actions.log

## 旧案からの統合方針

| 旧案 | 新案 |
|---|---|
| business/ | work/{project}/01_business/ |
| clients/ | work/{project}/00_context/ または data/memory/clients/ |
| proposals/ | work/{project}/02_proposal/ または data/templates/proposals/ |
| documents/ | work/{project}/03_documents/ または data/templates/documents/ |
| systems/ | work/{project}/04_system/ |
| operations/ | work/{project}/05_operation/ |
| data/ | work/{project}/06_data/ と data/ に分ける |
| executive-memory/ | data/memory/ |
| knowledge/ | data/knowledge/ |
| design-system/ | data/ui/ |
| tools/ | data/tools/ |
| logs/ | data/logs/ |

## 判断基準

迷ったら、次の基準で決める。

### 案件に属するもの

`work/{project}/` に入れる。

例:

- 顧客Aへの提案書
- 顧客Aの議事録
- 顧客Aの要件定義書
- 顧客Aのシステム実装
- 顧客Aの運用ログ
- 顧客AのKPI定義

### 案件をまたいで使うもの

`data/` に入れる。

例:

- 会社の判断軸
- 提案書テンプレート
- 設計書テンプレート
- Claude Code公式知識
- セキュリティ標準
- UI部品
- PDF生成スクリプト

### Claude Codeを動かすもの

`.claude/` に入れる。

例:

- agents
- skills
- hooks
- settings

## 最終判断

最もシンプルで説明しやすい構成は、以下である。

```txt
.claude/  = Claude Codeの操作盤
work/     = 実際の仕事を置く場所
data/     = 仕事を強くするための共通データ置き場
```

これを基本構成とする。

トップレベルを増やさない。

業務は `work/`、共通資産は `data/`、実行設定は `.claude/` に分ける。
