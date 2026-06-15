# /executive-review

経営者の右腕として、定例（週次／月次）で会社の状態を点検し、未決事項・期限超過・KPI逸脱を洗い出し、今やるべきことを提示する。

会社の仕組みを「受け身（指示待ち）」から「能動的に回る経営リズム」へ変えるためのコマンド。

## 使い方

```txt
/executive-review weekly     # 週次レビュー（既定）
/executive-review monthly    # 月次レビュー（KPI予実を含む）
```

引数がなければ `weekly` として扱う。

## 実行内容

### 1. 会社の現状を読む

- `data/memory/decision-principles.md`
- `data/memory/company/management-kpi.md`（KPI定義）
- `data/memory/company/kpi-actuals.md`（KPI実績）
- `data/memory/company/current-issues.md`
- `data/memory/company/action-ledger.md`
- `data/memory/company/strategy-roadmap.md`

### 2. 点検する（差分を出すことが目的）

- **期限超過アクション**：`action-ledger.md` で状態が `未着手/進行中` かつ期限を過ぎたもの。
- **滞留アクション**：更新日が古いまま動いていないもの。
- **未決事項**：`Open Decisions` で判断期限が近い／過ぎたもの。
- **KPI逸脱**（月次のみ）：`kpi-actuals.md` の判定が `要注意/逸脱` のもの。差異と対応の有無を確認。原因分解と打ち手まで深掘りする場合は Skill `14-analyze-numbers-and-act` に渡す。
- **重点施策の進捗**：`strategy-roadmap.md` の「今月／今四半期」に対する進み具合。
- **経営リスク**（四半期、または重大事象時）：`risk-register.md` の優先度上位と監視指標。深掘りは Skill `19-manage-business-risks` に渡す。
- **外部環境**（月次・四半期）：`market-watch.md` の前回からの差分。観測更新は Skill `18-watch-market-and-competitors` に渡す。

### 3. 経営者に提示する（レビュー出力）

以下を簡潔にまとめて提示する。長文にしない。

1. **要対応（今すぐ）**：期限超過・KPI逸脱・判断待ちの未決事項
2. **今週の重点**：roadmapとアクションから絞った3〜5件
3. **数字の状況**（月次）：KPI予実のサマリと逸脱
4. **判断を仰ぐこと**：経営者が決めないと進まない未決事項

### 4. 台帳を更新する

- 新たに決まったアクション・意思決定を `action-ledger.md` に追記。
- 月次は `kpi-actuals.md` に当月実績を1行ずつ追記し、判定・差異を更新。
- 完了・中止は消さず状態を変える。更新日を必ず直す。

### 5. 学びを戻す

- 繰り返し出る論点・判断は `decision-principles.md` や `data/memory/learnings/` に反映する。

## 成果物

- 更新された `data/memory/company/action-ledger.md`
- （月次）更新された `data/memory/company/kpi-actuals.md`
- 必要に応じて `current-issues.md` / `strategy-roadmap.md` の更新

## 定期実行（任意・各自で登録）

このコマンドは手動でも使えるが、定例で自動実行すると経営リズムが「指示待ち」から「能動的に回る」状態になる。

自動化したい場合は、各自が `/schedule` で**自分のアカウントに**リモート定例を登録する。推奨例：

- 週次：「毎週月曜9時に `/executive-review weekly` を実行」
- 月次／四半期：「毎月1日（または四半期初め）9時に `/executive-review monthly` を実行」

登録時は、リモートエージェントが結果を `data/memory/` に書き戻し `git push` するよう、プロンプトに「変更を main へ commit / push する」ことを明記する。

> 注意：`/schedule` の定例（routines）は**実行者のアカウントに紐づくクラウド設定で、このリポジトリには含まれない**。リポジトリを配布しても定例はコピーされないため、配布先では各自が改めて登録する必要がある（逆に、配布で勝手に動く心配もない）。

## 関連スキル

- 数字を分解して原因・打ち手まで詰める：Skill `14-analyze-numbers-and-act`
- 会議の前後（アジェンダ／決定・ToDo・未決の抽出）を回す：Skill `15-facilitate-meetings-and-decisions`
- 投資・施策の費用対効果を判断する：Skill `16-evaluate-roi-and-cost`
- 採用・教育・属人化解消を設計する：Skill `17-plan-people-and-org`
- 競合・業界・制度を定点観測する：Skill `18-watch-market-and-competitors`
- 経営リスクを棚卸しする：Skill `19-manage-business-risks`

## 原則

- 報告は「差分と要対応」に絞る。全項目の羅列はしない。
- 事実・仮説・未確認を分ける。
- 経営判断の高速化と、やり残し防止を最優先にする。
