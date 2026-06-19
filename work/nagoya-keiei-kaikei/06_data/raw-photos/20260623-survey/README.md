# 6/23 現地調査 写真 取り込みフォルダ

当日 iPhone で撮った写真を、ノートPCでまずここに入れる（AirDrop/USB/コピー）。

## 使い方

1. 撮影：場所が変わったら**見出し写真**→**4カット**（引き/全景/型番ラベル/配線）。詳細 [photo-capture-method.md](../../../04_system/photo-capture-method.md)。
2. ここ（`20260623-survey/`）に入れる。館ごとにサブフォルダを作ってもよい（`2gou/` `5gou/` `6gou/`）。
3. クロエに渡す：「**IMG_1234〜1240 は 5号館2F・52C配電盤、ラック全景と型番ラベル**」のように**場所＋何の写真**をコメント。
4. クロエが：内容確認 → `館-階-場所-カテゴリ-連番`にリネーム（例 `5-2F-52C-rack-01.jpg`）→ 整理 → `06_data/photo-index.md` に記録（機微が写るものは実値を書かず「(機微→credentials)」）。

## 重要

- **このフォルダの画像は git 管理外（ローカルのみ）**。GitHubには上がらない＝設定画面/ラベルのIP等が漏れない。バックアップはUSBへ。
- gitに上がるのは台帳 `06_data/photo-index.md`（テキスト）だけ。
- カテゴリ：diagram / device-label / rack / cabling / wifi / server / camera / doc / panel(配電盤)。
