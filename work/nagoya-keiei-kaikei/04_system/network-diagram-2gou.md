# 2号館 ネットワーク現状図（2026-06-23 現地で確定）

> ※本ファイルは git 管理対象。**ID/PW/PIN/PSK/SSIDキー/MAC/SN/グローバルIP実値は載せない**（→ `06_data/credentials/`）。
> ※状態＝**通電・稼働中**（館は未使用だが機器は生きている）。出典＝1F配電盤の実機写真＋目視トレース（raw-photos/20260623-survey、git管理外）。
> ※旧・仮説版（写真からの想定）は本コミットで確定値に置換。確定でない項目は「要確認」に残置。全館版は [network-diagram.md](network-diagram.md)。

---

## 確定トポロジ（1F配電盤の配線を目視トレースで確定）

```text
光
 │
[NTT GE-ONU]                （認証/UNI/光回線/電源 点灯）
 │ WAN
[白いボックス＝NTT HGW]      （POWER/INIT/ALARM/CONFIG/PPP 点灯 ＝ PPPoE終端・ひかり電話）
 │ LAN  →  RTX WAN
[YAMAHA RTX830]              （ルータ/境界・DHCP）
 │ LAN1:2
[FortiGate 50E] WAN1         （UTM・インライン＝全フロアの手前）
 ├ LAN2 → 1F PoE HUB（BUFFALO BS-GS2008P）→ riser → 1F各部屋
 ├ LAN3 → 2F PoE HUB（BUFFALO BS-GS2008P）→ 上部配管(riser) → 2F各部屋（ラベル 201/202）
 ├ LAN4 → 3F PoE HUB（BUFFALO BS-GS2008P）→ 上部配管(riser) → 3F各部屋（ラベル 301/302）
 └ LAN1 → 配電盤 下口 → 外 → デスク下HUB（＋小型AP）
```

## 現地での疎通テスト結果（重要）

| 接続点 | DHCP IP取得 | 解釈 |
|---|---|---|
| **RTX LAN 直結** | **取得できる** | RTXのDHCPは生きている＝RTX-LANセグメントは正常 |
| 各階AP（無線）経由 | 取得できない | FG配下フロア系にDHCPが届いていない |
| デスク下HUB＋小型AP（FG LAN1配下） | 取得できない | 同上、FG配下は全系でIP来ず |
| 無線 SSID `nkk2g-ap` | 接続(アソシエーション)は可能 | キー→credentials。電波は出ているがIPは別問題 |

**診断（仮説）**：RTX直結=IP取れる／**FortiGate配下（LAN1〜4の全フロア）=IP取れない**。
→ FortiGate がインラインで境界になっており、**RTXのDHCPがFGを越えてフロア側へ渡っていない**。
考えられる形：①FGがNATモードでLAN側は別セグメント（例 192.168.1.x）かつFG自前DHCPが無効、または②未使用館ゆえフロア末端が外され/停止、DHCP提供が止まっている。
→ いずれも **RTX830とFortiGateのconfigを取れば確定**。

## 5号館との決定的な違い（提案に直結）

| 観点 | 2号館（今日確定） | 5号館 |
|---|---|---|
| FortiGateの位置 | **インライン＝全フロアの手前**（WAN1=RTX、LAN2/3/4=各階HUB） | バイパス気味（FGはLSW2枝のみ保護、AP系はRTX直結でFG迂回） |
| フロア基幹 | **スター**（各階HUBがFGへhome-run） | カスケード（1F→2F→3F→4F数珠つなぎ・SPOF） |
| 評価 | **N-02で5号館に提案したい目標形が既にある** | 巻き直し対象 |

→ **2号館は同じ学校内に既にある「スター＋UTMインライン」の実例**。N-02提案で「2号館はこの構成、5号館も同じ形に揃える」と説明でき、説得材料になる。

## 重要：UTMベンダー判明

FortiGate脇の赤いステッカー「UTMに関するお問い合わせ **シャープマーケティングジャパン（株）** 0570-00xx19」＝5号館の同型ステッカーと一致。
→ **FortiGate（5E/40E）の導入・管理ベンダーはシャープMJ**。管理PW・UTMライセンス状況は学校経由でシャープMJに照会するのが正規ルート（ブルートフォース不要）。

## 確認できた機器

| 機器 | 型番 | 役割 | 備考 |
|---|---|---|---|
| 光終端 | NTT GE-ONU | 光→UNI | 点灯=回線生きている |
| HGW | NTT 白box（PPP点灯） | PPPoE終端/ひかり電話 | ONU WAN→HGW、HGW LAN→RTX WAN |
| ルータ | YAMAHA RTX830 | 境界/NAT/DHCP | config未取得（admin/sbmbs で取得予定） |
| UTM | Fortinet **FG-50E** | インラインUTM | MAC/SN→credentials。**50EはEOL/EOS世代**＝更新提案の根拠 |
| 階HUB | BUFFALO BS-GS2008P ×3 | 各階PoE基幹（1F/2F/3F） | FGへhome-run（スター） |
| 末端HUB | デスク下HUB＋小型AP | クライアント収容 | FG LAN1配下、現状IP来ず |

## 要確認（次アクション・2号館）

- [ ] **RTX830 config取得（admin/sbmbs）** → セグメント番号(192.168.21.x?)・DHCPスコープ・LAN1:2の扱い・tunnel1(→1号館)・VLAN分離有無 → credentialsへ
- [ ] **FortiGate 50E** → opmode(NAT/transparent)・LAN側セグメント・自前DHCP有無・UTMライセンス期限（シャープMJ経由）
- [ ] FG越えでDHCPが止まる原因の切り分け：FG LAN側に固定IPで直結し、FG管理IP（FG-50E既定 192.168.1.99 等）へHTTPS/ping → NATで別セグメントか判定
- [ ] HGW(白box)の型番・PPPoE設定（RTXとの二重ルータ/二重NATになっていないか）
- [ ] VLAN分離の有無（旧資料では単一192.168.21.0/24＝分離なし疑い）
- [ ] SoftBank系AP・ファイルサーバ（旧資料「故障中」）・ネットワークカメラの有無（未使用館で外されている可能性）

## メモ

- 2号館は未使用＝制約が緩いので、**FGのunplugテスト（インライン/バイパス判定）や設定確認を本番影響なく実施できる**。検証はこちらで先に回せる。
- FG-50EはFortiGate旧世代（EOS）。ライセンス切れならUTMは素通り＝「UTM入替」をN-02スコープに含める根拠。
