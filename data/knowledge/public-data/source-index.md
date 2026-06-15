# Public Data Source Index

## 目的

白書、公的統計、政策レポート、国際機関レポートを一覧化し、提案書・研修資料・DX構想書・経営分析資料で再利用できるようにする。

## 日本国内：総合入口

| ID | 分類 | 名称 | URL | 用途 | 更新頻度 |
|---|---|---|---|---|---|
| JP-GEN-001 | 白書ポータル | e-Gov 白書等ポータル | https://www.e-gov.go.jp/about-government/white-papers.html | 各省庁白書の入口 | 要確認 |
| JP-GEN-002 | 調査ガイド | 国立国会図書館リサーチ・ナビ 官庁の白書の調べ方 | https://ndlsearch.ndl.go.jp/rnavi/politics/post_205031 | 白書の探し方確認 | 要確認 |
| JP-GEN-003 | 白書一覧 | 国立国会図書館リサーチ・ナビ 官庁の白書・年報 | https://ndlsearch.ndl.go.jp/rnavi/politics/JGOV_hakusyo | 官庁白書・年報一覧 | 要確認 |
| JP-GEN-004 | 英語白書 | Cabinet Office White Papers | https://www.cao.go.jp/en/whitepaper.html | 英語資料・海外向け資料 | 要確認 |
| JP-STAT-001 | 政府統計 | e-Stat 政府統計の総合窓口 | https://www.e-stat.go.jp/ | 政府統計データ取得 | 随時 |
| JP-STAT-002 | 政府統計英語 | e-Stat English | https://www.e-stat.go.jp/en | 英語統計資料 | 随時 |
| JP-STAT-003 | 統計局 | 総務省統計局 | https://www.stat.go.jp/ | 人口・労働・経済統計 | 随時 |

## 日本国内：主要白書

| ID | 分野 | 資料名 | URL | 主な用途 |
|---|---|---|---|---|
| JP-CAO-001 | 政府全般 | 内閣府 白書、年次報告書等 | https://www.cao.go.jp/whitepaper/ | 政策背景、経済社会課題 |
| JP-CAO-002 | 経済 | 経済財政白書・世界経済の潮流 | https://www5.cao.go.jp/keizai3/whitepaper.html | マクロ経済、投資判断、補助金背景 |
| JP-SOU-001 | ICT / DX | 情報通信白書 | https://www.soumu.go.jp/johotsusintokei/whitepaper/index.html | DX、AI、ICT活用、情報通信動向 |
| JP-MHLW-001 | 労働 | 厚生労働白書・労働経済白書等 | https://www.mhlw.go.jp/toukei_hakusho/hakusho/ | 人手不足、賃金、労働市場、人材育成 |
| JP-SME-001 | 中小企業 | 中小企業白書 | https://www.chusho.meti.go.jp/pamflet/hakusyo/index.html | 中小企業DX、経営課題、価格転嫁 |
| JP-SME-002 | 小規模企業 | 小規模企業白書 | https://www.chusho.meti.go.jp/pamflet/hakusyo/syokibo_index.html | 小規模企業支援、地域事業者支援 |
| JP-METI-001 | 製造業 | 製造基盤白書・ものづくり白書 | https://www.meti.go.jp/report/whitepaper/mono/ | 製造業、現場改善、技能承継、IoT |
| JP-ENE-001 | エネルギー | エネルギー白書 | https://www.enecho.meti.go.jp/about/whitepaper/ | GX、省エネ、エネルギーコスト |
| JP-MLIT-001 | 国土交通 | 国土交通白書 | https://www.mlit.go.jp/statistics/file000004.html | インフラ、物流、建設、地域 |
| JP-ENV-001 | 環境 | 環境白書・循環型社会白書・生物多様性白書 | https://www.env.go.jp/policy/hakusyo/index.html | GX、環境、循環型社会 |

## 国際機関

| ID | 分野 | 機関・資料 | URL | 主な用途 |
|---|---|---|---|---|
| INT-OECD-001 | 政策・経済 | OECD Publications | https://www.oecd.org/en/publications.html | 国際比較、政策、DX、教育、労働 |
| INT-WB-001 | 経済・開発 | World Bank Documents & Reports | https://documents.worldbank.org/en/publication/documents-reports | 経済開発、国際比較、産業政策 |
| INT-WB-002 | 統計 | World Bank Open Data | https://data.worldbank.org/ | 国際統計、マクロデータ |
| INT-IMF-001 | 経済 | IMF Publications | https://www.imf.org/en/publications | マクロ経済、金融、国際経済 |
| INT-IMF-002 | 統計 | IMF Data | https://www.imf.org/en/data | 国際経済データ |
| INT-ILO-001 | 労働 | ILO Research and Publications | https://www.ilo.org/research-and-publications | 労働市場、人材、雇用 |
| INT-ILO-002 | 労働統計 | ILOSTAT | https://ilostat.ilo.org/ | 労働統計、国際比較 |
| INT-IEA-001 | エネルギー | IEA Reports | https://www.iea.org/reports | エネルギー、GX、脱炭素 |
| INT-IEA-002 | エネルギー統計 | IEA Data and Statistics | https://www.iea.org/data-and-statistics | エネルギー統計 |
| INT-WEF-001 | 経済・人材 | World Economic Forum Publications | https://www.weforum.org/publications/ | 将来労働、スキル、テクノロジー |

## 運用ルール

- 引用時は発行年を確認する。
- 最新版と過去版が混在する場合は最新版を優先する。
- URLだけでなく、何の根拠として使うかを記録する。
- 提案書に使った場合は `work/{project}/99_logs/` に出典を記録する。
- 定期的にURL死活確認を行う。
