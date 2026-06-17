# 5号館 当日確認手順（2026-06-23）

集合：6/23(火) 8:00 5号館（池下1-1-4）／調査者：清水（YSS）
記入用Excel：`06_data/credentials/5gou-survey-worksheet.xlsx`（★git管理外。機器IP・ログイン・スクショ貼付先入り。当日はこれを開いて埋める）
※この手順書はgit追跡（秘匿なし）。ログインID/PWはExcel/`device-credentials.md`を参照。

## 進め方（STEP1→6）

1. **STEP1 型番でManaged/Unmanagedを仕分け**
   本体ラベルで型番末尾を確認。**BS-GS2008P/2016P＝管理型→login対象**。NETGEAR gs324／ELECOM EHC／IODATA BSH-GP08／BUFFALO LSW6-GT-8EP＝無管理→物理のみ。
   ※「管理型＝必ずPoE」ではない（1号館にBS-GS2016＝非PoE管理型あり）。**P有無を必ず確認**。無管理に管理型(gs324T等)が紛れていないかも一目チェック。

2. **STEP2 ID/PW既知の機器を先にlogin → Configバックアップ（テキスト）**
   - RTX1210（NMACRT05）：`show config` 全文をテキスト保存 → ファイル名 `5gou_NMACRT05_config.txt`、USBへ。
   - 管理型SW（BS-GS2008P ×5）：設定ファイルをエクスポート ＋ 設定画面スクショ。

3. **STEP3 AP等は設定画面スクショ**
   WAPM-2133TR/1266R・WAB-S1775 の SSID/VLAN/認証/IP 画面をスクショ → Excel[3_スクショ貼付]の該当枠へ。

4. **STEP4 IPネットワーク/機器IPの事前リスト照合**
   Excel[2_IP照合]で 事前(資料) vs 実機 の一致を確認。相違は差分メモ（資料≠実態がこの案件の肝）。
   重点：lounge=**192.168.3.0/24**（設計書の.2は誤記）の最終確認、ゲスト192.168.169.0/24、静的経路=1号館ハブ集約。

5. **STEP5 無管理SWは物理配線のみ（loginしない）**
   2F配電盤のカスケードを物理確認：**段数(hop)／どのポートがどこへ／100Mbps機の混在／ループ防止有無**。写真＋メモ。
   ※生徒網(school)は管理型BS-GSに繋がらず、この無管理カスケード上に乗っている＝オリエン150名一斉アクセスの脆弱点。実測で裏取り。

6. **STEP6 FortiGateは物理結線を最優先**
   図ではRTX→FortiGate→{サーバ・事務所・プリンタ}。**実際に経路に挟まって稼働・ライセンス有効か**を確認。撤去/バイパスなら「サーバが素のLANに露出」＝重大所見（N-02根拠）。生きていれば設定スクショ。

## 作業区分（凡例）

| 区分 | 内容 | 対象 |
|---|---|---|
| ①Config-text | login→テキスト設定を全文バックアップ | RTX1210 / 管理型SW(BS-GS2008P) |
| ②設定スクショ | 管理画面をスクショ→Excel[3] | AP(WAPM/WAB) / FortiGate / サーバ |
| ③物理のみ | loginせず配線・ラベル・段数を確認 | 無管理SW(gs324/EHC/IODATA/LSW) |
| ④探索 | 資料に無い物を探す | ネットワークカメラ / 白ケーブル不明1本の行先 |

## 機器ごとの作業（概要・詳細はExcel）

- ①：RTX1210 NMACRT05（1F事務室）、BS-GS2008P ×5（1F/1F-IDF/2F/3F/4F）
- ②：WAPM-2133TR(1-5/1-7)、WAPM-1266R(1-6/各階)、WAB-S1775(職員室AP)、MKSERVER(FUJITSU)、FortiGate(稼働時)
- ③：NETGEAR gs324×2(52C)、ELECOM EHC-G08/G16MN-HJW(2F)、IODATA BSH-GP08(2F)、BUFFALO LSW6-GT-8EP(2F)
- ④：ネットワークカメラ（教室・要探索）、2F白ケーブル不明1本

## 当日の重点確認（5号館 固有）

- [ ] lounge VLAN3 が実機で 192.168.3.0/24 か（設計書.2との差を最終決着）
- [ ] FortiGate が実際に経路にあるか・ライセンス（撤去/バイパス疑い）
- [ ] 生徒網カスケードの段数・100M混在・ループ（150名ボトルネックの実測）
- [ ] WAB-S1775 のPass（記入漏れ濃厚→3241系/デフォルト試行）＋管理状態
- [ ] ネットワークカメラの有無・接続先（全資料に無し）
- [ ] 2F白ケーブル不明1本の行先
- [ ] L2スイッチ/サーバ/プリンタ2台の実機IP（資料に無し）

## 補助
- 写真の場所特定方式：見出し写真→4カット→付箋ID。詳細 [photo-capture-method.md](photo-capture-method.md)
- 構成の前提：[existing-network-summary.md](existing-network-summary.md)（5号館）・[network-diagram.md](network-diagram.md)・[ip-address-list.md](ip-address-list.md)
- Configテキストは持ち帰り用にUSBへ集約。スクショはExcel[3]へ。
