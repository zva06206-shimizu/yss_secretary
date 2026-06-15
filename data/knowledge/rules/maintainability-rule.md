# Maintainability Rule

## 目的

変更・改修に強いシステムを作る。速く作るだけでなく、後から仕様変更、画面追加、権限追加、外部連携追加、DB変更が発生しても壊れにくい構造にする。

## 基本原則

1. 変更理由が追えること
2. 変更箇所が局所化されていること
3. テストで影響範囲を検知できること
4. DB変更を安全に戻せること
5. 外部サービスを差し替えられること
6. UI部品を再利用できること
7. 設計書と実装が乖離しないこと

## Laravel構造ルール

### Controller

- Controllerに業務ロジックを書きすぎない。
- Controllerは入力、権限確認、Service呼び出し、View/Response返却に限定する。

### Service

- 業務処理は `app/Services` に分離する。
- 1つのServiceは1つの業務目的にする。
- 外部API、メール、CSV、PDF、ファイル保存など副作用のある処理はService化する。

### Action / UseCase

- 複雑な処理は `app/Actions` または `app/UseCases` に分離する。
- 例: `CreateOrderAction`, `ApproveRequestAction`, `ImportCsvAction`

### Repository

- DBアクセスを隠蔽したい場合のみRepositoryを使う。
- 単純なEloquent操作に過剰なRepositoryを作らない。
- 外部システム連携、複雑な検索条件、差し替え可能性がある場合に使う。

### Policy / Gate

- 認可はController内のif文ではなくPolicy/Gateへ寄せる。
- 画面表示だけで権限制御したことにしない。

### FormRequest

- ValidationはFormRequestへ寄せる。
- Validationルールは画面設計、API仕様、テストケースと一致させる。

## DB変更ルール

- DB変更はMigrationで行う。
- カラム削除・型変更は影響範囲を記録してから行う。
- 互換性を壊す変更は段階的に行う。
- 重要テーブルには created_at / updated_at を付与する。
- 監査が必要な業務には audit log を検討する。
- Enum的な値は意味、追加方針、表示名を設計書に記録する。

## API/外部連携ルール

- 外部APIはInterfaceを切り、実装を差し替え可能にする。
- APIレスポンスをControllerで直接扱わない。
- タイムアウト、リトライ、失敗時の記録を設計する。
- 外部仕様は `work/{project}/04_system/design/api/` に記録する。

## UI変更ルール

- 新しいUI部品を画面単位で作らない。
- まず `data/ui/components/` を確認する。
- 既存部品で対応できない場合は、コンポーネントとして追加する。
- スマホ表示を同時に定義する。

## テストルール

- 変更が入る箇所には、正常系、異常系、権限系、境界値のテストを追加する。
- バグ修正時は、同じバグを再発させないテストを追加する。
- 重要業務フローはFeature TestまたはE2E Testで守る。

## ドキュメント同期ルール

実装変更時に以下を確認する。

- 要件定義の修正が必要か
- 画面設計の修正が必要か
- 機能設計の修正が必要か
- DB設計の修正が必要か
- API仕様の修正が必要か
- テストケースの修正が必要か
- UI共通部品の修正が必要か
- 画面・機能実装一覧表の更新が必要か

## 禁止

- とりあえずControllerに書く
- とりあえずBladeに直接ロジックを書く
- テストなしで仕様変更する
- MigrationなしにDBを変更する
- 既存コンポーネントを確認せずに似たUIを作る
- 設計判断を記録せずにライブラリを追加する
