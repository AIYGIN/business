---
name: pr-human-feedback-loop
description: Use when incorporating human PR comments into documents or code. Separates feedback collection, classification, edits, consistency checks, and verified commit/push, with Japanese reporting and subagent-friendly prompts.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [github, pull-requests, feedback, review, subagents, japanese]
    related_skills: [github-workflows, ai-coding-agents, proposal-planning-workflow]
---

# PR人間指摘 反映ループ

## agent-memory 記録ルール

PR人間指摘の反映では、コメント取得・分類・修正・矛盾チェック・push の作業自体を `agent-memory` コマンドで必ず記録する。`proposal-planning-workflow` の Phase 5 として実行する場合は特に必須。

```bash
rtk agent-memory write --content "pr feedback: <owner/repo>#<PR番号> 開始。対象=<files> / comments=<件数> / branch=<branch>"
rtk agent-memory write --content "pr feedback: <owner/repo>#<PR番号> 分類完了。対応=<件数> / 要確認=<件数> / 対応不要=<件数>"
rtk agent-memory write --content "pr feedback: <owner/repo>#<PR番号> 反映完了。files=<paths> / commit=<sha or 未commit> / push=<済|未> / 要確認=<項目>"
rtk agent-memory scratchpad add --text "pr feedback <owner/repo>#<PR番号>: <未完了TODOまたは要ユーザー確認>"
```

記録する内容:

- 開始時: 対象PR、対象ファイル、ブランチ、取得したコメント件数。
- 分類完了時: 対応する指摘、対応しない指摘、要ユーザー確認。
- 修正完了時: 更新ファイル、対応した指摘ID、未対応理由、矛盾チェック結果。
- commit/push時: commit要約、push結果、PRコメント有無。
- ブロック時: 原因、試したこと、再開条件。

注意:

- PR番号、commit SHA、進捗ログは daily log に残し、Hermes persistent memory には保存しない。
- 未完了TODOは scratchpad に追加し、完了したら `agent-memory scratchpad done --text "..."` で消す。
- `agent-memory write --target long_term` は、今後も使う安定したレビュー運用ルールだけに限定する。

## 目的

PRに付いた人間のコメント、レビュー、修正依頼を収集し、分類し、文書またはコードへ反映し、矛盾チェック後に commit/push する。

このスキルは、指摘をただ反映するのではなく、以下を分離して品質を保つ。

- 指摘収集
- 指摘分類
- 修正方針作成
- 実修正
- 矛盾/整合性チェック
- commit/push
- ユーザー報告

## 使うタイミング

- 「PRコメントを反映して」
- 「人間のレビュー指摘を直して」
- 「提案書PRの指摘を反映して矛盾チェックして」
- `proposal-planning-workflow` の Phase 5 を実行するとき

使わないケース:

- コメントがなく、単なる自己修正だけの場合
- ユーザーが特定の1行修正だけを明示している場合
- PR外の口頭フィードバックだけで、GitHub確認が不要な場合

## 事前確認

作業前に以下を確認する。

```bash
rtk git -C <repo> status --short --branch
gh -R <owner/repo> pr view <PR番号> --json number,title,headRefName,baseRefName,url,comments,reviews
```

確認ポイント:

- 対象PRが正しい
- 現在ブランチがPRブランチ、またはPRブランチにcheckout可能
- 作業ツリーに意図しない変更がない
- コメント/レビューを取得できている

## サブエージェント分離

### 1. 指摘収集サブエージェント

役割:

- PRコメント、レビューコメント、会話を取得する。
- 指摘を重複排除する。
- 指摘を分類する。

分類:

- 事実修正
- 論理矛盾
- 不足情報
- 表現修正
- スコープ変更
- 要ユーザー確認
- 対応不要/既対応

出力形式:

```markdown
## 指摘一覧
| ID | 種別 | 指摘内容 | 対象ファイル/箇所 | 推奨対応 | 要確認 |
|---|---|---|---|---|---|
```

### 2. 修正サブエージェント

役割:

- 指摘一覧に基づき、対象ファイルを修正する。
- 未確認事項を断定しない。
- スコープ変更や判断が必要なものは勝手に反映せず、要ユーザー確認に回す。

出力:

- 修正したファイル
- 反映した指摘ID
- 反映しなかった指摘IDと理由
- 要ユーザー確認事項

### 3. 矛盾チェックサブエージェント

役割:

- 修正後のファイルを読み比べる。
- 提案、レビュー報告書、PR本文、コメント返信が矛盾していないか確認する。

確認観点:

- 目的と実行計画が一致しているか
- コスト/リスク/実現可能性の記述が矛盾していないか
- 対象外スコープを実行計画に入れていないか
- 未確認事項を断定していないか
- 人間指摘への対応漏れがないか

出力形式:

```markdown
## 矛盾チェック結果
- 結論:
- 問題なし:
- 要修正:
- 要ユーザー確認:
```

## 親エージェントの責任

親エージェントは、サブエージェントの自己申告だけで完了扱いにしない。

必ず行うこと:

1. `rtk git diff` で変更内容を確認する。
2. 修正対象ファイルを読み返す。
3. 要ユーザー確認がある場合は commit/push せず止める。
4. 問題なければ commit/push する。
5. 必要に応じてPRコメントで対応内容を報告する。

## commit/push 手順

```bash
rtk git -C <repo> diff -- <paths>
rtk git -C <repo> status --short --branch
rtk git -C <repo> add <paths>
rtk git -C <repo> commit -m "docs: address review feedback"
rtk git -C <repo> push
```

PRに返信する場合:

```bash
gh -R <owner/repo> pr comment <PR番号> --body-file /tmp/<topic>-feedback-response.md
```

## 提案書PRでの追加観点

提案書・レビュー報告書の場合は、以下も確認する。

- 提案書とシステムレビュー報告書の結論が矛盾していないか
- コスト、リスク、実現可能性、既存サービス/代用手段の評価が一致しているか
- レビュー報告書で「要確認」とした内容を提案書本文で断定していないか
- ユーザー確認ゲートで承認された前提から逸脱していないか

## Common Pitfalls

1. PRコメントを一部だけ見て、レビューコメントを取り逃す。
2. 指摘を分類せず、対応要否が曖昧なまま修正する。
3. スコープ変更をユーザー確認なしに反映する。
4. 修正後の矛盾チェックを省略する。
5. サブエージェントの「完了しました」を検証せずにpushする。
6. PRコメントで対応済みと言いながらcommitがpushされていない。

## Verification Checklist

- [ ] PRコメント/レビューを取得した。
- [ ] 指摘を分類し、対応要否を整理した。
- [ ] 要ユーザー確認事項を勝手に反映していない。
- [ ] 修正後に矛盾チェックを実施した。
- [ ] 親エージェントがdiffと対象ファイルを確認した。
- [ ] commit/pushした場合、実コマンド結果を確認した。
- [ ] 必要に応じてPRへ対応報告コメントを残した。
- [ ] コメント取得・分類・修正・矛盾チェック・commit/push・残TODOを `agent-memory write` / `agent-memory scratchpad add` で記録した。
