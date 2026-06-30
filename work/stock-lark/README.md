# stock-to-lark

yfinance で株価を取得 → Lark Base に毎日アップロードする最小構成。
GitHub Actions（無料枠）で平日1日1回・引け後に自動実行する。

## 重要な前提

**このフォルダ（`work/stock-lark/`）の中身を、別の新規GitHubリポジトリのルートに置く。**
GitHub Actions のワークフローは `.github/workflows/` が**リポジトリのルート直下**にないと動かない。
秘書リポジトリ（yss_secretary）の `work/` 配下に置いたままでは実行されない。

```
新リポジトリ(例: stock-to-lark)/
├── fetch.py
├── tickers.txt
├── requirements.txt
├── .gitignore
├── .env.example
└── .github/workflows/stock.yml
```

## セットアップ手順

### 1. Lark 側（アプリと書込み先）
1. [Lark 開発者コンソール](https://open.larksuite.com/app) でアプリを作成 → **App ID / App Secret** を控える
2. アプリの権限に **Bitable（Base）の読み書き** を付与し、対象 Base にアプリを追加
3. 書き込む Base とテーブルを開き、URL から控える
   - `App Token`：BaseのURL `.../base/<ここがApp Token>`
   - `Table ID`：テーブル表示時の `tblxxxxxxxx`
4. テーブルに列を用意（列名は `fetch.py` の `FIELD_*` と一致させる）
   `銘柄`(テキスト) / `名称`(テキスト) / `日付`(テキスト) / `終値`(数値) /
   `始値`(数値) / `高値`(数値) / `安値`(数値) / `出来高`(数値) / `通貨`(テキスト)

### 2. GitHub 側
1. 新規リポジトリを作り、このフォルダの中身を push
2. リポジトリの **Settings → Secrets and variables → Actions** に4つ登録
   - `LARK_APP_ID` / `LARK_APP_SECRET` / `LARK_APP_TOKEN` / `LARK_TABLE_ID`
3. **Actions タブ → stock-to-lark → Run workflow** で手動実行し動作確認
4. 以後は平日 JST 16:00 ごろ自動実行

### 3. 銘柄の変更
`tickers.txt` を編集して push するだけ。日本株は `7203.T`、米国株は `AAPL`。

## ローカル確認（任意・Windows/PowerShell）
```powershell
pip install -r requirements.txt
Copy-Item .env.example .env   # .env に実値を記入（.env はコミットされない）
Get-Content .env | ForEach-Object { if ($_ -match '^\s*([^#=]+)=(.*)$') { [Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim()) } }
python fetch.py
```

## 既知の注意点
- **cronは不正確**：GitHub のスケジュールは混雑時に数分〜十数分遅れる。厳密な時刻実行は不可。
- **yfinanceは非公式**：Yahoo をスクレイピングするため、クラウドIPで稀にレート制限/403。`fetch.py` はリトライ実装済み。多発するなら有料API（Alpha Vantage 等）へ差し替え。
- **追記方式**：毎回 `batch_create` で行を追加する。同じ日を二重登録したくない場合は、実行前に当日分の有無を確認するロジックを足す（拡張余地）。
- **無料枠**：パブリック/プライベートとも個人利用なら GitHub Actions 無料枠で十分（1回数十秒）。
