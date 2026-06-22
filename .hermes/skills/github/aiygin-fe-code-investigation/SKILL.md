---
name: aiygin-fe-code-investigation
description: AIYGIN/fe のコード調査を CodeGraph 優先で行うための FE 専用 skill。Next.js routing、middleware、Orval、生成 API client、mock、Storybook、test、UI 導線を調査し、Issue 化や実装前の context を作る。
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [macos, linux]
metadata:
  hermes:
    tags: [aiygin, fe, nextjs, codegraph, investigation, orval]
    related_skills: [aiygin-codegraph-investigation-common, aiygin-fe-bff-issue-planning]
---

# AIYGIN/fe CodeGraph 調査

## 概要

この skill は、`AIYGIN/fe` のコード調査を FE 専用に行うための手順である。

`aiygin-codegraph-investigation-common` の共通ルールを前提に、Next.js routing、middleware、認証導線、Orval、生成 API client / mock、Storybook、test、UI component、状態管理の入口を CodeGraph 優先で調べる。

この skill は調査専用であり、Issue 作成、コード変更、PR 作成は行わない。

## 使用する場面

- business Issue 起票前に FE 側の現状と影響範囲を確認する。
- BFF API 契約変更が FE の Orval 生成物や UI に与える影響を調べる。
- FE 子 Issue 作成へ渡す repo 固有の注意点を整理する。
- 実装前に routing / page / component / Storybook / test の既存構成を把握する。

使わない場面。

- BFF の controller / service / repository / OpenAPI docs を調べる。
- FE Issue を直接作る。
- FE 実装や test 修正を行う。

## 前提

- local path は通常 `/Users/ynaragin/git/fe`。
- canonical repository は `https://github.com/AIYGIN/fe`。
- `/Users/ynaragin/git/fe` の remote が異なる場合は、canonical repo ではなく local remote misconfiguration と扱う。
- `.codegraph/codegraph.db` がある場合、grep/find や大量手読みより先に CodeGraph を使う。
- Orval 生成物は手動編集しない。
- `src/apis/generated` は本番コードから直接利用する。
- `src/apis` 直下に本番用 API wrapper や業務ロジックを追加しない。配置可能なのは Orval 共通 mutator と mock / test 用構成だけ。

## 最初に読む入口

調査サブエージェントは必要範囲で以下を読む。

```text
/Users/ynaragin/git/fe/AGENTS.md
/Users/ynaragin/git/fe/src/AGENTS.md
/Users/ynaragin/git/fe/docs/rules/frontend.md
/Users/ynaragin/git/fe/docs/rules/testing.md
/Users/ynaragin/git/fe/docs/rules/state-management.md
/Users/ynaragin/git/fe/docs/rules/ui.md
/Users/ynaragin/git/fe/.codex/workflows/sdd_flow.md
/Users/ynaragin/git/fe/.codex/agents/*.toml
```

全部を無条件に読むのではなく、対象要件に必要なものだけ読む。

## CodeGraph 質問例

対象要件に合わせて、以下のような質問を `codegraph explore` または `codegraph_explore` に投げる。

```text
Next.js の routing、page、layout、middleware、protected route の構成はどこか
login 画面、認証導線、未認証 redirect、認証後 redirect はどこで実装されているか
TODO 画面または対象機能画面の component、page、state、API 呼び出しはどこか
Orval 設定、OpenAPI 入力、生成 API client、mock の生成先と script はどこか
src/apis/generated を利用している UI / hook / service はどこか
Storybook stories、MSW mock、test の対象機能入口はどこか
```

候補が出たら、`codegraph node <symbol-or-file>` で詳細を確認する。

## FE 調査観点

必ず確認する観点。

- routing / page / layout / navigation
- middleware / protected route / public route
- login / logout / callback / redirect 導線
- 対象機能画面、TODO 画面、関連 component
- UI state、form、validation、error / loading / empty state
- BFF API 利用箇所
- Orval 設定、生成 script、生成物配置
- `src/apis/generated` 利用方針
- mock / MSW / Storybook / test / e2e
- `pnpm check`、`pnpm test`、`pnpm test:e2e` などの quality gate

## delegate_task 用 context template

```text
目的: AIYGIN/business の親 Issue と FE 子 Issue 委譲入力を作る前の FE コード調査。
対象要件: <ユーザー要件を貼る>
対象 repo: AIYGIN/fe
local path: /Users/ynaragin/git/fe
必須:
- AGENTS.md と必要な src/AGENTS.md / docs に従う。
- `.codegraph/` があれば CodeGraph を grep/find や大量手読みより先に使う。
- routing / middleware / login / protected route / 対象画面 / Orval / API client / mock / Storybook / test を確認する。
- Issue は作らない。
- コード変更しない。
- Orval 生成物を手動編集する前提にしない。
出力:
- 日本語。
- 事実、推測、未確認を分ける。
- aiygin-codegraph-investigation-common の調査結果 schema に従う。
```

## Issue planning に返す要約観点

business Issue 化や FE 子 Issue 委譲に渡すときは、以下を短くまとめる。

```text
FE 現状:
FE 差分:
UI / UX 要件に反映すべきこと:
API / Orval / mock への影響:
テスト / Storybook 方針:
FE 子 Issue 委譲時の注意点:
未確認事項:
```

## よくある失敗

1. BFF API response を FE 都合だけで変える前提にする。
2. Orval 生成物を手動編集する前提で Issue 化する。
3. `src/apis` 直下に本番用 API wrapper を追加する前提にする。
4. Storybook / mock / test の既存方針を見ずに UI タスクを切る。
5. `AGENTS.md` と `src/AGENTS.md` を読まずに調査する。
6. CodeGraph の候補 path を根拠行確認なしに断定する。

## 完了確認チェックリスト

- [ ] `/Users/ynaragin/git/fe/AGENTS.md` を確認した。
- [ ] 必要に応じて `src/AGENTS.md` と docs/rules を確認した。
- [ ] CodeGraph を優先利用した、または fallback 理由を明記した。
- [ ] routing / middleware / 対象画面 / API 利用箇所を確認した。
- [ ] Orval 設定、生成物、mock、再生成方針を確認した。
- [ ] Storybook / test / e2e の既存方針を確認した。
- [ ] Issue 作成やコード変更をしていない。
