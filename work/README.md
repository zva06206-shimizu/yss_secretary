# Work

## 目的

このディレクトリは、いま動いている仕事・案件を置く場所である。

提案、議事録、業務整理、文書作成、ラフモック、システム実装、運用改善、業務データ設計など、案件に属するものはここに置く。

## 基本構成

```txt
work/
├── _template/
├── _archive/
├── _inbox/
└── {client-or-project}/
    ├── 00_context/
    ├── 01_business/
    ├── 02_proposal/
    ├── 03_documents/
    ├── 04_system/
    ├── 05_operation/
    ├── 06_data/
    └── 99_logs/
```

## 判断基準

案件に属するものは `work/{client-or-project}/` に入れる。

案件をまたいで再利用するものは `data/` に入れる。

Claude Codeの実行設定は `.claude/` に入れる。
