# 2号館 当日確認手順（2026-06-23）

対象：2号館（専門学校エクラ／仲田2-5-2）。RTX830 NMACRT02・単一セグメント192.168.21.0/24。
記入用Excel：`06_data/credentials/2gou-survey-worksheet.xlsx`（★git管理外・6シート）。
進め方の基本（STEP1〜6・作業区分・物理位置のロケーションコード・写真法）は [5gou-survey-procedure.md](5gou-survey-procedure.md) と共通。本書は2号館固有の重点のみ。

## 進め方（共通STEPの要約）
1. 型番でManaged/Unmanaged仕分け（BS-GS2008P=管理型→login）
2. 既知ID/PWでlogin→Configテキスト保存（RTX `show config` → `2gou_NMACRT02_config.txt`／管理SWはエクスポート＋画面）
3. AP（WAPM-1266R）は設定画面スクショ→Excel[3]
4. IP事前リスト照合（Excel[2]）
5. 無管理SWは物理のみ（2号館は無管理SWは資料上ほぼ無し＝主役は配電盤の配線確認）
6. FortiGateは物理結線を最優先

## 2号館 固有の重点確認
- [ ] **ONU：過去に故障の前例あり**（作業最終日に発覚した経緯）→ **現物・型番・ランプ状態を最優先**で確認。
- [ ] **FortiGate**：実際に経路に挟まって稼働・ライセンス有効か（撤去/バイパス疑い）。
- [ ] **1FのSoftBank AP?**：自販機系フリーWi-Fiの正体を確認（出席登録の経路に絡む）。型番・SSID。
- [ ] **VLAN有無**：資料にVLAN明示なし＝**単一セグメント192.168.21.0/24**かを実機で確認（DHCP .21.2-.80）。
- [ ] **ファイルサーバ**：2023図で「故障中」注記→**実機の稼働可否・用途**。
- [ ] **VPN**：RTX830はtunnel1単一でハブ(1号館)へ＝**スター型**の確認。グローバルIP/PSKは→credentials。

## 機器ごとの作業（概要・詳細はExcel[1]）
- ①Config-text：RTX830 NMACRT02、BS-GS2008P ×3（1F/2F/3F PoE）
- ②スクショ：WAPM-1266R（201/202/301/302）、サーバ、FortiGate（稼働時）
- ④探索：ONU現物、1F SoftBank AP正体、ネットワークカメラ（資料に無し）

## 提案（N-02）確認ポイント
Excel[5_提案確認ポイント]参照（経年/障害実績/電源/回線/ライセンス/無線実測/セキュリティ/ラベリング物量/構成統一/将来要件）。共通解説は [5gou-survey-procedure.md](5gou-survey-procedure.md)。
