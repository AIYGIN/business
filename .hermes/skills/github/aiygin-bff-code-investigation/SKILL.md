---
name: aiygin-bff-code-investigation
description: AIYGIN/bff のコード調査を CodeGraph 優先で行うための BFF 専用 skill。NestJS module、controller、service、resource、repository、DTO、OpenAPI docs、auth、DB、test/e2e を調査し、Issue 化や実装前の context を作る。
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [macos, linux]
metadata:
  hermes:
    tags: [aiygin, bff, nestjs, codegraph, investigation, openapi]
    related_skills: [aiygin-codegraph-investigation-common, aiygin-fe-bff-issue-planning]
---

# AIYGIN/bff CodeGraph 調査

## 概要

この skill は、`AIYGIN/bff` のコード調査を BFF 専用に行うための手順である。

`aiygin-codegraph-investigation-common` の共通ルールを前提に、NestJS module / controller / service / resource / repository、DTO、Swagger / OpenAPI docs decorator、認証・認可、Cookie / CORS / JWT、DB 接続、migration、test / e2e / OpenAPI e2e の入口を CodeGraph 優先で調べる。

この skill は調査専用であり、Issue 作成、コード変更、PR 作成は行わない。

## 使用する場面

- business Issue 起票前に BFF 側の現状と影響範囲を確認する。
- FE から利用する BFF API 契約、DTO、OpenAPI への影響を調べる。
- BFF 子 Issue 作成へ渡す repo 固有の注意点を整理する。
- 認証、認可、DB、外部連携、resource 層、test/e2e の既存構成を把握する。

使わない場面。

- FE の page / component / Storybook / Orval 生成物の利用箇所を調べる。
- BFF Issue を直接作る。
- BFF 実装や test 修正を行う。

## 前提

- local path は通常 `/Users/ynaragin/git/bff`。
- repository は `AIYGIN/bff`。
- `.codegraph/codegraph.db` がある場合、grep/find や大量手読みより先に CodeGraph を使う。
- API 完了条件は Swagger/OpenAPI で API 契約を表現できること。
- API 作業は Controller mock または実装を draft PR にする運用だが、この skill では PR や実装は行わない。
- 基盤作業は設定、DI、横断動作、機密情報保護、既存 API 非回帰を test で表現する前提だが、この skill では調査だけ行う。

## 最初に読む入口

調査サブエージェントは必要範囲で以下を読む。

```text
/Users/ynaragin/git/bff/AGENTS.md
/Users/ynaragin/git/bff/docs/bff-code-design-rules.md
/Users/ynaragin/git/bff/docs/swagger-openapi-rules.md
/Users/ynaragin/git/bff/docs/ai-api-harness.md
/Users/ynaragin/git/bff/docs/layer-boundaries.md
/Users/ynaragin/git/bff/.codex/workflows/api_controller_mock_flow.md
/Users/ynaragin/git/bff/.codex/workflows/api_implementation_flow.md
/Users/ynaragin/git/bff/.codex/workflows/foundation_implementation_flow.md
/Users/ynaragin/git/bff/.codex/agents/*.toml
```

全部を無条件に読むのではなく、対象要件に必要なものだけ読む。

## CodeGraph 質問例

対象要件に合わせて、以下のような質問を `codegraph explore` または `codegraph_explore` に投げる。

```text
対象機能に関連する NestJS module、controller、service、resource、repository はどこか
DTO、request/response model、validation、Swagger/OpenAPI docs decorator はどこか
認証 Guard、decorator、current user、JWT、Cookie、CORS の処理はどこか
DB 接続、repository、migration、entity/schema、transaction 境界はどこか
外部 HTTP client、resource 層、error mapping、retry/timeout はどこか
対象 API の unit test、e2e test、OpenAPI e2e test はどこか
```

候補が出たら、`codegraph node <symbol-or-file>` で詳細を確認する。

## BFF 調査観点

必ず確認する観点。

- NestJS module / controller / service / provider / DI
- resource 層、外部 HTTP client、error mapping
- repository / DB 接続 / migration / transaction
- DTO / validation / request / response
- Swagger / OpenAPI docs decorator
- Guard / decorator / current user / ownership boundary
- Cookie / CORS / JWT / session / auth flow
- test / e2e / OpenAPI e2e / AI API harness
- API 契約変更時の FE Orval 再生成への影響
- 既存 API 非回帰の確認ポイント

## delegate_task 用 context template

```text
目的: AIYGIN/business の親 Issue と BFF 子 Issue 委譲入力を作る前の BFF コード調査。
対象要件: <ユーザー要件を貼る>
対象 repo: AIYGIN/bff
local path: /Users/ynaragin/git/bff
必須:
- AGENTS.md と必要な docs / workflow に従う。
- `.codegraph/` があれば CodeGraph を grep/find や大量手読みより先に使う。
- module / controller / service / resource / repository / DTO / OpenAPI docs / auth / DB / test を確認する。
- Issue は作らない。
- コード変更しない。
- FE 都合だけで BFF response 契約を変える前提にしない。
出力:
- 日本語。
- 事実、推測、未確認を分ける。
- aiygin-codegraph-investigation-common の調査結果 schema に従う。
```

## Issue planning に返す要約観点

business Issue 化や BFF 子 Issue 委譲に渡すときは、以下を短くまとめる。

```text
BFF 現状:
BFF 差分:
API / OpenAPI / DTO へ反映すべきこと:
BE / DB / 外部連携への影響:
認証・認可・所有者境界:
test / e2e / OpenAPI e2e 方針:
BFF 子 Issue 委譲時の注意点:
未確認事項:
```

## よくある失敗

1. FE 都合だけで BFF response 契約を変更する前提にする。
2. Swagger / OpenAPI docs decorator の確認を省略する。
3. Controller だけ見て、service / resource / repository / test への影響を見落とす。
4. Guard / current user / ownership boundary を確認せずに認可要件を書く。
5. DB 接続や migration 方針を推測で埋める。
6. `AGENTS.md` と docs を読まずに調査する。
7. CodeGraph の候補 path を根拠行確認なしに断定する。

## 完了確認チェックリスト

- [ ] `/Users/ynaragin/git/bff/AGENTS.md` を確認した。
- [ ] 必要に応じて docs / workflow / agent role を確認した。
- [ ] CodeGraph を優先利用した、または fallback 理由を明記した。
- [ ] module / controller / service / resource / repository を確認した。
- [ ] DTO / OpenAPI docs decorator / validation を確認した。
- [ ] auth / Guard / Cookie / CORS / JWT / ownership boundary を確認した。
- [ ] DB / migration / external resource / test/e2e を確認した。
- [ ] Issue 作成やコード変更をしていない。
