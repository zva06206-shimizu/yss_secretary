# Claude Code Runtime Policy

## Purpose

この `.claude/` ディレクトリは、Claude Codeを動かすための操作盤である。

仕事の中身、顧客情報、提案書、設計書、実装成果物は `.claude/` に置かない。

## Repository Structure

```txt
.claude/  Claude Codeの実行設定
work/     実際の仕事・案件
data/     仕事を強くする共通データ
```

## Role of `.claude/`

`.claude/` に置くものは以下に限定する。

- agents
- skills
- hooks
- commands
- settings

## Do Not Store Here

以下は `.claude/` に置かない。

- 顧客情報
- 経営メモリ本体
- 提案書本体
- 設計書本体
- システム実装本体
- 業務データ本体
- 公的白書・統計データ本体

## Work Rule

案件に属する作業は `work/{client-or-project}/` に置く。

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

## Data Rule

案件をまたいで使うものは `data/` に置く。

```txt
data/
├── memory/
├── knowledge/
├── ui/
├── templates/
├── tools/
└── logs/
```

## Standard Behavior

1. まず依頼内容を分類する。
2. 経営相談、業務整理、提案、文書作成、システム化、運用改善を混同しない。
3. 案件に属するものは `work/` に記録する。
4. 案件をまたぐ学びは `data/` に戻す。
5. システム化は必要な場合だけ行う。
6. 作業後はGit commit / pushを行う。

## Intake Policy

短い指示をすぐ実装タスクに変換しない。

以下のどれかを判断する。

- 経営相談
- 顧客理解
- 業務改善
- 営業提案
- 顧客提出文書
- ラフモック
- システム設計
- 実装
- テスト
- 運用改善
- データ蓄積
- 経営メモリ更新

## Quality Policy

- 事実、仮説、未確認を分ける。
- 顧客や会社の課題を勝手に決めつけない。
- 経営効果、現場運用、継続性を重視する。
- 秘密情報、APIキー、パスワード、個人情報をコミットしない。
- 古い情報と新しい情報を混ぜない。

## Completion Report

作業完了時は、以下を簡潔に報告する。

- 更新ファイル
- 実施内容
- `data/` に戻した学び
- 残課題
- Git commit / push 結果
