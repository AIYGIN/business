---
name: aiygin-codegraph-investigation-common
description: AIYGIN リポジトリで CodeGraph 優先のコード調査を行う共通手順。FE/BFF など個別調査 skill から参照し、delegate_task 用 context、出力 schema、fallback 方針、禁止事項を標準化する。
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [macos, linux]
metadata:
  hermes:
    tags: [aiygin, codegraph, investigation, context-engineering, delegate-task]
    related_skills: [aiygin-fe-code-investigation, aiygin-bff-code-investigation]
---

# AIYGIN CodeGraph 共通コード調査

## 概要

この skill は、AIYGIN 系リポジトリでコード調査を行うときの共通手順である。

目的は、親エージェントが大量のファイルを直接読むのではなく、調査サブエージェントに狭い context と明確な出力 schema を渡し、CodeGraph で探索範囲を絞ってから必要最小限のファイルだけ確認することにある。

FE 固有の調査は `aiygin-fe-code-investigation`、BFF 固有の調査は `aiygin-bff-code-investigation` を使う。この skill は共通ルール、context template、出力形式だけを定義する。

## 使用する場面

- AIYGIN/fe、AIYGIN/bff、AIYGIN/business などで実装前の影響範囲を調べる。
- business Issue 化の前に FE/BFF の現状をコードから確認する。
- PR レビュー、仕様変更、契約変更、認証・権限変更の影響範囲を CodeGraph で探索する。
- `delegate_task` のサブエージェントへ調査を委譲する。

使わない場面。

- GitHub Issue 作成そのもの。
- コード変更、PR 作成、実装作業そのもの。
- CodeGraph ではなく外部仕様や市場情報を調べるだけの調査。

## 基本ルール

- 調査、設計、Issue 発行、実装を同じサブエージェントに混ぜない。
- 調査サブエージェントは Issue を作らない。
- 調査サブエージェントはコード変更しない。
- `AGENTS.md` がある場合は最初に読む。
- `.codegraph/` がある場合、grep/find や大量手読みより先に CodeGraph を使う。
- CodeGraph で path / symbol / 呼び出し関係を絞ってから、必要最小限のファイルだけ読む。
- 未確認事項は推測で埋めず、`未確認` と書く。
- 事実、推測、提案を分けて報告する。

## CodeGraph 優先探索

MCP が使える場合。

```text
1. codegraph_explore で広い質問を投げる。
2. 候補 symbol / file が見えたら codegraph_node で詳細を見る。
3. 呼び出し元・影響範囲が必要な場合は codegraph_callers を使う。
```

Shell だけの場合。

```bash
codegraph explore "<調査したい質問>"
codegraph node <symbol-or-file>
```

`rtk` が使える環境では、shell command に原則 `rtk` を prefix する。ただし CodeGraph の raw output が必要な場合や `rtk` 経由で問題が出る場合は通常コマンドに戻してよい。

## fallback 条件

以下の場合だけ `search_files` / `read_file` / `rtk grep` に fallback する。

- `.codegraph/` が存在しない。
- `.codegraph/codegraph.db` が存在しない。
- `codegraph` command または MCP tool が利用できない。
- CodeGraph が明確に古く、対象ファイルや symbol を返さない。
- CodeGraph の結果だけでは根拠行を確認できない。

fallback した場合は、調査結果に必ず理由を書く。

```text
CodeGraph fallback 理由:
- <例: codegraph command が PATH にない>
- <例: 対象 symbol が CodeGraph から見つからず、search_files で補完>
```

## delegate_task 共通 template

調査を委譲するときは、以下の情報を context に含める。

```text
目的: <何のためのコード調査か。例: business Issue 起票前の影響範囲確認>
対象要件: <ユーザー要件、Issue 草案、仕様メモ>
対象 repo: <AIYGIN/fe または AIYGIN/bff など>
local path: <ローカル clone path>
必須:
- AGENTS.md に従う。
- `.codegraph/` があれば CodeGraph を grep/find や大量手読みより先に使う。
- Issue は作らない。
- コード変更しない。
- 調査、設計、実装を混ぜない。
出力:
- 日本語。
- 事実、推測、未確認を分ける。
- 下記の調査結果 schema に従う。
```

推奨 toolsets。

```text
["terminal", "file"]
```

必要な場合だけ `web` を追加する。子エージェントにユーザー対話を期待しない。

## 調査結果 schema

調査サブエージェントは以下の形で返す。

```text
## 調査対象
- repository:
- local path:
- branch:
- HEAD:

## 参照した入口ルール
- AGENTS.md:
- 追加 docs / workflow / agent role:

## CodeGraph 利用状況
- 利用可否:
- 使った質問:
- 確認した symbol / path:
- fallback 有無と理由:

## 現在の構成
- <確認できた構成を箇条書き>

## 確認した path / symbol と根拠
- `<path or symbol>`: <何を確認したか>

## 既存の規約・script・template
- <repo 固有の規約や script>

## 今回要件との差分
- <実装済み / 未実装 / 変更必要>

## Issue / 設計へ反映すべき制約
- <契約、生成物、テスト、権限、運用上の制約>

## 子 Issue 委譲先に渡す注意点
- <FE/BFF 子 Issue 作成側へ渡すべき repo 固有情報>

## 未確認事項
- <未確認、要確認>
```

## よくある失敗

1. CodeGraph を使わず、最初から grep/find と大量手読みに入る。
2. 調査サブエージェントに Issue 作成や実装まで任せてしまう。
3. CodeGraph の質問、確認 symbol、fallback 理由を記録しない。
4. 未確認事項を推測で埋める。
5. 親エージェントがサブエージェントの全ログを読む前提にして context を膨らませる。

## 完了確認チェックリスト

- [ ] AGENTS.md を確認した。
- [ ] CodeGraph を優先利用した、または fallback 理由を明記した。
- [ ] 調査対象 branch / HEAD を記録した。
- [ ] 確認した path / symbol を記録した。
- [ ] 事実、推測、未確認を分けた。
- [ ] Issue 作成やコード変更をしていない。
