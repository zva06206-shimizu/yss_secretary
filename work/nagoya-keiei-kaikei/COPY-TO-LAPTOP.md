# ノートPCへ手動コピーするファイル一覧（GitHub未掲載＝git管理外）

作成日：2026-06-17 ／ 用途：6/23現地調査の作業用ノートPCへ持ち出し

## 前提（重要）

- **GitHub上にあるファイル（ネットワーク図・IPアドレスリスト・調査計画・写真撮影方式 等）は、ノートPCで `git clone` または `git pull` すれば自動で入る** → 手動コピー不要。
- 手動コピーが必要なのは、**`.gitignore` でGitHubに上げていない秘匿・大容量ファイル**だけ（下記）。合計 **168ファイル**。
- コピー先のノートPCでも、同じ `.gitignore` が効くのでこれらは引き続きgit管理外のまま（誤コミットされない）。

---

## A. 最優先：認証情報（秘匿）　`06_data/credentials/` フォルダ一式

| ファイル | 中身 | 重要度 |
|---|---|---|
| **2gou / 5gou / 6gou-survey-worksheet.xlsx** | 各館 当日記入Excel（6シート:手順/機器/IP照合/スクショ貼付/物理配線/提案確認） | ★当日これを開いて埋める |
| **field-worksheet.md** | 全館 機器一覧（型番/IP/ID/PW/接続先/Config取得欄） | ★最重要 |
| **device-credentials.md** | 全機器の管理ID/PW/PIN/IPsec PSK/SSIDキー台帳 | ★最重要 |
| **1gou_RTX830_config.txt** | 1号館RTX(ハブ)の全文config＝ターゲット構成の正本 | 参考・基準 |
| README.md / _gen_5gou_worksheet.py | フォルダ説明 / Excel生成スクリプト | 参考 |

> ⚠️ **credentialsフォルダごとコピー**すればOK（中身は全部git管理外）。ただし**USB紛失＝情報漏洩**。暗号化USB or PCローカルのみ、メール添付・クラウド共有はしない。帰宅後USBから消す。
> ※5号館Excelは埋めると設定スクショ＝機微情報になる。filled版もcredentials内に保存すればgitに乗らない。

## B. 現地調査写真（資料binder）　164ファイル・約325MB

`work/nagoya-keiei-kaikei/06_data/raw-photos/`

| サブフォルダ | 枚数 | 内容 |
|---|---|---|
| 202603/ | 59 | 2026年3月＝主に1号館＋ヒアリング、IODATA PINコード等 |
| 202606/2020-2023/ | 61 | 2020〜2023の設計binder（IP設計・機器一覧・config・**IMG_2928機器一覧/IMG_Meikei-BD6H-RTX1210**） |
| 202606/2024/ | 44 | 2024の5/6号館調査（IP設計・構成図） |

> 当日「資料 vs 実態」の差分照合に使う。容量が大きいので、最低限なら下記「当日よく見る写真」だけでも可。

### 当日よく見る写真（最低限これだけでも）
- `202606/2020-2023/IMG_2928.JPG`（4ルータ機器一覧）
- `202606/2020-2023/IMG_Meikei-BD6H-RTX1210.jpg`（6号館RTXのID/PW）
- `202606/2020-2023/IMG_2943.JPG`〜`IMG_2950.JPG`（6号館/5号館 設定・IP設計）
- `202606/2024/IMG_8959/8977/8980/8983/8990/9001/9002.jpg`（5/6号館 構成図・IP設計）
- `202603/IODATA_PINコード.png`（NAS PIN）

## C. その他　1ファイル

- `work/nagoya-keiei-kaikei/06_data/proposal/202603/NW図_IP_Lists.pdf`（旧NW図・IPリストPDF）
  ※同フォルダの提案pptx・202606のPDFはGitHub掲載済（pullで入る）

---

## コピー方法（どちらか）

### 方法1：USBメモリに3カテゴリをまるごとコピー（簡単）
エクスプローラで以下をUSBへドラッグ：
- `work\nagoya-keiei-kaikei\06_data\credentials\`（フォルダごと）
- `work\nagoya-keiei-kaikei\06_data\raw-photos\`（フォルダごと）
- `work\nagoya-keiei-kaikei\06_data\proposal\202603\NW図_IP_Lists.pdf`

### 方法2：PowerShellでUSB(例 E:)へ一括（robocopy）
```powershell
$src = "C:\git\yss_secretary\work\nagoya-keiei-kaikei\06_data"
$dst = "E:\nagoya-持出\06_data"
robocopy "$src\credentials" "$dst\credentials" /E
robocopy "$src\raw-photos"  "$dst\raw-photos"  /E
robocopy "$src\proposal\202603" "$dst\proposal\202603" "NW図_IP_Lists.pdf"
```

### ノートPC側でGitHub分を入れる
```powershell
# 初回
git clone <このリポジトリのURL> C:\git\yss_secretary
# 2回目以降
cd C:\git\yss_secretary; git pull
```
→ そのうえで、上記A/B/Cを `work\nagoya-keiei-kaikei\06_data\` の同じ場所に貼れば完成。

---

## 持ち出しチェック
- [ ] A 認証情報3ファイル（暗号化USB推奨）
- [ ] B 写真（最低限セット or 全164枚）
- [ ] C NW図_IP_Lists.pdf
- [ ] ノートPCで `git pull` 済み（図・IPリスト・計画書が最新か確認）
- [ ] 帰宅後：USB内の認証情報を消す or 安全保管（紛失対策）
