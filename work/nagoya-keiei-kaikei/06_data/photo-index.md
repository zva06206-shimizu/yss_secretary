# 写真索引：名古屋経営会計専門学校 現地調査

`raw-photos/` に置いた写真を1行ずつ記録する。これがあると、どの写真から何を読み取るかが整理でき、報告書への転記が速くなる。
※ざっくりで可。撮影者メモ程度でOK。空欄はClaudeが画像を見て埋める。
※**機密（IP/ID/PW/PIN/SSIDキー/グローバルIP/事前共有鍵）は本ファイルに書かない**。秘匿情報の所在は `credentials/device-credentials.md`（git管理外）に集約。本表では「（管理情報あり→credentials参照）」と記す。
※棚卸し実施: 2026-06-16（資料＝仮説ベース。実態は6/23調査で確認）。

## 202603（2026年3月撮影＝1号館install＋全校設計binder。LINE_ALBUM=一号館ネットワーク）

| ファイル名 | 場所/号館 | カテゴリ | 写っているもの（メモ） | 報告書へ転記 |
|---|---|---|---|---|
| IODATA_PINコード.png | 1号館 NAS | 設定画面 | IODATA NAS 接続用PINコード（管理情報あり→credentials参照） | ☑ |
| 20260302-174712.jpg | 1号館 | 構成図 | 「1号館ネットワーク図」手書き寄り。Buffalo AP／ELECOM AP複数、SSID・Wi-Fiキー（管理情報あり→credentials参照） | ☑ |
| LINE_ALBUM_..._1 | 1号館3F | AP/機器 | ELECOM製 天井設置ボックス（「1-3F」ラベル） | ☐ |
| LINE_ALBUM_..._2,_3,_4,_5 | 1号館 | 機器ラベル | ELECOM WAB-M1775-PS 管理者情報シート×複数（型番/SN/MAC、初期admin/admin）（→credentials） | ☑ |
| LINE_ALBUM_..._6 | 1号館 | 構成図/書類 | binderページ（裏写り） | ☐ |
| LINE_ALBUM_..._7 | 1号館 | 機器ラベル/設定 | YAMAHA RTX1210(NMACR T05) 機器写真＋Port List(VLAN)、login/admin（→credentials） | ☑ |
| LINE_ALBUM_..._8 | 1号館 | 設定画面 | FortiGate/Secure Filter ACL表 2/2（IP・ポリシー）（→credentials） | ☑ |
| LINE_ALBUM_..._9 | 1号館 | 設定画面 | FortiGate/ACL・ポリシー表（サブネット・ポート・VPN）（→credentials） | ☑ |
| LINE_ALBUM_..._10,_13 | 1号館 | 構成図 | **1号館 全体図（2024.5.27 エンジニアリンク中部）**。NTT終端→FortiGate→RTX830→コアSW LSW6-GT-8NS→各階SW(2F-6F)→ELECOM WAB-M1775-PS(教員用/教室用)、WAPM-1266R、192.168.1.0/24 | ☑ |
| LINE_ALBUM_..._11 | 1号館 | 機器ラベル | ELECOM WAB-M1775-PS シート（型番/SN/MAC）（→credentials） | ☑ |
| LINE_ALBUM_..._12,_14 | 1号館 | 設定画面 | YAMAHA RTX830(NMACRT01) フル設定（Port/IP/Static Route/DHCP/PP=asahinet PPPoE/NAT）＋2F BUFFALO WAPS-1266(SSID igou-jimu)（→credentials） | ☑ |
| IMG_7841,7842 | 全校 | 設定画面 | RTX1210(NMACRT05) IPsecトンネル＋Secure Filter ACL、Other Setting(DNS/telnet/NTP)（→credentials） | ☐ |
| IMG_7844 | 6号館 | 構成図 | **6号館 全体図**（中部, 2024.5.27）。WAPM-1266R各階(3F-8F)、BS-GS2016P、FortiGate、RTX1210、EHC-F08PA-B/F05PA-B | ☑ |
| IMG_7847,7851 | 全校 | 構成図 | **全校間マップ**。1号館/2号館エクラ/5号館1F・2F/6号館をVPN接続。ファイルサーバ、FortiGate-50E、RTX1210/RTX830、MKSERVER | ☑ |
| IMG_7848,7850 | 全校 | 構成図 | 論理構成図「アクセス許可の通信」。館別VLAN(教職員/生徒/分離なし)、IPSecリンク | ☑ |
| IMG_7853 | 5号館 | 書類 | 動作概要/セグメント間通信制御マトリクス(Office/School/Lounge/Internet許可表) | ☐ |
| IMG_7856,7860,7862,7864 | 全校 | 設定画面 | 各RTX(NMACRT01/02/05)のSecure Filter ACL・IPsec/事前共有鍵（→credentials） | ☐ |
| IMG_7859 | 全校 | 設定画面 | RTX830(NMACRT01)詳細(PP=ISP auth、IPsec PSK)（→credentials） | ☐ |
| IMG_7865 | 5号館 | 構成図 | **5号館 ネットワーク構成図**。RTX1210、VLAN1 Office/VLAN2 School/VLAN3 Lounge、MKSERVER、各室PC/プリンタ | ☑ |
| IMG_7868 | 6号館 | 構成図 | **6号館 ネットワーク図(2020.07 SBM)**。WAPM-1266R各階3F-8F＋BS-GS2016P、SSID/Wi-Fiキー（→credentials） | ☑ |
| IMG_7870 | 6号館 | 構成図 | 6号館 VLAN環境構築図。RTX1210、各階AP、VLAN1/7/8、DHCPスコープ（→credentials） | ☑ |
| IMG_7843,7845,7846,7849,7852,7854,7855,7857,7858,7861,7863,7866,7867,7869 | 全校 | binderページ | 上記binderの間ページ・重複・裏写り。新規情報少 | ☐ |
| S__3604503,3604504 | 全校 | 機器ラベル | ELECOM WAB-M1775-PS 管理者情報シート（別個体SN/MAC）（→credentials） | ☐ |
| S__3604509 | 1/2号館 | 設定画面 | BUFFALO WAPS-1266 設定(SSID igou-jimu, 192.168.0.242)（→credentials） | ☐ |
| S__3604512 | 全校 | 設定画面 | RTX1210(NMACRT05) Port List(office/school/lounge)、admin（→credentials） | ☐ |
| S__3604506,3604515 | 全校 | 設定画面/ラベル | RTX830(NMACRT01)設定シート(2024.5.27更新, 鮮明)＋ELECOMラベル（→credentials） | ☐ |
| S__3604505,3604507,3604508,3604510,3604511,3604513,3604514 | 全校 | binder/ラベル | binderページ・ELECOM/AP ラベルシートの連番。新規情報少（一部→credentials） | ☐ |

## 202606/2020-2023（2020〜2023の「ネットワーク環境状況概要」binder。2/5/6号館VPN構築時）

| ファイル名 | 場所/号館 | カテゴリ | 写っているもの（メモ） | 報告書へ転記 |
|---|---|---|---|---|
| IMG_2919 | 全校 | 書類 | binder表紙「ネットワーク環境状況概要 2023.1現在」 | ☐ |
| IMG_2920 | 全校 | 構成図 | **全拠点トポロジ**。1/2号館エクラ/5号館1F・2F/6号館。各館にFortiGate-50E＋YAMAHA(RTX830 or RTX1210)＋ファイルサーバ。2号館エクラserver「故障中」 | ☑ |
| IMG_2921 | 全校 | 書類 | 「固定IPによる4拠点VPN構築」方針 | ☑ |
| IMG_2922 | 全校 | 書類 | FortiGate-50E 製品/提案シート（5年AV/IPS/Web等） | ☐ |
| IMG_2925 | 全校 | 構成図 | セグメント/VLANマップ。館別サブネット＋IPSecリンク、凡例(教職員/生徒/分離なし) | ☑ |
| IMG_2928 | 全校 | 機器一覧 | ルータ一覧: 1号館RTX830(NMACRT01,2020/2)、2号館RTX830(NMACRT02,2020/3)、5号館RTX1210(NMACRT05,2017/12)、6号館RTX1210(Meikei_BD6H 2F給湯室盤内)（管理IPあり→credentials） | ☑ |
| IMG_2931 | 5号館 | 設定画面 | NMACRT05 Secure Filter/Other Setting（DNS/syslog/global IP）（→credentials） | ☐ |
| IMG_2934,2935 | 1号館 | 設定画面 | NMACRT01 config(DHCP/ntp/syslog)、RTX830詳細(Port/VLAN/DHCP/IPsec)（→credentials） | ☐ |
| IMG_2937 | 6号館 | 設定画面 | RTX1210 config(他拠点IPsecトンネル)（→credentials） | ☐ |
| IMG_2940 | 2号館 | 設定画面 | NMACRT02 Secure Filter ACL＋Other Setting（→credentials） | ☐ |
| IMG_2943 | 6号館 | 設定画面 | 6号館RTX1210 Port/VLAN/IPsec表（→credentials） | ☐ |
| IMG_2946 | 全校 | 設定画面 | IPsec ike 事前共有鍵/filter dump（→credentials） | ☐ |
| IMG_2949 | 5号館 | 構成図 | 5号館ネットワーク構成図。RTX1210@1F事務室、VLAN Office/School/Lounge、2F各室＋MKSERVER | ☑ |
| IMG_2950 | 5号館 | 書類 | アドレス設計表(Office/School/Lounge各/24、GW、DHCP範囲、VLAN ID 1/2/3) | ☑ |
| IMG_2952,2955 | 5/6号館 | 書類 | DHCP/IP割当リスト（多数IP→credentials） | ☐ |
| IMG_2958 | 5号館 | 書類 | 5号館AP一覧(階別): WAPM-2133TR/1266R、BS-GS2008P（SSIDキー/IP/admin→credentials） | ☑ |
| IMG_2961,2962,2964,2967 | 5号館(MKSERVER) | 書類 | サーバ構築doc(Confidential, 2023/1/19, 大野)。WinServer2019/PowerAct Pro/ServerView/RAID/ファイル共有 | ☑ |
| IMG_2970 | 6号館 | 書類 | 6号館AP一覧3F-8F: WAPM-1266R、BS-GS2016P。「5Fより各階へ幹線」（SSID/Key/SN/IP→credentials） | ☑ |
| IMG_2973 | 2号館 | 構成図 | **2号館ネットワーク図(2020.07 SBM)**。BS-GS2008P PoE各階、WAPM-1266R(2F/3F)、1FはSoftBank AP（SSID/Key→credentials） | ☑ |
| IMG_2974 | 2号館 | 書類 | 2号館AP一覧1F-3F: BS-GS2008P、WAPM-1266R（SSID/Key/IP/admin→credentials） | ☑ |
| IMG_2976 | 全校 | 書類 | 館別AP詳細設定(SSID guest/student/teacher、SN、RTX830 admin)（→credentials） | ☐ |
| IMG_2979 | 5号館 | 書類 | Zetta「リモコン倶楽部Z School Edition LT v11」ライセンス(1+28, 2020/7-2021/6)（シリアル/住所→credentials） | ☑ |
| IMG_2923,2924,2926,2927,2929,2930,2932,2933,2936,2938,2939,2941,2942,2944,2945,2947,2948,2951,2953,2954,2956,2957,2959,2960,2963,2965,2966,2968,2971,2972,2975,2977,2978 | 全校 | binder連番 | 上記binderの間ページ群（config dump・割当表・診断の連番）。代表ページで把握済、個別転記不要 | ☐ |

## 202606/2024（2024年 エンジニアリング中部 survey binder。5号館・6号館調査）

| ファイル名 | 場所/号館 | カテゴリ | 写っているもの（メモ） | 報告書へ転記 |
|---|---|---|---|---|
| IMG_8959 | 5号館 | 構成図 | **5号館 全体図(1F-4F)**。1F: RTX1210＋FortiGate。各階Buffalo BS-GS2008P/GS2016P、教室AP WAB-S1775/WAPM-1266R/2133TR、netgear-gs324、ELECOM EHC-G08/G16MN-HJW、プリンタRICOH SG-720/APEOS C3070、サーバ、NTT終端 | ☑ |
| IMG_8960 | 5号館1F | 機器一覧 | RTX-1210、FortiGate(UTM)、BS-GS2008P、WAPM-2133TR/1266R、WAB-S1775、FUJITSU PRIMERGY TX1310 M5(サーバ)（IP→credentials） | ☑ |
| IMG_8961 | 5号館2F | 機器一覧 | BS-GS2008P、I-O-DATA BSH-GP08、NTT VOIP終端、WAPM-1266R×4、WAB-S1775×4、LSW6-GT-8EP、EHC-G08/G16MN-HJW、NETGEAR gs324×2（IP→credentials） | ☑ |
| IMG_8962,8963 | 5号館3F/4F | 機器一覧 | BS-GS2008P(IDF HUB)、WAPM-1266R×4(53A-D/54A-D)（IP→credentials） | ☐ |
| IMG_8964 | 6号館 | 配線写真 | 1F配電盤/1Fサーバー室。WAN配線、HUB、サーバ筐体(1-1..1-9) | ☑ |
| IMG_8965 | 5号館 | 配線写真 | 2F配電盤配線。「生徒用AP PoEHUB」。白3本(→RTX1210/→2C教室/→不明)、青→1F PoE | ☑ |
| IMG_8966,8967 | 5号館 | 設定画面 | RTX1210(NMACRT05) Port List＋**VLAN表(VLAN1 office/VLAN2 school/VLAN3 lounge)**、DHCP/PP/NAT（→credentials） | ☑ |
| IMG_8968 | 5号館 | 設定画面 | RTX1210 2/2: IPsecトンネル、VLAN別Secure Filter ACL、syslog/dns（事前共有鍵→credentials） | ☐ |
| IMG_8969,8970,8971,8974,8975 | 5号館 | 機器ラベル | AP仕様シート: WAPM-2133TR(1F-1/1F-2)、WAPM-1266R(1F職員室/2F-4)。VLANポート表あり（→credentials） | ☐ |
| IMG_8977 | 5号館 | 機器ラベル | ELECOM WAB-S1775。SSID nagoyakeiei-ap/-guest（ゲストNW定義あり）（→credentials） | ☑ |
| IMG_8980 | 5号館 | 書類 | ラウンジNW(192.168.3.0/24)ホスト一覧 | ☐ |
| IMG_8983 | 6号館 | 構成図 | **6号館 全体図(2F-8F)**。2F: FortiGate＋RTX1210。BS-GS2016P(5F)、各階WAPM-1266R(教員)＋ELECOM EHC-F05PA-B/F08PA-B＋WAPM-1166D(生徒) | ☑ |
| IMG_8986 | エクラ/1号館 | 機器一覧 | 3F-8F: WAPM-1266R、BS-GS2016P、EHC-F05PA-B/F08PA-B、WAPM-1166D（「1号館/エクラ」参照あり＝対象外館に言及）（IP→credentials） | ☑ |
| IMG_8987 | 6号館 | 配線写真 | 2F給湯室(2T-1)配線、2F事務所(2-8..2-10) | ☑ |
| IMG_8988,8989 | 6号館 | 配線写真 | IDF: 3T-1/4T-1/6T-1「機材無し」、5T-1/7T-1/8T-1に機材(EHC-F0xスイッチ) | ☑ |
| IMG_8990,8998 | 6号館 | 書類 | 教員NW(192.168.2.0/24)割当・DHCP | ☐ |
| IMG_8992 | 6号館3F | 機器ラベル | WAPM-1166D(3F-1)。SSID NGOKAJP36（→credentials） | ☐ |
| IMG_8993,8995 | 6号館3F | 機器ラベル | WAPM-1266R(3F-1, SSID nkk6g-ap)（→credentials） | ☐ |
| IMG_9001 | 6号館8F | 書類 | 8Fネットワーク(192.168.8.0/24)・DHCP(生徒NW) | ☐ |
| IMG_9002 | 6号館 | 設定画面 | YAMAHA RTX830(NMACRT02) Port/IP/Static/DHCP/NAT(192.168.21.0/24)（→credentials） | ☑ |
| IMG_9003 | 6号館 | 設定画面 | RTX1210(Meikei_BDGH 2/2) IPsec/Secure Filter ACL/syslog（事前共有鍵→credentials） | ☑ |
| IMG_8972,8973,8976,8978,8979,8981,8982,8984,8985,8991,8994,8996,8997,9000(欠番含む) | 5/6号館 | 機器ラベル/書類連番 | AP仕様シート・IP割当表の連番。代表ページで把握済、個別転記不要 | ☐ |

## 20260623（6/23 当日撮影＝5号館1F ルータ周り。ラック/結線/機器ラベル/実機トレース。raw-photos/20260623-survey/5gou/）

> 当日iPhone連番を「ファイル名」に記入→クロエが `5-1F-...` にリネーム。機微（S/N・MAC・IP・PW）が写るものは raw=git管理外のまま、台帳実値は `credentials/device-credentials.md` へ。
> ★この14枚で**5号館1Fコアの物理が確定**：WAN=RTX **LAN2**(赤/2F ONU由来)、office=RTX LAN1→FG-40F(インライン透過)→LSW2(100M)→機器、サーバ=EHC経由でFG配下。**I-O DATA USB-HDD(バックアップ)を新規発見**。

| ファイル名 | 場所 | カテゴリ | 写っているもの | リネーム案 | 転記 |
|---|---|---|---|---|---|
| (記入) | 5-1F | rack | **Buffalo LSW2-TX-16NSRR LEDパネル**。凡例=**100/10/ACT・FD/COL＝Fast Ethernet(100M)確証**。ポート1,2,5-8他 多数Link＝office主幹線が100Mで稼働 | 5-1F-lsw2-led | ☑ |
| (記入) | 5-1F | rack | **ラック全景(縦)**。FG-40F(LED点灯)／RTX1210(青)／ONU／電源タップ | 5-1F-rack-overview | ☑ |
| (記入) | 5-1F | cabling | **FG黄(internal)→LSW2** トレース | 5-1F-fg-to-lsw2 | ☑ |
| (記入) | 5-1F | server | **ELECOM EHC-F05PA-JB**(POWER/LOOP/1-5 LED)＋サーバ周り。下段にONU白箱 | 5-1F-ehc-server | ☑ |
| (記入) | 5-1F | rack | **OMRON BN50T(UPS, S/N AOW17109137700G→cred)＋Fujitsu PRIMERGY TX1310 M5**。下段=ONU白箱＋小型機＋予備ケーブル | 5-1F-ups-server | ☑ |
| (記入) | 5-1F | cabling | **RTX1210 LAN1ポート**。port1=黄「元:RTX1210 LAN1:1 office」、port2/3=青 | 5-1F-rtx-lan1 | ☑ |
| (記入) | 5-1F | device-label | **FortiGate FG-40F 底面ラベル**。Model FG-40F／SN FGT40FTK23001296／MAC 84:39:8F:79:04:EA／製造2023-03-07／HWID／PN（→cred） | 5-1F-fg-label | ☑ |
| (記入) | 5-1F | cabling | **RTX1210 背面ラベル**。LAN2:WAN(赤)／LAN1:2 school／LAN1:3 lounge | 5-1F-rtx-labels | ☑ |
| (記入) | 5-1F | cabling | **RTX1210 背面**。WANラベル＋LAN2(赤・Link点灯)／ISDN S/T／microSD＝**WANはLAN2**(config `pppoe use lan2` と一致) | 5-1F-rtx-wan-lan2 | ☑ |
| (記入) | 5-1F | cabling | **RTX1210 背面**。WAN(赤)＋LAN1:1 office/1:2 school/1:3 lounge ラベル＋結線 | 5-1F-rtx-lan1-labels | ☑ |
| (記入) | 5-1F | rack | **RTX1210(青)側面**。STANDBY/ON電源＋予備ケーブル束＋白箱(終端機?要確認) | 5-1F-rtx-side | ☐ |
| (記入) | 5-1F | device-label | **I-O DATA HDJA-UT2RW(2TB USB-HDD, S/N 11UD0231653W→cred)**＝サーバ外付けバックアップと推定。**新規発見** | 5-1F-iodata-hdd | ☑ |
| (記入) | 5-1F | server | **PRIMERGY 背面**。NIC1本(青・Link点灯)＋手書き連番ラベル(1-7)＋鍵。VGA/DP/USB | 5-1F-server-rear | ☑ |

### 2F PoE 配電盤内（WAN入口＋教員/生徒 PoE分配）

> ★WANチェーン確定：**光 → GE-ONU → OG410Xa(NTT HGW/ひかり電話) → 赤ケーブル → 1F RTX1210 WAN(LAN2)**。OG410XaはPPP=消灯(=RTXがPPPoE終端)・VoIP/WAN=点灯。
> ★2F配電盤は**教員系と生徒系でPoEスイッチが物理分離**：BS-GS2008P(2F-PoE=教員/office/Gigabit)と「生徒用AP PoEHUB」(生徒/school)。

| ファイル名 | 場所 | カテゴリ | 写っているもの | リネーム案 | 転記 |
|---|---|---|---|---|---|
| (記入) | 5-2F | panel | **2F配電盤 全景**。扉に生徒用AP PoEHUB、盤内にOG410Xa/ONU/BS-GS2008P＋空調ダクト | 5-2F-panel-overview | ☑ |
| (記入) | 5-2F | device-label | **NTT GE-ONU**(光終端)。認証/UNI/光回線/登録/電源 緑点灯 | 5-2F-geonu | ☑ |
| (記入) | 5-2F | device-label | **NTT OG410Xa(HGW/ひかり電話)** LEDパネル。POWER/CONFIG/VoIP/WAN=緑、**PPP=消灯**＝RTXがPPPoE。2018/12製 | 5-2F-og410xa-led | ☑ |
| (記入) | 5-2F | device-label | **OG410Xa 背面ラベル**。MAC 6C:E4:DA:39:FE:6F／製番H8Z124568K10／認証DE140113003（→cred） | 5-2F-og410xa-label | ☑ |
| (記入) | 5-2F | cabling | **OG410Xa 側面**。**赤ケーブル(WAN)＝RTXへの上り**＋電話系パンチダウン | 5-2F-og410xa-wan | ☑ |
| (記入) | 5-2F | device-label | **BUFFALO BS-GS2008P**「8-Port Gigabit Switch・PoE」(2F-PoE黄ラベル)＝教員/office系・**Gigabit** | 5-2F-bsgs2008p-label | ☑ |
| (記入) | 5-2F | cabling | **BS-GS2008P(2F-PoE)** 青ケーブル＝52A/52B/52C/52D(教員AP)＋**1F PoE/3F PoE(幹線)**。LED多数Link | 5-2F-bsgs2008p-cabling | ☑ |
| (記入) | 5-2F | device-label | **「生徒用AP PoEHUB」**(navy)前面LED(POWER緑/LINK/PoE) | 5-2F-student-poehub-led | ☑ |
| (記入) | 5-2F | cabling | **生徒用AP PoEHUB** 白ケーブル＝生徒用AP 52A/52C＋**1F〜2F幹線**(CAT5e NIPPON SEISEN) | 5-2F-student-poehub-cabling | ☑ |
| (記入) | 5-2F | device-label | **生徒用AP PoEHUB 本体ラベル＝I-O DATA BSH-GP08MB**(8p Gigabit PoE/110W)。MAC 50:41:B9:42:00:B8／S/N 11VS00882KD。**IPスキャン .1.5(school/Hydra web)と一致＝管理機ありsmart SW**（→cred） | 5-2F-student-poehub-label | ☑ |

### 1F PoE 配電盤内（教員/office縦系の起点＝RTXへ合流）

> ★1F-PoE(BS-GS2008P/Gigabit・黄ラベル「2F-1FPoE」)＝教員/office APの1F集約。**1F AP(事務所/ラウンジ/休憩室=.5.11-13)＋上り「2F PoE」(教員カスケードへ)＋「1F ルーター」(=RTXへ合流)**。
> ★含意（要RTXポート確認）：APカスケードは「1F ルーター」でRTXへ合流＝**FG→LSW2ブランチとは別系統**。→ **FGの実保護範囲はLSW2側(サーバ等)に限られ、AP/カスケード系はFGを通らない可能性**。office VLANは1つのL2なので疎通はするが、FG検査対象から外れる。
> ★注意：「ラウンジAP」は設置場所名で**office VLAN1(.5.12)**。lounge VLAN3(.3.x)とは別。

| ファイル名 | 場所 | カテゴリ | 写っているもの | リネーム案 | 転記 |
|---|---|---|---|---|---|
| (記入) | 5-1F | panel | **1F-PoE BS-GS2008P 全景**(壁付・黄ラベル2F-1FPoE)＋青ケーブル束 | 5-1F-poe-overview | ☑ |
| (記入) | 5-1F | cabling | **1F-PoE ケーブルラベル**＝職員室AP/休憩室AP/ラウンジAP/(カウンター)AP＋**2F PoE(上)＋1F ルーター(RTXへ)** | 5-1F-poe-cabling-labels | ☑ |
| (記入) | 5-1F | device-label | **1F-PoE 前面LED/ポート**(BS-GS2008P・Gigabit・port1-4/7 Link) | 5-1F-poe-ports | ☑ |

### 3F 配電盤内（教員/office 縦系＝BS-GS2008Pカスケード）

> ★教員/office側の縦系は **BS-GS2008P(Gigabit)を 1F→2F→3F→4F でカスケード(数珠つなぎ)**。各階の青ケーブルに「2F PoE / 4F PoE」等の上下トランクラベル。＝スター(home-run)でなく**直列＝単一経路・冗長なし**。

| ファイル名 | 場所 | カテゴリ | 写っているもの | リネーム案 | 転記 |
|---|---|---|---|---|---|
| (記入) | 5-3F | panel | **3F配電盤 全景**。端子台 53A-D/54A-C(教室分配)＋BS-GS2008P(3F-PoE)＋Aichi UWC-4F(CATV 4分岐器)＋電話/構内端子台＋電源 | 5-3F-panel-overview | ☑ |
| (記入) | 5-3F | device-label | **BUFFALO BS-GS2008P(3F-PoE)** 前面LED。教員/office・Gigabit | 5-3F-bsgs2008p | ☑ |
| (記入) | 5-3F | cabling | **3F-PoE 青ケーブル**＝53A/53B/53C/53D(教員AP)＋**4F PoE(上トランク)/2F PoE(下トランク)**＝カスケード裏取り | 5-3F-cabling-labels | ☑ |
| (記入) | 5-3F | cabling | **縦系riser(床貫通)**。各階間の幹線束＋空き管の現況＝home-run化/光化の可否材料 | 5-3F-riser | ☑ |

### 4F 配電盤内（教員カスケードの最上＝終端）

> ★4F-PoE(BS-GS2008P)は下りトランク「3F PoE」のみ・上りなし＝**教員/office縦系は 1F→2F→3F→4F で終端**。全階Gigabit BS-GS2008Pのカスケード確定。

| ファイル名 | 場所 | カテゴリ | 写っているもの | リネーム案 | 転記 |
|---|---|---|---|---|---|
| (記入) | 5-4F | panel | **4F配電盤 全景**。端子台 54A-D＋BS-GS2008P(4F-PoE)＋Aichi UWC-4F(CATV)＋コンセント | 5-4F-panel-overview | ☑ |
| (記入) | 5-4F | device-label | **BUFFALO BS-GS2008P(4F-PoE)** 前面LED。教員/office・Gigabit | 5-4F-bsgs2008p | ☑ |
| (記入) | 5-4F | cabling | **4F-PoE 青ケーブル**＝54A/54B/54C/54D(教員AP)＋**3F PoE(下トランクのみ＝終端)** | 5-4F-cabling-labels | ☑ |
| (記入) | 5-4F | cabling | **縦系riser(床貫通)** | 5-4F-riser | ☐ |

## 撮影サマリ
- 総枚数：約160枚（202603 約57＋PIN png／2020-2023 60／2024 44）。
- 主に撮れたもの：**設計binder（構成図・VLAN/アドレス設計・機器一覧・各機器の設定シート/ACL/IPsec）が大半**。物理ラックの全景・パッチパネル写真は少。2024 binderに一部、配電盤・IDFの配線写真あり。機器ラベルシート（ELECOM/BUFFALO AP）多数。
- 撮れなかった・不明だったもの：
  - **ネットワークカメラ**：どの年代のbinderにも写っていない（5号館教室の「資料にないカメラ」は資料に存在せず＝6/23実機確認必須）。
  - **L2スイッチ(BS-GS2008P/2016P, NETGEAR, EHC)のポート別VLANタグ設定**：専用シートなし＝幹線トランク構成が資料化されていない（6/23確認）。
  - 物理ラック全景・配線盤の現況写真（押し込み状態の現物）。
- 注意：202603と2024のbinderはともに「エンジニアリング/エンジニアリンク中部」作成。資料間で2号館serverの稼働状況・機器更新に差分があり、資料が実態と一致する保証はない（要実機確認）。
