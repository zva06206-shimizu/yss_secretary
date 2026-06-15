# UI

企業向けWebシステム、管理画面、ダッシュボード、業務アプリで共通利用するUI部品・画面パターンを置く。

## 目的

- 案件ごとに一覧表、検索、ページング、モーダル、メール編集、ボタン、ナビゲーションを再設計しない。
- HTMLモックアップとLaravel Blade実装で同じコンポーネント思想を使う。
- PC、タブレット、スマホで破綻しない管理画面を標準化する。
- WCAG 2.2を意識し、キーボード操作、フォーカス、ラベル、エラー表示を標準化する。

## 注意

UIは業務そのものではない。

業務を画面化するときに使う共通部品である。

## 参照した設計思想

- GOV.UK Design System: 再利用可能なUI部品、フォーム、エラー、ページング、テーブルの考え方
- Material Design: コンポーネント体系、状態、レイアウト、ダイアログ、ナビゲーション
- WCAG 2.2: Focus Visible、Reflow、Target Size、Labels or Instructions、Error Identification
- MDN: レスポンシブデザイン、CSS Grid/Flexbox、セマンティックHTML

## 構成

```txt
data/ui/
├── README.md
├── foundations/
├── components/
├── patterns/
└── examples/
```

## 使用ルール

1. 新規画面はまず `components/` から必要部品を選ぶ。
2. 既存コンポーネントで足りない場合だけ追加する。
3. 追加時は、PC表示、スマホ表示、状態、アクセシビリティ、Laravel Blade化方針を記録する。
4. モックアップでは `examples/system-components.css` を流用する。
5. 本実装では、同じクラス体系をBlade Componentへ移植する。

## スマホ対応方針

- 768px未満では、横並びを縦積みにする。
- テーブルは横スクロールまたはカード型へ変換する。
- サイドバーはドロワー化する。
- モーダルは画面幅いっぱいに近づける。
- ボタンのタップ領域は最低44px相当を確保する。
- フィルターは折りたたみ、または下部シート化する。
