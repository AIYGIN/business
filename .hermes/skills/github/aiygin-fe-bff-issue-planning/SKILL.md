---
name: aiygin-fe-bff-issue-planning
description: FE/BFF の開発計画を GitHub Issue 形式へ変換し、AIYGIN/business の親 Issue だけを作成したうえで、AIYGIN/fe と AIYGIN/bff の子 Issue 作成は各リポジトリ内のテンプレート・スクリプト・skill へ委譲するワークフロー。
version: 1.3.0
author: Hermes Agent
license: MIT
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [github, issues, planning, fe, bff, business, aiygin]
    related_skills: [github-issues, github-pr-summarizer, aiygin-product-orchestrator, aiygin-codegraph-investigation-common, aiygin-fe-code-investigation, aiygin-bff-code-investigation]
---

# AIYGIN FE/BFF 開発計画の business Issue 化と子 Issue 作成委譲

## 概要

この skill は、FE/BFF をまたぐ開発計画・仕様・RFC・ユーザーストーリーを、まず `AIYGIN/business` の GitHub Issue として整理・登録するための手順である。

重要: この skill が直接発行する Issue は `AIYGIN/business` の親 Issue だけである。

`AIYGIN/fe` と `AIYGIN/bff` の子 Issue は、この skill から直接 `gh issue create --repo AIYGIN/fe` や `gh issue create --repo AIYGIN/bff` を実行して作成してはいけない。FE/BFF 各リポジトリには Issue 作成用のテンプレート、スクリプト、skill ファイルがあるため、子 Issue 作成は必ずそれらへ委譲する。

対象リポジトリは以下の 3 つ。

- 親の計画リポジトリ: `AIYGIN/business`
- BFF 実装リポジトリ: `AIYGIN/bff`
- フロントエンド実装リポジトリ: `AIYGIN/fe`

必須の流れは以下。

0. Issue 起票前に、既存の `AIYGIN/fe` / `AIYGIN/bff` ソースコードを調査する。調査、設計、Issue 発行は同じ思考で混ぜず、原則として別 skill / 別エージェント / 別フェーズに分ける。
1. FE 調査エージェントが `AIYGIN/fe` を調査し、routing、middleware、認証導線、Orval 設定、生成 API client / mock、既存 TODO 画面、テスト構成をまとめる。
2. BFF 調査エージェントが `AIYGIN/bff` を調査し、NestJS module/controller/service/resource/repository 構成、OpenAPI/docs、認証・Guard、DB 接続、test/e2e 構成をまとめる。
3. 設計フェーズで、ユーザー入力と FE/BFF 調査結果を統合し、実装可能な FE/BFF 横断設計へ落とし込む。
4. Issue 発行フェーズで、`AIYGIN/business` に親 Issue を作成、または既存の親 Issue を特定する。
5. 親 Issue には、調査結果に基づく BE、BFF、機能要件、UI要件、セキュリティ対策、リスク、リスク対策を必ず含める。
6. 親 Issue の URL と要件整理結果を、FE/BFF 子 Issue 作成用の委譲入力としてまとめる。
7. `AIYGIN/fe` の子 Issue 作成は、`AIYGIN/fe` リポジトリ内のテンプレート・スクリプト・skill に委譲する。
8. `AIYGIN/bff` の子 Issue 作成は、`AIYGIN/bff` リポジトリ内のテンプレート・スクリプト・skill に委譲する。
9. 子 Issue 作成が完了したら、作成された FE/BFF Issue URL を `AIYGIN/business` の親 Issue にコメント、または本文更新で追記する。

## フェーズ分離とエージェント分担

効率と品質のため、この workflow は以下の 3 フェーズに分ける。

### 1. 既存ソースコード調査フェーズ

Issue 起票前に、FE/BFF の現状を実コードから確認する。ここでは Issue 本文を作成しない。

調査は親エージェントが直接すべて読むのではなく、原則として `delegate_task` で FE/BFF それぞれの調査サブエージェントを並列起動する。詳細手順は以下の 3 skill に分離する。

- 共通ルール: `aiygin-codegraph-investigation-common`
- FE 調査: `aiygin-fe-code-investigation`
- BFF 調査: `aiygin-bff-code-investigation`

親エージェントは、上記 skill から必要な context だけを調査サブエージェントへ渡す。親エージェント自身は FE/BFF の詳細な探索ログを抱え込まず、返却された調査結果 schema を使って横断設計に進む。

基本方針:

- `AIYGIN/fe` と `AIYGIN/bff` は `.codegraph/codegraph.db` がある前提で、コード理解・影響範囲確認では CodeGraph を優先する。
- FE 調査では `aiygin-fe-code-investigation` を使い、routing、middleware、認証導線、Orval、生成 API client / mock、Storybook、test、UI 導線を確認する。
- BFF 調査では `aiygin-bff-code-investigation` を使い、NestJS module/controller/service/resource/repository、DTO、OpenAPI docs、auth、DB、test/e2e を確認する。
- FE/BFF 調査では、コード構成だけでなく、子 Issue 作成用の repo-local asset（skill / template / script / workflow）も確認し、path、使い方、見つからない場合の fallback 方針を調査結果に含める。詳細メモは `references/aiygin-child-issue-delegation-assets.md` を参照する。特に AIYGIN/fe は `.github/ISSUE_TEMPLATE` ではなく `.codex/skills/plan-to-issue/`（`SKILL.md`, `references/rules.md`, `assets/template.md`, `scripts/create_issue.sh`）を優先確認する。
- repo-local asset が見つからない repo では、この skill から直接 `gh issue create --repo AIYGIN/fe` / `AIYGIN/bff` を代替実行しない。親 business Issue に「未作成理由」をコメントし、未完了 TODO を agent-memory scratchpad に残す。
- 共通の出力 schema、fallback 方針、禁止事項は `aiygin-codegraph-investigation-common` に従う。
- 調査、設計、Issue 発行を同じサブエージェントに混ぜない。
- 調査サブエージェントは Issue 作成やコード変更を行わない。

### 2. 横断設計フェーズ

設計担当は、ユーザー入力と FE/BFF 調査結果を統合する。この時点でもまだ GitHub Issue は作成しない。

このフェーズは特定機能に依存しない汎用設計 skill として扱う。具体機能名を固定せず、対象機能に合わせて画面生成・導線・API・データ・権限・テストを整理する。

- FE 側で実装すべき routing、page/layout、middleware、public/protected route、画面生成、UI component、状態管理、form/input、navigation、Orval 再生成、test 方針を整理する。
- BFF 側で実装すべき endpoint、DTO、OpenAPI、Controller、Service、Resource、Repository、DB、外部連携、認可・所有者境界、test 方針を整理する。
- FE/BFF の API 契約境界を明確にし、frontend 都合だけで BFF response を変えない。
- Mermaid diagram など GitHub で render される表現は、GitHub Mermaid 互換の単純な syntax で書く。
- 情報不足は `未確定` / `要確認` として残す。

### 3. Issue 発行フェーズ

Issue 発行担当は、設計結果をもとに `AIYGIN/business` の親 Issue だけを作成・更新する。

- Issue 発行担当は、`references/business-parent-issue-template.md` をベースに親 Issue 本文を作る。これは AIYGIN/business #1 の復元後構成をもとにしたテンプレートであり、見出し欠落を防ぐための正本とする。
- Issue 発行担当は、FE/BFF のソースコード調査を追加で始めない。必要なら調査フェーズへ差し戻す。
- Issue 発行担当は、`AIYGIN/fe` / `AIYGIN/bff` に直接 Issue を作成しない。
- Issue 発行担当は、作成前に重複検索、label 確認、本文 file 作成、`gh issue create` / `gh issue edit`、作成後 verification だけを担当する。
- `gh issue edit` などで既存 Issue を更新するときは、部分更新でも本文全体を一時ファイルに保存し、更新前後の見出し一覧を比較して欠落がないことを確認する。
- フローチャートや Mermaid block を差し替えるときは、次の `## ...` 見出し以降を消さない範囲指定にする。
- FE/BFF 子 Issue は各 repo のテンプレート・スクリプト・skill へ委譲する。

推奨する `delegate_task` 分担:

```text
1. FE 調査エージェント: `aiygin-codegraph-investigation-common` + `aiygin-fe-code-investigation` の内容で AIYGIN/fe の現状調査だけを行う。
2. BFF 調査エージェント: `aiygin-codegraph-investigation-common` + `aiygin-bff-code-investigation` の内容で AIYGIN/bff の現状調査だけを行う。
3. 親エージェント: 2つの調査結果とユーザー要件から横断設計を作る。
4. Issue 発行 skill/エージェント: business Issue 作成・更新だけを行う。
```

調査時の context load 方針:

- FE だけ調査する場合は、共通 + FE 調査 skill のみ使い、BFF 調査 skill は読まない。
- BFF だけ調査する場合は、共通 + BFF 調査 skill のみ使い、FE 調査 skill は読まない。
- business Issue planning のように FE/BFF 両方が必要な場合だけ、FE/BFF 調査を `delegate_task` batch mode で並列実行する。
- 親エージェントは調査 skill の詳細をすべて保持せず、サブエージェントへ渡す context と返却された調査結果 schema に絞る。


## 使用する場面

ユーザーが以下のように依頼したときに使う。

- 「fe/bff の開発計画を Issue 化して」
- 「この仕様を business / bff / fe に Issue 登録して」
- 「開発計画を GitHub Issue 用フォーマットへ変換して自動登録して」
- 「FE と BFF にタスクを切って。その前に business に親 Issue を立てて」
- 「この要件から business, bff, fe の Issue を作って」

使わない場面。

- 単一リポジトリだけで完結する軽微な bug report。
- PR 作成、コード実装、レビュー依頼そのもの。
- GitHub 認証や gh CLI セットアップのトラブルシュート。必要なら `github-auth` / `github-issues` を使う。

## 絶対ルール

- この skill で直接作成してよい Issue は `AIYGIN/business` だけ。
- `AIYGIN/fe` と `AIYGIN/bff` の Issue 作成は、各リポジトリ内の Issue 作成用テンプレート・スクリプト・skill に委譲する。
- FE/BFF 子 Issue の本文テンプレートをこの skill 内で独自生成して、そのまま `gh issue create` してはいけない。
- FE/BFF 子 Issue 作成に必要な情報は、business Issue URL と整理済み要件を委譲入力として渡す。
- 子 Issue 作成後は、FE/BFF 側の作成結果 URL を business Issue に戻す。

## 対象リポジトリ

コマンドでは必ずリポジトリ名を明示する。

```bash
BUSINESS_REPO="AIYGIN/business"
BFF_REPO="AIYGIN/bff"
FE_REPO="AIYGIN/fe"
```

このワークフローでは、現在の作業ディレクトリの git remote に依存してはいけない。

## 入力から抽出する情報

入力は、箇条書きの計画、仕様、RFC、会話メモ、ユーザーストーリー、既存 Issue 草案などでよい。

Issue 作成前に、以下を抽出・整理する。

- 機能名 / 短いタイトル
- ビジネス目的、ユーザー価値
- 機能要件
- UI要件
- BE の責務
- BFF の責務
- FE の責務
- API 契約への影響
- セキュリティ対策
- リスク
- リスク対策
- 受け入れ条件
- 依存関係
- 未決事項

情報が足りない場合は、勝手に詳細を捏造せず、`未確定` / `要確認` と明記して進める。

ただし、以下のように Issue 作成対象や登録可否が変わる曖昧さがある場合は、ユーザーに確認する。

- business の親 Issue を新規作成するか、既存 Issue を使うか判断できない。
- FE/BFF 子 Issue の作成委譲先がローカルに存在せず、取得方法も分からない。
- ユーザーが「登録前に内容確認したい」と明示している。

## 事前確認

Issue を作る前に、GitHub CLI とアクセス権を確認する。

```bash
command -v gh >/dev/null || { echo "gh CLI が必要です"; exit 1; }
gh auth status >/dev/null || { echo "gh auth が必要です"; exit 1; }

gh repo view AIYGIN/business >/dev/null
gh repo view AIYGIN/bff >/dev/null
gh repo view AIYGIN/fe >/dev/null
```

重複を避けるため、まず `AIYGIN/business` の既存 Issue を検索する。

```bash
QUERY="<機能名または主要キーワード>"
gh issue list --repo AIYGIN/business --state open --search "$QUERY" --limit 20
```

該当する business Issue がすでにある場合は、重複作成せず親 Issue として再利用する。

FE/BFF 側の重複確認は、この skill で直接 `AIYGIN/fe` / `AIYGIN/bff` の Issue 作成を行うためではなく、委譲先が必要とする入力として扱う。最終的な重複判定と子 Issue 作成は、各リポジトリのテンプレート・スクリプト・skill の責務とする。

## business 親 Issue の形式

`AIYGIN/business` に作成する親 Issue の本文は、原則として以下の構成にする。

```markdown
## 概要
<この開発計画で実現することを 2-5 文で記載>

## 背景・目的
- <なぜ必要か>
- <誰にどの価値があるか>

## スコープ
### 対象
- <今回含めること>

### 対象外
- <今回含めないこと>

## 機能要件
- [ ] <ユーザー操作・業務要件・状態遷移など>
- [ ] <...>

## UI要件
- [ ] <画面、導線、表示項目、バリデーション、空状態、エラー状態など>
- [ ] <...>

## BE要件
- [ ] <DB、外部連携、ドメインロジック、バッチ、権限など。該当なしなら「現時点では該当なし / 要確認」>

## BFF要件
- [ ] <API、DTO、OpenAPI、認可、集約、変換、エラーハンドリングなど>

## セキュリティ対策
- [ ] <認証・認可>
- [ ] <入力検証>
- [ ] <機密情報・ログ・監査>
- [ ] <レート制限・権限境界など>

## リスク
| リスク | 影響 | 可能性 | 備考 |
|---|---:|---:|---|
| <risk> | 高/中/低 | 高/中/低 | <note> |

## リスク対策
- [ ] <risk に対応する mitigation>
- [ ] <...>

## 受け入れ条件
- [ ] <ユーザー観点の完了条件>
- [ ] <API / UI / セキュリティ観点の完了条件>

## FE/BFF 子 Issue 作成
- FE: `AIYGIN/fe` リポジトリ内の Issue 作成テンプレート・スクリプト・skill に委譲する。作成後に URL を追記する。
- BFF: `AIYGIN/bff` リポジトリ内の Issue 作成テンプレート・スクリプト・skill に委譲する。作成後に URL を追記する。

## 委譲用入力
### FE 向け
- 親 Issue: <business issue URL>
- UI要件: <要約>
- 機能要件: <要約>
- API / 契約影響: <要約>
- セキュリティ・UX 注意点: <要約>

重要: BFF API を FE から利用する計画では、FE は BFF の OpenAPI 定義を元に Orval で API client / mock を自動生成する前提を明記する。委譲用入力の API / 契約影響には、少なくとも以下を含める。

- FE は BFF の OpenAPI 定義を元に Orval で API client / mock を自動生成する前提とする。
- Orval 生成物は手動編集しない。
- BFF の API 契約変更時は OpenAPI を更新し、FE 側で Orval 再生成を行う。

### BFF 向け
- 親 Issue: <business issue URL>
- BFF要件: <要約>
- API / OpenAPI 対応: <要約>
- BE 連携: <要約>
- セキュリティ注意点: <要約>

## 未決事項
- [ ] <要確認事項。なければ「なし」>
```

推奨タイトル。

```text
[Feature] <機能名> の開発計画
```

## business Issue の自動登録手順

複数行の Issue 本文は一時ファイルに書き出す。長い Markdown を shell command に直接埋め込まない。

```bash
mkdir -p /tmp/aiygin-issues
BUSINESS_BODY="/tmp/aiygin-issues/business.md"
```

1. business 親 Issue の本文を `$BUSINESS_BODY` に書く。
2. business 親 Issue を作成する。

```bash
BUSINESS_URL=$(gh issue create \
  --repo AIYGIN/business \
  --title "[Feature] <機能名> の開発計画" \
  --body-file "$BUSINESS_BODY")

echo "$BUSINESS_URL"
```

この手順で作成するのは `AIYGIN/business` の Issue だけである。

## FE/BFF 子 Issue 作成への委譲

business Issue を作成・特定したら、FE/BFF 子 Issue 作成は各リポジトリに委譲する。

委譲時には、少なくとも以下を渡す。

```text
親 business Issue: <business issue URL>
機能名: <機能名>
概要: <概要>
機能要件: <機能要件>
UI要件: <UI要件>
BE要件: <BE要件>
BFF要件: <BFF要件>
API / 契約影響: <API 契約影響>
セキュリティ対策: <セキュリティ対策>
リスク: <リスク>
リスク対策: <リスク対策>
受け入れ条件: <受け入れ条件>
未決事項: <未決事項>
```

### FE への委譲

`AIYGIN/fe` リポジトリ内にある Issue 作成用テンプレート・スクリプト・skill を使う。

この skill では FE Issue 本文を独自に確定しない。FE 側のテンプレートとスクリプトが期待する形式に合わせて、business Issue URL と要件整理結果を渡す。

FE 側へ渡す観点の例。

- 親 business Issue URL
- UI要件
- 画面・導線・状態・表示・入力・バリデーション
- API / BFF 契約への依存
- セキュリティ・UX 注意点
- 受け入れ条件
- 未決事項

### BFF への委譲

`AIYGIN/bff` リポジトリ内にある Issue 作成用テンプレート・スクリプト・skill を使う。

この skill では BFF Issue 本文を独自に確定しない。BFF 側のテンプレートとスクリプトが期待する形式に合わせて、business Issue URL と要件整理結果を渡す。

BFF 側へ渡す観点の例。

- 親 business Issue URL
- BFF要件
- API / OpenAPI / DTO / Controller / docs decorator への影響
- BE 連携、DB、外部連携、ドメインロジック
- 認証・認可、入力値検証、エラー応答
- FE 連携に必要な契約・mock・注意点
- 受け入れ条件
- 未決事項

## 子 Issue 作成結果の business Issue への反映

FE/BFF 側の委譲が完了し、子 Issue URL が得られたら、親エージェント自身が `gh issue view` で再検証してから business Issue にコメントする。サブエージェントの自己申告だけで成功扱いにしない。

## 親 Issue コメント反映ループ

親 `AIYGIN/business` Issue に人間コメントで route、API path、認証、DTO 命名、保存先、実装配置などの確定方針が追加された場合は、親 Issue だけでなく作成済み FE/BFF 子 Issue も同時に見直す。

手順:

1. `gh issue view <parent> --repo AIYGIN/business --json comments,body,title` で対象コメントと現行本文を取得する。
2. コメント内の確定事項を分類する。
   - FE route（例: `/dividend`）
   - BFF endpoint（例: 既存方針に合わせた `/company/...`）
   - 認証（例: JWT 必須）
   - path param 名・形式（例: `symbolId` / 4桁証券コード）
   - DTO 表現（例: `analysisSummary: null`, FCF N/A は `null` + boolean）
   - resource / utility / scripts など実装配置
3. 親 Issue 本文を更新する。
4. 作成済み FE 子 Issue と BFF 子 Issue を `gh issue edit --body-file` で更新する。
5. `gh issue view` で stale な旧記述が残っていないか確認する。
   - 旧 API path（例: `/api/dividend-analysis`）
   - 未確定扱いのまま残った route / auth / DTO 方針
   - 子 Issue 未作成などの古い作業状況コメント
6. business 親 Issue に反映結果コメントを残す。

注意:

- API path や DTO が変わった場合、BFF Issue の title も本文と合わせて更新する。
- FE Issue には新しい BFF endpoint、Orval 生成結果確認、null/TODO 表示、path param 名を反映する。
- `gh issue view --jq` で boolean 式を書くときは object の値に文字列を直接置かず、`{title:.title, ...}` のように key を明示する。

必須 verification:

```bash
gh issue view <FE_ISSUE_NUMBER> --repo AIYGIN/fe --json url,title,number,body --jq \
  '{number,title,url,hasParent:(.body|contains("<BUSINESS_ISSUE_URL>"))}'

gh issue view <BFF_ISSUE_NUMBER> --repo AIYGIN/bff --json url,title,number,body --jq \
  '{number,title,url,hasParent:(.body|contains("<BUSINESS_ISSUE_URL>"))}'
```

確認すること:

- 子 Issue URL / number / title が実在する。
- 子 Issue 本文に親 business Issue URL が含まれる。
- FE/BFF repo の子 Issue 作成は各 repo の仕組みで行われており、この skill が直接 `gh issue create --repo AIYGIN/fe` / `AIYGIN/bff` していない。

検証後、business Issue にコメントする。

```bash
gh issue comment "$BUSINESS_URL" --body "FE/BFF 子 Issue 作成結果です。

- FE: <FE issue URL または 未作成理由>
- BFF: <BFF issue URL または 未作成理由>"
```

子 Issue 作成が未完了の場合は、成功したように報告してはいけない。以下のように状態を明記する。

```text
- FE: 委譲先スクリプト未実行 / 実行失敗 / URL 未取得
- BFF: 委譲先スクリプト未実行 / 実行失敗 / URL 未取得
```

AIYGIN 運用補足:

- 作成完了、ブロック、失敗の要約を対象 repo の `agent-memory` daily log に残す。
- 親 business、FE、BFF の各 repo で agent-memory 配置が異なる場合は、対象 repo の `AGENTS.md` に従い、保存先を推測せず確認する。

## 事前確認のみ行う場合

ユーザーが明確に「自動登録して」「作成して」「Issue を立てて」と言っていない場合は、まず登録予定と委譲方針を提示する。

```text
登録予定:
- AIYGIN/business: [Feature] <機能名> の開発計画

委譲予定:
- AIYGIN/fe: リポジトリ内の Issue 作成テンプレート・スクリプト・skill へ委譲
- AIYGIN/bff: リポジトリ内の Issue 作成テンプレート・スクリプト・skill へ委譲

注意:
- この skill では AIYGIN/fe / AIYGIN/bff の Issue は直接作成しません。
- business Issue URL と整理済み要件を委譲入力として渡します。
```

ユーザーが「自動登録して」「作成して」「立てて」と明示した場合は、事前確認と重複確認を行ったうえで business Issue を登録し、その後 FE/BFF 側へ委譲する。

## 重複 Issue の扱い

Issue 作成前に、複数のキーワードで `AIYGIN/business` を検索する。

```bash
gh issue list --repo AIYGIN/business --state open --search "<機能名>" --limit 20
gh issue list --repo AIYGIN/business --state open --search "<主要キーワード>" --limit 20
```

business 親 Issue の重複候補がある場合。

- `gh issue view --repo AIYGIN/business <number>` で内容を確認する。
- 同じ計画を扱っているなら、既存 Issue を親として使う。
- 既存親 Issue URL を FE/BFF 委譲入力に使う。
- 子 Issue 作成結果が得られたら、既存親 Issue にコメントする。

FE/BFF 子 Issue の重複確認・再利用判断は、各リポジトリの Issue 作成用テンプレート・スクリプト・skill に委譲する。この skill が独自判断で FE/BFF Issue を作成・更新してはいけない。

## label と assignee

この skill で扱う label / assignee は `AIYGIN/business` の親 Issue に限る。

label は存在を確認してから使う。

```bash
gh label list --repo AIYGIN/business
```

存在しない label は使わない。ユーザーが明示しない限り、新規 label は作成しない。

存在する場合に使ってよい候補。

- `feature`
- `planning`
- `security`
- `risk`

assignee は、ユーザーが指定した場合、または `AIYGIN/business` の明確な運用ルールが分かっている場合だけ設定する。推測で担当者を割り当てない。

FE/BFF 子 Issue の label / assignee は、各リポジトリの委譲先テンプレート・スクリプト・skill の責務とする。

## 品質ルール

- business Issue を横断要件の正本とする。
- Issue 本文は極力日本語で書く。Mermaid node label、補足、受け入れ条件、委譲用入力も日本語を優先し、API 名・endpoint・env・コード識別子だけ英語表記を許容する。
- この skill で直接作成する Issue は `AIYGIN/business` のみ。
- FE/BFF 子 Issue 作成は、それぞれ `AIYGIN/fe` / `AIYGIN/bff` 内のテンプレート・スクリプト・skill に委譲する。
- business Issue には、FE/BFF に委譲しやすいよう `委譲用入力` を含める。
- 認証基盤 Issue では `references/auth-planning-corrections.md` も確認し、Orval 前提、Next.js middleware + `/login` 導線、Supabase 等 managed Postgres 前提、provider 置換漏れを反映する。
- Google `displayName` を TODO 所有者として使い、かつ Cookie から復元する設計を求められた場合は `references/auth-displayname-owner-cookie.md` を確認する。DB に users / auth_accounts を作らず、`access_token` Cookie 内 JWT の `displayName` claim から `CurrentUser.displayName` を復元し、TODO の `owner_display_name` と照合する。
- セキュリティ対策とリスクは、情報不足でも省略しない。`要確認` として残す。
- 実装可能な要件と受け入れ条件は checkbox にする。
- 詳細が不明な場合は `未確定` と書き、事実のように補完しない。
- Issue タイトルは短く検索しやすくする。
- FE 生成物、特に Orval 生成 API client / mock は手動編集しない前提で整理する。
- frontend 都合だけで BFF レスポンス契約を変更しない。契約変更が必要な場合は business Issue の API / 契約影響に明記し、BFF 側委譲入力にも含める。
- 委譲先の実行結果を確認せず、FE/BFF 子 Issue が作成済みだと報告しない。

## よくある失敗

1. この skill から `AIYGIN/fe` や `AIYGIN/bff` に直接 Issue を作ってしまう。子 Issue 作成は必ず各リポジトリ内の仕組みに委譲する。
2. business Issue からセキュリティ対策やリスク対策を省略する。このワークフローでは必須。
3. 委譲用入力に business Issue URL を入れ忘れる。FE/BFF 側が親子関係を追えなくなる。
4. frontend の都合だけで BFF レスポンス契約を変える前提にする。必要なら契約変更として business Issue と BFF 委譲入力に明記する。
5. frontend の生成 API client を手動編集する前提にする。FE 側委譲入力ではプロジェクトのワークフローに従って再生成する旨を伝える。
6. label や assignee が存在すると決めつける。business Issue の label は事前に確認するか、指定しない。
7. 重複 business Issue を作る。作成前に `AIYGIN/business` を検索する。
8. FE/BFF の子 Issue URL を business Issue へ戻し忘れる。
9. 子 Issue 作成の委譲が失敗したのに、成功したように報告する。
10. 情報不足を推測で埋める。`未確定` / `要確認` と書く。
11. FE repo の `.github/ISSUE_TEMPLATE` だけを探し、`.codex/skills/plan-to-issue/` を見落として FE 子 Issue 未作成扱いにする。
12. 親 business Issue の人間コメントで API path や認証方針が確定したのに、作成済み FE/BFF 子 Issue の古い endpoint・未確定事項を更新し忘れる。

## 完了確認チェックリスト

登録後、以下を確認する。

- [ ] `AIYGIN/business` に親 Issue が存在する、または既存親 Issue を再利用している。
- [ ] 親 Issue に BE、BFF、機能要件、UI要件、セキュリティ対策、リスク、リスク対策が含まれている。
- [ ] 親 Issue に FE/BFF へ渡せる委譲用入力が含まれている。
- [ ] この skill から `AIYGIN/fe` / `AIYGIN/bff` へ直接 Issue 作成していない。
- [ ] FE 子 Issue 作成を `AIYGIN/fe` リポジトリ内のテンプレート・スクリプト・skill に委譲した、または委譲できなかった理由を明記した。
- [ ] BFF 子 Issue 作成を `AIYGIN/bff` リポジトリ内のテンプレート・スクリプト・skill に委譲した、または委譲できなかった理由を明記した。
- [ ] 子 Issue URL が得られた場合は、business Issue に URL をコメントまたは本文更新で追記した。
- [ ] 最終応答で business Issue URL、FE/BFF 委譲結果、取得できた子 Issue URL をユーザーに報告している。
