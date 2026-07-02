# 株価データ源 比較（顧客提供・日中分足の前提で検証）

作成: 2026-07-02 / 調査: Web一次情報ベース（出典URL付き）

## 目的

Lark Base に株価を自動蓄積・モニターする仕組みを、**顧客に「設定方法ごと」提供するサービス**にできるか。
特に「日中・数分足（intraday minute bars）」を、**正規ライセンス・安価・PC常時起動不要**で実現できるかを検証。

## 最重要の結論

- **「顧客提供 × 日中リアルタイム数分足 × 安価 × 合法再配布」は、同時に満たすデータ源が現状ない。**
- **再配布・商用が公式に許諾されているのは J-Quants（JPX公式）だけ。** ただし J-Quants の分足は
  **当日16:30頃のバッチ確定＝リアルタイムではない**。
- yfinance は **Yahoo規約で再配布・商用が明確に禁止**。自分用には使えるが、顧客提供の土台にできない
  （20分遅延という弱点より、この再配布禁止の方が本質的な壁）。

## 分岐（ここで構成が全部決まる）

| 顧客要件 | 正規×安価×PC常時起動不要を同時に満たすか | 採るべき道 |
|---|---|---|
| 当日夕方に分足がまとまればいい（引け後の蓄積・分析） | ○ | **J-Quants 外部配信（¥13,200/月）＋クラウドバッチ蓄積** |
| 日中にリアルタイム（数分遅延）の分足が要る | ✕（同時不可） | 海外APIの東証intraday対応を要確認 or kabu（PC常時起動＝振り出し） |

## 比較表

| データ源 | 分足の有無/遅延 | 料金（月額） | 商用・再配布 | PC常時起動 |
|---|---|---|---|---|
| **J-Quants API（JPX公式）** | 1分足あり。**リアルタイム不可・当日16:30頃バッチ**。過去2年保持 | 分足アドオン：個人¥220／法人自己利用¥4,400／**外部配信¥13,200**（＋基本プラン別） | **公式に明確＝可**（自己利用/外部配信の料金区分あり） | **不要**（REST・クラウド完結） |
| kabuステーションAPI（三菱UFJ eスマート証券） | リアルタイム時価・板（WebSocket push）。**足は自前でtickから生成** | API無料だがProfessional以上要（月額要確認） | **再配布可否は公式明記なし＝要確認** | **必須**（アプリ常駐・localhost:18080） |
| 楽天 MarketSpeed II RSS（現行） | リアルタイム分足可（Excelアドイン経由） | 取引口座前提 | 再配布/商用は不透明＝要確認 | **必須**（MS2＋Windows＋Excel、クラウド不可） |
| yfinance / Yahoo Finance | 日本株分足取れるが**15〜20分遅延・非公式・429頻発** | 無料（非公式） | **Yahoo規約で再配布・商用を明確に禁止** | 不要（ただし規約リスク大） |
| Twelve Data | 東証（XJPX）掲載。分足対応だが**日本株intradayの粒度/プラン要確認** | Basic無料／Grow$79／Pro$229／Ultra$999（東証はPro以上） | 有償で商用の建付け、**日本株再配布条件は要確認** | 不要 |
| Alpha Vantage | 分足あるが**主に米国。日本株intraday要確認** | 無料〜$50前後〜 | 有償で商用の建付け、要確認 | 不要 |
| EODHD | 1/5分intradayあるが**取引所リストに東証が見当たらず＝非対応の可能性大** | Basic €19.99〜 | 有償で商用可 | 不要 |
| Polygon | 分足・tick・WebSocketに強いが**基本は米国。日本株対応確認できず** | 無料〜$199+ | 有償で商用可 | 不要 |

## 現実的な選択肢（トレードオフ）

**案A：J-Quants「外部配信」＋クラウドバッチ蓄積（正規・最安・低運用）**
毎日16:30以降にREST取得→蓄積→顧客提供。分足外部配信¥13,200/月＋基本プラン。**常時起動不要・再配布が唯一明確に合法**。
弱点＝**リアルタイムではない**（当日夕方確定）。引け後の蓄積・分析・翌日判断なら第一候補。

**案B：kabuステーションAPI＋クラウドVPSでアプリ常駐＋自前分足生成（準リアルタイム）**
真のリアルタイム/日中数分足は可能。だが①VPS上のGUIアプリ常駐で運用が重く不安定、②口座紐付き、
③**第三者再配布の可否が未確認＝規約リスク**。案Aより運用も法務も重い。

**案C：Twelve Data等 海外クラウドAPI（要・東証intraday一次確認）**
クラウド完結・商用の建付けは明快。ただし**東証intradayの実対応・粒度・遅延・日本株再配布条件が未確認**。
契約前にサポートへ直接照会が必要。確認クリアなら運用は最軽量。

## 要確認（公式明記を取れなかった項目）

- kabuステーション Professional の月額と、取得データの顧客再配布可否（規約原文）。
- Twelve Data / Alpha Vantage / Polygon / EODHD の東証intraday実対応・プラン・料金・日本株再配布条件。
- J-Quants 基本プラン（ライト/スタンダード/プレミアム）の月額。

## 次の一手

1. 顧客要件を「当日夕方バッチで足りる／日中リアルタイム必須」で確定する（分岐点）。
2. 当日バッチで足りる → J-Quants外部配信でPoC（REST取得→Lark Base蓄積、認証・遅延・銘柄上限を実測）。
3. リアルタイム必須 → Twelve Data等サポートへ東証intraday対応を直接照会し「要確認」を潰す。

## 出典

1. J-Quants データ仕様 https://jpx-jquants.com/ja/spec/data-spec
2. J-Quants 更新タイミング https://jpx-jquants.com/ja/spec/data-update
3. J-Quants 株価分足API https://jpx-jquants.com/ja/spec/eq-bars-minute
4. JPX ニュース（分足・Tick追加/CSV提供 2026-01-19） https://www.jpx.co.jp/corporate/news/news-releases/6020/20260119.html
5. kabuステーションAPI 製品 https://kabu.com/item/kabustation_api/default.html
6. kabuステーションAPI リファレンス https://kabucom.github.io/kabusapi/reference/index.html
7. kabuステーションAPI Push https://kabucom.github.io/kabusapi/ptal/push.html
8. 楽天 MarketSpeed II RSS https://marketspeed.jp/ms2_rss/
9. MS2 RSS 機能 https://marketspeed.jp/ms2_rss/function/
10. Yahoo Developer API 規約 https://legal.yahoo.com/us/en/yahoo/terms/product-atos/apiforydn/index.html
11. Yahoo ToS https://legal.yahoo.com/xw/en/yahoo/terms/otos/index.html
12. yfinance/日本株 実態 https://systemtrade.blog/posts/restapi
13. Twelve Data 東証（XJPX） https://twelvedata.com/exchanges/XJPX
14. Twelve Data 料金 https://twelvedata.com/pricing
15. Alpha Vantage ドキュメント https://www.alphavantage.co/documentation/
16. EODHD 取引所一覧 https://eodhd.com/list-of-stock-markets
17. 金融データAPI比較（2025） https://www.ksred.com/the-complete-guide-to-financial-data-apis-building-your-own-stock-market-data-pipeline-in-2025/
