# Initial Setup

このリポジトリを初めて使うとき、または新しい会社・案件で使い始めるときに実行する。

## 目的

`.claude / work / data` の役割を確認し、会社メモリ、作業場所、GitHub Actionsの確認まで案内する。

## 実行手順

以下を順に実施する。

### 1. 構成確認

```bash
test -d .claude && test -d work && test -d data && echo "OK: core directories exist"
```

### 2. 実行権限付与

```bash
chmod +x data/tools/scripts/*.sh .claude/hooks/*.sh
```

### 3. 会社メモリ初期化

会社スラッグを決める。

```bash
./data/tools/scripts/init-company.sh company-name
```

例:

```bash
./data/tools/scripts/init-company.sh dot-think
```

### 3.5 秘書の名前を設定

経営者の右腕AI（秘書）の名前を決める。以後この名前・人格で会話が続く。

```bash
./data/tools/scripts/init-secretary.sh "秘書の名前" "ユーザーの呼び方"
```

例:

```bash
./data/tools/scripts/init-secretary.sh "ミライ" "社長"
```

- 名前は `data/memory/secretary/secretary-profile.md` に保存される。
- 毎セッション開始時に `SessionStart` フックで読み込まれ、同じ秘書として会話を継続できる。
- 性格・口調を変えたい場合は `secretary-profile.md` を直接編集する。

### 4. 作業フォルダ作成

```bash
mkdir -p work/{client-or-project}/{00_context,01_business,02_proposal,03_documents,04_system,05_operation,06_data,99_logs}
```

実際には `{client-or-project}` を案件名に置き換える。

### 5. 最低限の初期ファイル作成

```bash
touch work/{client-or-project}/00_context/project-brief.md
touch work/{client-or-project}/99_logs/decision-log.md
touch work/{client-or-project}/99_logs/issue-log.md
```

### 6. 初期確認

以下を確認する。

- `data/memory/secretary/secretary-profile.md`
- `data/memory/decision-principles.md`
- `data/memory/company/`
- `data/knowledge/source-registry.yml`
- `data/knowledge/public-data/`
- `work/{client-or-project}/00_context/project-brief.md`

### 7. GitHub Actions確認

GitHub画面で以下を確認する。

- CI
- Monthly Public Source Check

## Claude Codeへの報告形式

完了後、以下の形式で報告する。

```md
# Initial Setup Result

## Completed

- Core directories checked
- Execute permission granted
- Secretary name set
- Company memory initialized
- Work folder created
- Initial files created

## Created / Checked Paths

## Remaining Tasks

## Next Action
```

## 注意

- `.claude/` に仕事の中身を置かない。
- 案件の成果物は `work/` に置く。
- 案件をまたぐ記憶や知識は `data/` に置く。
