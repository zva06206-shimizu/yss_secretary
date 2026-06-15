# Start Project

## 目的

新規案件を `work/{project_slug}/` に作成し、以後の作業記録先を確定する。

## 手順

1. 案件名（project_slug）、対象会社、目的を確認する。
2. `work/{project_slug}/` 配下に標準ディレクトリを作成する。

   ```text
   work/{project_slug}/
   ├── 00_context/      顧客・案件の前提、会議メモ
   ├── 01_business/     業務整理、As-Is/To-Be、KPI
   ├── 02_proposal/     提案、ROI、見積
   ├── 03_documents/    要件・設計・報告などの提出文書
   ├── 04_system/       モック・設計・実装
   ├── 05_operation/    マニュアル・教育・運用改善
   ├── 06_data/         KPI・監査・保存設計
   └── 99_logs/         指示ログ・変更履歴
   ```

3. `00_context/project-brief.md` に目的・対象・成功条件を記録する。
4. `99_logs/instruction-log.md` に初回指示を記録する。
5. Git commit / push を行う。

## 完了条件

- `work/{project_slug}/` と標準ディレクトリが存在する。
- project-brief、instruction-log が初期化されている。

## 関連

- 入口の振り分けは `secretary-hub`。
- 案件をまたぐ学びは `data/memory/` に戻す（`/learn-company`）。
