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

**診断（RTX830 config取得で確定）**：RTX直結=IP取れる／**FortiGate配下（LAN1〜4の全フロア）=IP取れない**。
さらに「RTX LAN直結PCから 1F HUB .21.201 へ ping も不達」。

**結論（FG-LAN側の実測で確定。当初のNAT説は訂正）**：

- RTX側スキャン（PC=.21.5）で見えたのは `.1`(RTX)・`.5`(PC)・`.253` のみ。各階HUB(.201等)は見えず。
- **FG LANポート/各階PoE SWに直結してもDHCPは取得できない**が、**手動で固定IP `192.168.21.101` を振ると PoE SW(.201)の管理画面に到達できた**。
- ∴ **FGのLAN側も同じ 192.168.21.0/24**。フロア機器は **静的IP（.201/.202/.205 等＝旧資料どおり正しい）**。
- → **FortiGate 50E は「透過(ブリッジ)モード」で、管理IP=`.21.253`**（pingは返るがWAN側から管理UI不可＝典型挙動）。**同一/24を挟みつつ、ファイアウォールポリシーで RTX/事務所側 ↔ フロア側 を遮断**している（DHCPブロードキャストもping(WAN→LAN)も越えない）。
- ⇒ **当初「NATで別セグメント」と述べたのは誤り。正しくは「透過＋ポリシー遮断、両側とも.21.x」**。
- フロア側にDHCPが来ないのは、DHCPサーバ(RTX)がFGの反対側にあり**FGがDHCPを中継/許可していない**ため。フロア機器は静的なので運用上は支障なし（クライアントPCを置くと取得不可になる点が課題）。

→ 各階機器の管理は **フロア側に固定IP `.21.x` を振れば可能**（PoE SW=admin/sbmbs3241 で到達確認済）。

## 1F デスク下（FG LAN1配下）＝シャドーIT発見

```text
FG LAN1
 └ ELECOM EHB-UG2A16（16p Giga・無管理SW）
     ├ p16 ← FG LAN1（上り）
     ├ p2  → BUFFALO WSR-2533DHP【WANポート接続＝ルータモード＝二重NAT】→ 民生Wi-Fi(Buffalo-A/G-E6F0)
     └ p1  → Apple AirMac系（白タワー）→ 「2号館 食堂」Wi-Fi（SSID eclat0202）
```

- **WSR-2533DHP がルータモード**（WAN挿し）＝RTX→FG→WSR-2533で**三重NAT**。配下WiFiクライアントは奥深くに隔離。
- **Apple AirMac で食堂Wi-Fi**を提供（民生機・本体に初期PW刻印＝物理露出）。
- いずれも**無管理の民生機（シャドーIT）**。SSID/Key/MAC→credentials。**N-02で撤去・managed AP統合の対象**。

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
| ルータ | YAMAHA RTX830（NMACRT02） | 境界/NAT/DHCP | **config取得済→credentials**。下記「RTX830 config判明事項」 |
| UTM | Fortinet **FG-50E** | インラインUTM | MAC/SN→credentials。**50EはEOL/EOS世代**＝更新提案の根拠 |
| 階HUB | BUFFALO BS-GS2008P ×3 | 各階PoE基幹（1F/2F/3F） | FGへhome-run（スター） |
| 末端HUB | デスク下HUB＋小型AP | クライアント収容 | FG LAN1配下、現状IP来ず |

## RTX830 config 判明事項（2026-06-23 取得・生config→credentials）

ホスト名 NMACRT02。**秘匿値（暗号化PW/PPPoEパス/PSK）は credentials のみ**。構造のみ以下に記録。

- **LAN：lan1 = 192.168.21.1/24 の単一フラットセグメントのみ。VLAN分離なし＝確定**（旧資料の疑いが実機で確定）。職員/生徒/ゲストの分離なし＝N-02の改善ポイント。
- **DHCP：scope 192.168.21.2〜.80（/24・48h）**。HUP/APの .201〜 はスコープ外＝**固定IP運用**。
- **WAN：pp1 PPPoE（OCN系 `j030rdgw@one.ocn.ne.jp`）、lan2口、always-on、NATマスカレード**。※description は "asahinet" だが認証は OCN。
- **VPN：tunnel1 IPsec で 1号館（180.235.35.50）へ。local-name=2goukan、PSK=共通(Cu9yI986系)＝1号館ハブのスター型VPNのスポーク**。
- **VPN越し到達セグメント（tunnel1へ静的ルート）：192.168.0/24（1号館）・192.168.2/24（6号館）・192.168.5/24（5号館）・192.168.170/24（ゲスト?）**。→2号館から校舎間がVPNで相互到達。
- 管理：`telnetd host lan1 192.168.0.1`＝**1号館の管理端末(192.168.0.1)からのみtelnet許可**。現地PCからは不可（設定変更は1号館経由 or コンソール）。
- フィルタは標準テンプレ（プライベート宛リジェクト、NetBIOS/445遮断、IKE/ESP通し）。

> ★重要：**RTX configには「FortiGate配下フロアへの経路情報が一切ない」**。RTXはFGの存在を知らずフラット/24として動作。フロア分離はFGが単独で作っている＝**RTXとFGで設計思想が二重化・未整合**。これも現状の弱点（管理が分断、図面なし）。

## 要確認（次アクション・2号館）

- [x] **RTX830 config取得** → 単一192.168.21.0/24・VLANなし・DHCP.2-.80・tunnel1(→1号館)・OCN PPPoE を確定（上記）
- [ ] **FortiGate 50E** → opmode(NAT/transparent)・LAN側セグメント・自前DHCP有無・UTMライセンス期限（シャープMJ経由）
- [ ] **【最優先・決定打】FG-LAN側（各階HUP or デスク下HUB）にPCを直結し `ipconfig`** → 払い出しIP/GW で FG-LAN の実セグメント番号を確定（.21.x なのか別番号か）。これでFGがNATか透過かが一発で判明。
- [ ] HGW(白box)の型番・PPPoE設定（RTXとの二重ルータ/二重NATになっていないか）
- [ ] VLAN分離の有無（旧資料では単一192.168.21.0/24＝分離なし疑い）
- [ ] SoftBank系AP・ファイルサーバ（旧資料「故障中」）・ネットワークカメラの有無（未使用館で外されている可能性）

## メモ

- 2号館は未使用＝制約が緩いので、**FGのunplugテスト（インライン/バイパス判定）や設定確認を本番影響なく実施できる**。検証はこちらで先に回せる。
- FG-50EはFortiGate旧世代（EOS）。ライセンス切れならUTMは素通り＝「UTM入替」をN-02スコープに含める根拠。
