# Engineering Practices References

## 目的

Claude CodeがPR、差分、実装変更をレビューするときに、信頼できる外部基準を参照するための入口である。

このディレクトリでは、Google Engineering Practices Documentation のような公式・準公式のレビュー基準を、全文コピーではなく、参照先・用途・読み分けルールとして管理する。

## 基本方針

- 入口は薄くする。
- 厚い知識は必要なときだけ参照する。
- 要約で原文を置き換えない。
- 迷ったら該当する原文1ファイルだけ読む。
- 全ファイルを一括で読まない。
- 原文を同梱する場合はライセンスを確認する。

## Primary Source

| Source | URL | License / Notes | Use |
|---|---|---|---|
| Google Engineering Practices | https://github.com/google/eng-practices | CC BY 3.0。利用時は帰属表示が必要 | PRレビュー、差分レビュー、変更分割、レビューコメント基準 |
| Google Engineering Practices site | https://google.github.io/eng-practices/ | 公開ドキュメント | 必要な1ページだけ参照 |

## On-demand Reference Map

| 判断 | 参照先 | 用途 |
|---|---|---|
| 変更が大きすぎる | https://google.github.io/eng-practices/review/developer/small-cls.html | 変更分割、リファクタと機能変更の分離 |
| レビューで何を見るか | https://google.github.io/eng-practices/review/reviewer/looking-for.html | 設計、機能、複雑さ、テスト、保守性の観点 |
| レビューコメントを書く | https://google.github.io/eng-practices/review/reviewer/comments.html | コメントの粒度、伝え方、修正要求 |
| 用語確認 | https://github.com/google/eng-practices | CL、LGTMなどの用語読み替え |

## Terminology Mapping

| Google term | Repository term |
|---|---|
| CL | PR / Pull Request / change |
| submit | merge / push / release |
| code health | maintainability / quality |
| reviewer | reviewer / quality-risk-reviewer |
| author | implementer / Claude Code |

## 使い方

1. まず `.claude/skills/review-pr-quality/SKILL.md` を読む。
2. チェックリストで当たりをつける。
3. 判断に迷った項目だけ、上記Reference Mapの該当URLを見る。
4. レビュー結果は blocking / should-fix / nit に分ける。
5. blocking がある場合は、完了・提出・merge扱いにしない。

## 注意

このREADMEは原文の代替ではない。

レビュー判断に迷う場合は、該当する一次資料を確認する。
