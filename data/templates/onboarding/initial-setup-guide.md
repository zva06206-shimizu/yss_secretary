# Initial Setup Guide

## 目的

このリポジトリを初めて使うときに、Claude Codeが最初に案内する初期設定手順を定義する。

このリポジトリは、単なる開発テンプレートではない。

```txt
.claude/  = Claude Codeの操作盤
work/     = 実際の仕事・案件
data/     = 共通データ・記憶・知識・テンプレート・UI・ツール
```

この3つの役割を理解してから使い始める。

---

## 初回に確認すること

### 1. リポジトリ構成

以下が存在するか確認する。

```txt
.claude/
work/
data/
```

不足している場合は、初期化前に構成を補正する。

### 2. 実行権限

以下を実行する。

```bash
chmod +x data/tools/scripts/*.sh .claude/hooks/*.sh
```

### 3. 会社メモリの初期化

会社名または会社スラッグを決めて、以下を実行する。

```bash
./data/tools/scripts/init-company.sh company-name
```

例:

```bash
./data/tools/scripts/init-company.sh dot-think
```

作成先:

```txt
data/memory/company/{company-name}/
```

### 4. 作業場所の作成

新しい案件や仕事を始める場合は、`work/` に作業フォルダを作成する。

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

### 5. 最初に記入するファイル

最低限、以下を記入する。

```txt
work/{client-or-project}/00_context/project-brief.md
data/memory/company/company-profile.md または data/memory/company/{company}/company-brain.md
data/memory/decision-principles.md
```

### 6. GitHub Actionsの確認

GitHub上で以下を確認する。

- CI が通るか
- Monthly Public Source Check が手動実行できるか

月次白書チェックは、以下を入力として使う。

```txt
data/knowledge/public-data/source-index.md
data/knowledge/public-data/public-whitepapers-and-reports.md
```

---

## Claude Codeが初回に伝えるべきこと

Claude Codeは、このリポジトリで初回作業を開始するとき、以下を案内する。

```txt
このリポジトリは .claude / work / data の3層で運用します。

1. .claude はClaude Codeの操作盤です。
2. work は今動いている仕事・案件を置く場所です。
3. data は会社理解、白書、テンプレート、UI部品、ツールなどの共通データ置き場です。

初回は以下を確認してください。

- chmod +x data/tools/scripts/*.sh .claude/hooks/*.sh
- ./data/tools/scripts/init-company.sh company-name
- work/{client-or-project}/ を作成
- data/memory/ に会社情報と判断軸を記入
- GitHub Actions のCIを確認
```

---

## 初期設定チェックリスト

| No | 確認項目 | 状態 |
|---:|---|---|
| 1 | `.claude/` が存在する | 未確認 |
| 2 | `work/` が存在する | 未確認 |
| 3 | `data/` が存在する | 未確認 |
| 4 | HookとScriptに実行権限を付与した | 未確認 |
| 5 | 会社メモリを初期化した | 未確認 |
| 6 | `work/{project}/` を作成した | 未確認 |
| 7 | `project-brief.md` を作成した | 未確認 |
| 8 | `decision-principles.md` を確認した | 未確認 |
| 9 | CIを確認した | 未確認 |
| 10 | 月次白書チェックを確認した | 未確認 |

---

## 注意

- `.claude/` に顧客情報や成果物本体を置かない。
- 案件に属するものは `work/` に置く。
- 案件をまたいで使うものは `data/` に置く。
- 会社の判断軸や経営メモリは `data/memory/` に置く。
- 白書や公的統計は `data/knowledge/public-data/` に置く。
- UI部品は `data/ui/` に置く。
