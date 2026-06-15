# AIYGIN/business 親 Issue テンプレート

このテンプレートは、AIYGIN/business issue #1（Google OAuth 2.0 + BFF JWT Cookie 認証基盤）で確定した構成をベースにした、FE/BFF 横断開発計画の親 Issue 用テンプレートである。

Issue 発行時は、この見出し構成と検証ルールをベースにし、要件に応じて内容を置き換える。特定機能（login / auth / todo 等）に依存する文言は、対象機能に合わせて置換する。

## 必須見出し

以下の見出しを原則として欠落させない。

```markdown
## 概要

## 背景・目的

## スコープ
### 対象
### 対象外

## Next.js / BFF 疎通フロー

## フローチャート

## 機能要件

## UI要件

## BE要件

## BFF要件

## セキュリティ対策

## リスク

## リスク対策

## Test 方針

## 受け入れ条件

## FE/BFF 子 Issue 作成

## 委譲用入力
### FE 向け
### BFF 向け

## 未決事項

## 参考
```

## Issue 発行時のルール

- Issue 本文は極力日本語で書く。Mermaid node label、補足、受け入れ条件、委譲用入力も日本語を優先し、API 名・endpoint・env・コード識別子だけ英語表記を許容する。
- 新規 Issue 作成または既存 Issue 更新では、まず本文全体を一時ファイルへ書き出す。
- 部分置換で本文を更新する場合も、更新前後の見出し一覧を比較する。
- `## フローチャート` など中間セクションを差し替える場合、次の `## ...` 見出し以降を削除しない。
- GitHub Mermaid を使う場合は、node label を `A["..."]` のように quote し、`/login` や URL など parser と衝突しやすい文字を裸で置かない。
- 更新後に `gh issue view --json body` で本文を取得し、必須見出し、Orval、DB、委譲用入力、受け入れ条件の有無を確認する。

## FE 向けの汎用観点

- routing / page / layout / middleware / protected route / public route
- 画面生成、UI component、表示状態、空状態、loading、error、validation
- user action、navigation、redirect、modal、toast、form/input
- BFF OpenAPI から Orval で API client / mock を自動生成する前提
- Orval 生成物を手動編集しないこと
- BFF 契約変更時の OpenAPI 更新と FE 側 Orval 再生成
- FE test / e2e / mock 方針

## BFF 向けの汎用観点

- endpoint / DTO / OpenAPI / docs decorator
- controller / service / resource / repository の責務分離
- DB / migration / external API / backend integration
- authn/authz、owner scope、guard/decorator、input validation
- error response、provider error masking、logging、security
- unit / integration / e2e / OpenAPI e2e test

## 発行後 verification 例

```bash
gh issue view <number> --repo AIYGIN/business --json body --jq '
  .body as $b |
  {
    has_overview: ($b | contains("## 概要")),
    has_requirements: ($b | contains("## 機能要件")),
    has_ui: ($b | contains("## UI要件")),
    has_bff: ($b | contains("## BFF要件")),
    has_risk: ($b | contains("## リスク")),
    has_acceptance: ($b | contains("## 受け入れ条件")),
    has_delegation: ($b | contains("## 委譲用入力")),
    headings: [$b | split("\n")[] | select(startswith("## "))]
  }'
```

## 参考となる実例

- AIYGIN/business #1: Google OAuth 2.0 + BFF JWT Cookie 認証基盤の開発計画
  - フローチャート追加後に本文欠落が発生したため、復元後の構成をこのテンプレートのベースにする。
  - 今後は、同じ見出し構成・検証手順を使って欠落を防ぐ。
