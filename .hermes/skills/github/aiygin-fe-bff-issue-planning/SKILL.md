---
name: aiygin-fe-bff-issue-planning
description: FE/BFF の開発計画を GitHub Issue 形式へ変換し、AIYGIN/business を親 Issue、AIYGIN/bff と AIYGIN/fe を子 Issue として自動登録するワークフロー。
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [github, issues, planning, fe, bff, business, aiygin]
    related_skills: [github-issues, github-pr-summarizer]
---

# AIYGIN FE/BFF 開発計画の GitHub Issue 化

## 概要

この skill は、FE/BFF をまたぐ開発計画・仕様・RFC・ユーザーストーリーを、AIYGIN の GitHub Issue 群へ変換して登録するための手順である。

対象リポジトリは以下の 3 つ。

- 親の計画リポジトリ: `AIYGIN/business`
- BFF 実装リポジトリ: `AIYGIN/bff`
- フロントエンド実装リポジトリ: `AIYGIN/fe`

必須の流れは以下。

1. まず `AIYGIN/business` に親 Issue を作成、または既存の親 Issue を特定する。
2. 親 Issue には、BE、BFF、機能要件、UI要件、セキュリティ対策、リスク、リスク対策を必ず含める。
3. 親 Issue の内容を元に、`AIYGIN/bff` と `AIYGIN/fe` に子 Issue を作成する。
4. 子 Issue から親 Issue へリンクする。
5. 親 Issue へ BFF / FE の子 Issue URL をコメント、または本文更新で追記する。

`AIYGIN/business` の親 Issue を作成・特定しないまま、FE/BFF の実装 Issue を作成してはいけない。

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

- FE/BFF のどちらか一方だけでよい可能性がある。
- business の親 Issue を新規作成するか、既存 Issue を使うか判断できない。
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

重複を避けるため、関連しそうな既存 Issue を検索する。

```bash
QUERY="<機能名または主要キーワード>"
gh issue list --repo AIYGIN/business --state open --search "$QUERY" --limit 10
gh issue list --repo AIYGIN/bff --state open --search "$QUERY" --limit 10
gh issue list --repo AIYGIN/fe --state open --search "$QUERY" --limit 10
```

該当する business Issue がすでにある場合は、重複作成せず親 Issue として再利用する。

該当する BFF / FE Issue がすでにある場合は、足りない子 Issue だけ作成する。既存子 Issue の内容が不足している場合は、新規 Issue を重複作成せず、既存 Issue へ不足事項をコメントする。

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

## API / 契約影響
- <既存 API で足りるか、追加・変更が必要か、OpenAPI 更新が必要か>

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

## 実装 Issue
- BFF: 作成後に追記
- FE: 作成後に追記

## 未決事項
- [ ] <要確認事項。なければ「なし」>
```

推奨タイトル。

```text
[Feature] <機能名> の開発計画
```

## BFF 子 Issue の形式

business 親 Issue の作成・特定後、`AIYGIN/bff` に作成する。

```markdown
## 親 Issue
- Business: <business issue URL>

## 概要
<この BFF issue で実装・調査する範囲>

## 要件
- [ ] <BFF に必要な要件>
- [ ] <OpenAPI / DTO / Controller / Service / 認可 / エラー仕様など>

## API / OpenAPI 対応
- [ ] 既存 OpenAPI 契約で要件を満たせるか確認する
- [ ] 不足がある場合は契約変更内容を明記する
- [ ] Controller / DTO / docs decorator を更新する
- [ ] frontend の Orval 生成に必要な契約を提供する

## セキュリティ
- [ ] 認証・認可の境界を確認する
- [ ] 入力値検証とエラー応答を定義する
- [ ] 機密情報をレスポンス・ログへ出さない

## テスト観点
- [ ] 正常系
- [ ] 異常系
- [ ] 認可エラー
- [ ] バリデーションエラー
- [ ] OpenAPI / DTO の整合性

## 受け入れ条件
- [ ] <BFF 完了条件>

## FE 連携メモ
- <FE 側が参照すべき endpoint / schema / mock / 注意点>
```

推奨タイトル。

```text
[BFF] <機能名> の API / 契約対応
```

## FE 子 Issue の形式

business 親 Issue の作成・特定後、`AIYGIN/fe` に作成する。

```markdown
## 親 Issue
- Business: <business issue URL>

## 概要
<この FE issue で実装・調査する範囲>

## 要件
- [ ] <画面・導線・状態・表示・入力・バリデーションなど>

## UI要件
- [ ] <画面構成>
- [ ] <操作導線>
- [ ] <ローディング / 空状態 / エラー状態>
- [ ] <アクセシビリティ・レスポンシブなど>

## API 連携
- [ ] Business / BFF issue の契約内容を確認する
- [ ] 既存 API で要件を満たせるか確認する
- [ ] 必要に応じて Orval 生成 API client / mock を更新する
- [ ] 生成物は手動編集しない

## セキュリティ・UX
- [ ] 認可されていない操作を UI 上で適切に扱う
- [ ] 入力値・表示値の扱いを確認する
- [ ] エラー時に機密情報や内部事情を露出しない

## テスト観点
- [ ] ユーザー操作の正常系
- [ ] 入力バリデーション
- [ ] API 成功 / 失敗
- [ ] 空状態 / ローディング / エラー状態
- [ ] 権限差分がある場合の表示制御

## 受け入れ条件
- [ ] <FE 完了条件>

## BFF 連携メモ
- <依存する BFF issue URL、endpoint、schema、mock、未決事項>
```

推奨タイトル。

```text
[FE] <機能名> の画面 / UI 対応
```

## 自動登録手順

複数行の Issue 本文は一時ファイルに書き出す。長い Markdown を shell command に直接埋め込まない。

```bash
mkdir -p /tmp/aiygin-issues
BUSINESS_BODY="/tmp/aiygin-issues/business.md"
BFF_BODY="/tmp/aiygin-issues/bff.md"
FE_BODY="/tmp/aiygin-issues/fe.md"
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

3. business Issue URL を含めて BFF Issue 本文を `$BFF_BODY` に書き、BFF Issue を作成する。

```bash
BFF_URL=$(gh issue create \
  --repo AIYGIN/bff \
  --title "[BFF] <機能名> の API / 契約対応" \
  --body-file "$BFF_BODY")

echo "$BFF_URL"
```

4. business Issue URL を含めて FE Issue 本文を `$FE_BODY` に書き、FE Issue を作成する。

```bash
FE_URL=$(gh issue create \
  --repo AIYGIN/fe \
  --title "[FE] <機能名> の画面 / UI 対応" \
  --body-file "$FE_BODY")

echo "$FE_URL"
```

5. business 親 Issue に子 Issue の URL をコメントする。

```bash
gh issue comment "$BUSINESS_URL" --body "実装 Issue を作成しました。

- BFF: $BFF_URL
- FE: $FE_URL"
```

6. 必要に応じて子 Issue 同士にも相互リンクをコメントする。

```bash
gh issue comment "$BFF_URL" --body "関連 FE Issue: $FE_URL"
gh issue comment "$FE_URL" --body "関連 BFF Issue: $BFF_URL"
```

## 事前確認のみ行う場合

ユーザーが明確に「自動登録して」「作成して」「Issue を立てて」と言っていない場合は、まず登録予定を提示する。

```text
登録予定:
- AIYGIN/business: [Feature] <機能名> の開発計画
- AIYGIN/bff: [BFF] <機能名> の API / 契約対応
- AIYGIN/fe: [FE] <機能名> の画面 / UI 対応

親子関係:
- business issue を親にして、bff / fe issue からリンクします。
- business issue に bff / fe issue URL をコメントで追記します。
```

ユーザーが「自動登録して」「作成して」「立てて」と明示した場合は、事前確認と重複確認を行ったうえで登録する。

## 重複 Issue の扱い

Issue 作成前に、複数のキーワードで検索する。

```bash
gh issue list --repo AIYGIN/business --state open --search "<機能名>" --limit 20
gh issue list --repo AIYGIN/business --state open --search "<主要キーワード>" --limit 20
```

business 親 Issue の重複候補がある場合。

- `gh issue view --repo AIYGIN/business <number>` で内容を確認する。
- 同じ計画を扱っているなら、既存 Issue を親として使う。
- 足りない BFF / FE 子 Issue だけ作成する。
- 新規作成した Issue URL を親 Issue にコメントする。

BFF / FE 子 Issue の重複候補がある場合。

- 重複 Issue は作らない。
- 親 Issue へ既存子 Issue のリンクを追記する。
- 既存子 Issue の内容が不足している場合は、不足要件をコメントで追記する。

## label と assignee

label は存在を確認してから使う。

```bash
gh label list --repo AIYGIN/business
gh label list --repo AIYGIN/bff
gh label list --repo AIYGIN/fe
```

存在しない label は使わない。ユーザーが明示しない限り、新規 label は作成しない。

存在する場合に使ってよい候補。

- `feature`
- `planning`
- `frontend`
- `bff`
- `security`
- `risk`

assignee は、ユーザーが指定した場合、またはリポジトリの明確な運用ルールが分かっている場合だけ設定する。推測で担当者を割り当てない。

## 品質ルール

- business Issue を横断要件の正本とする。
- BFF / FE 子 Issue の先頭付近に business Issue URL を必ず入れる。
- FE Issue では、BFF / OpenAPI 契約が確認される前に API 挙動を断定しない。
- BFF Issue では、契約変更がある場合に OpenAPI / DTO / Controller / docs decorator の対応を明記する。
- セキュリティ対策とリスクは、情報不足でも省略しない。`要確認` として残す。
- 実装可能な要件と受け入れ条件は checkbox にする。
- 詳細が不明な場合は `未確定` と書き、事実のように補完しない。
- Issue タイトルは短く検索しやすくする。
- FE 生成物、特に Orval 生成 API client / mock は手動編集しない前提で Issue に書く。
- frontend 都合だけで BFF レスポンス契約を変更しない。契約変更が必要な場合は business Issue と BFF Issue に明記する。

## よくある失敗

1. FE/BFF Issue を先に作ってしまう。必ず `AIYGIN/business` の親 Issue を先に作成・特定する。
2. business Issue からセキュリティ対策やリスク対策を省略する。このワークフローでは必須。
3. frontend の都合だけで BFF レスポンス契約を変える前提にする。必要なら契約変更として business / BFF Issue に明記する。
4. frontend の生成 API client を手動編集する前提にする。FE Issue ではプロジェクトのワークフローに従って再生成する旨を書く。
5. label や assignee が存在すると決めつける。事前に確認するか、指定しない。
6. 重複 Issue を作る。作成前に business / bff / fe を検索する。
7. business Issue へ子 Issue URL を戻し忘れる。
8. 情報不足を推測で埋める。`未確定` / `要確認` と書く。

## 完了確認チェックリスト

登録後、以下を確認する。

- [ ] `AIYGIN/business` に親 Issue が存在する。
- [ ] 親 Issue に BE、BFF、機能要件、UI要件、セキュリティ対策、リスク、リスク対策が含まれている。
- [ ] `AIYGIN/bff` に BFF 子 Issue が存在する、または既存 Issue を再利用している。
- [ ] `AIYGIN/fe` に FE 子 Issue が存在する、または既存 Issue を再利用している。
- [ ] 各子 Issue が business Issue にリンクしている。
- [ ] business Issue に BFF / FE 子 Issue の URL がコメントまたは本文更新で追記されている。
- [ ] 最終応答で作成・再利用した Issue URL をユーザーに報告している。
