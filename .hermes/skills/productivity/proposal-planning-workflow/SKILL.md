---
name: proposal-planning-workflow
description: Use when orchestrating Japanese proposal creation/review workflows with user confirmation, subagent research, proposal-review-drafter, proposal-system-reviewer, AIYGIN/business planning PRs, and follow-up human review fixes.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [proposal, workflow, subagents, github, planning, japanese, productivity]
    related_skills: [proposal-preflight-research, user-confirmation-gate, pr-human-feedback-loop, proposal-review-drafter, proposal-system-reviewer, github-workflows, ai-coding-agents]
---

# 提案書作成・レビューPR化ワークフロー

## 目的

ユーザーの曖昧なアイデア、または指定されたMarkdown文書から「やりたいこと」を理解し、事前調査、ユーザー確認、提案書作成、システム観点レビュー、AIYGIN/business の `planning/` 配下へのPR化、人間指摘への修正までを一連のワークフローとして実行する。

このスキルは、`proposal-review-drafter` と `proposal-system-reviewer` を単発利用ではなく、段階分離されたサブエージェント運用とGitHub PR運用に接続するための司令塔として使う。

## 使うタイミング

以下の依頼で使う。

- 「提案書作成からレビュー、PR化まで回して」
- 「proposal-review-drafter と proposal-system-reviewer を使ったワークフローを実行して」
- 「アイデアを聞いて、調査して、提案書にして、planningにPRを出して」
- 「PRの人間コメントを反映して提案書を直して」
- 「AIYGIN/business の planning に提案書・レビュー報告書を追加して」

使わないケース:

- 単純な文章添削だけで、調査・確認・PR化が不要な場合
- 法務・会計・投資判断の最終承認そのもの
- ユーザーが明示的に「PR化しない」「調査しない」と指定した場合

## 全体原則

1. 日本語で進める。
2. 事実、仮定、推論、要確認を分ける。
3. 曖昧な依頼には、回答・作業開始前に最大3つの確認質問をする。
4. ユーザーがMarkdown文書を指定した場合は、先にその内容を読み、目的・読み手・意思決定・制約を抽出する。
5. 調査結果を提示し、ユーザーの確認が取れるまで提案書作成・PR化に進まない。
6. サブエージェントの自己申告を信用せず、親エージェントがファイル、diff、PR URL、コマンド結果を確認する。
7. AIYGIN/business の作業は `/Users/ynaragin/git/business` を使い、成果物は原則 `planning/` 配下に置く。
8. 既存の作業ツリー変更を壊さない。作業前に git status と remote を確認する。
9. 作業自体の記録を `agent-memory` コマンドで必ず残す。開始時、各Phase完了時、ブロック時、PR/コメント作成時、完了時に、何をしたか・対象ファイル/PR・判断・残TODOを daily log へ書く。未完了TODOは scratchpad に追加する。安定した設計/運用決定だけ long_term に残す。

## agent-memory 記録ルール

提案ワークフローでは、成果物だけでなく作業プロセス自体を再追跡できるように、親エージェントが以下を実行する。

```bash
rtk agent-memory write --content "proposal: <topic> 開始。入力=<概要> / repo=<repo> / 予定Phase=<phase>"
rtk agent-memory write --content "proposal: <topic> Phase <N> 完了。実施=<内容> / 判断=<決定> / files=<path> / pr=<url or 未作成> / next=<次作業>"
rtk agent-memory scratchpad add --text "proposal <topic>: <残TODOまたは要確認>"
```

記録する内容:

- 開始時: テーマ、入力元、対象repo、想定成果物。
- 各Phase完了時: 実施内容、判断、作成/更新ファイル、PR URL、次アクション。
- ブロック時: 原因、試したこと、再開条件。
- 人間確認待ち: 確認したい事項、保留している作業。
- 完了時: 最終成果物、PR URL、残課題、ユーザーが次に見るべきポイント。

注意:

- `agent-memory write` は原則 daily log 用に使い、作業履歴・PR番号・一時的な進捗を Hermes persistent memory へ保存しない。
- `agent-memory scratchpad` は未完了TODOだけに使い、完了したら `done` する。
- `agent-memory write --target long_term` は、今後も再利用する安定した設計判断・運用ルールだけに限定する。

## Phase 0: 入力理解・ヒアリング

### 入力パターンA: 口頭/チャット依頼

最初に以下を抽出する。

- 提案テーマ
- 読み手・決裁者
- 期待する意思決定（承認、予算化、PoC開始、採用、廃止など）
- 背景・課題
- 期限・制約
- 既知の競合案・代替案

不足していて作業方針が変わる場合は、最大3問だけ確認する。

確認質問例:

1. この提案の読み手・決裁者は誰ですか。
2. 最終的に承認してほしい判断は何ですか（PoC開始、予算化、実装着手など）。
3. 既に前提として使いたいMarkdown文書、既存Issue、参考URLはありますか。

### 入力パターンB: Markdown文書指定

ユーザーがMarkdownファイルを指定した場合は、次を実行する。

1. `read_file` で対象ファイルを読む。
2. 目的、対象者、意思決定、制約、未確認事項を抽出する。
3. 不足情報があれば最大3問だけ確認する。
4. 追加確認が不要なら、抽出結果を「理解したやりたいこと」として短く提示する。

## Phase 1: 事前調査サブエージェント

このPhaseでは `proposal-preflight-research` を必ず併用する。

親エージェントは、提案テーマ、背景、読み手、期待する意思決定、制約、前提資料を整理し、`proposal-preflight-research` のテンプレートに従って別サブエージェントへ調査を依頼する。

調査で必ず扱う観点:

- コスト
- リスク
- 実現可能性
- 既存サービス・代用手段

親エージェントは、サブエージェントの結果をそのまま貼らず、`proposal-preflight-research` の集約ルールに従って、事実・仮定/推論・要確認・推奨方針・ユーザーに確認すべき判断事項へ整理する。

## Phase 2: ユーザー確認ゲート

このPhaseでは `user-confirmation-gate` を必ず併用する。

Phase 1 の調査結果を提示した後、`user-confirmation-gate` の標準提示フォーマットに従って、次工程へ進む前にユーザー確認を取る。

提示内容:

- 理解したやりたいこと
- 事実、仮定/推論、要確認
- コスト見立て
- 主要リスク
- 実現可能性
- 既存サービス/代用手段
- 推奨方針
- 次に作る成果物
- ユーザーに確認したいこと（最大3問）

ユーザーの確認が取れるまで、`proposal-review-drafter` に提案書作成を依頼しない。

## Phase 3: proposal-review-drafter による提案書作成とPR化

ユーザー確認後、`proposal-review-drafter` を使って提案書ドラフトを作成する。

作成時の追加条件:

- Phase 1 の調査結果を反映する。
- コスト、リスク、実現可能性、既存サービス/代用手段を提案書内に含める。
- 数字・外部情報は出典または `[要確認]` を付ける。
- 断定できない項目は「仮定」「要確認」に分ける。
- 成果物は最終的に `/Users/ynaragin/git/business/planning/<YYYYMMDD>-<short-topic>-proposal.md` に配置する。

GitHub作業手順:

```bash
rtk git -C /Users/ynaragin/git/business remote -v
rtk git -C /Users/ynaragin/git/business status --short --branch
rtk git -C /Users/ynaragin/git/business fetch origin main --prune
rtk git -C /Users/ynaragin/git/business checkout -B planning/<short-topic> origin/main
rtk git -C /Users/ynaragin/git/business add planning/<proposal-file>.md
rtk git -C /Users/ynaragin/git/business commit -m "docs: add <topic> proposal"
rtk git -C /Users/ynaragin/git/business push -u origin planning/<short-topic>
gh -R AIYGIN/business pr create --base main --head planning/<short-topic> --title "docs: <日本語タイトル>" --body-file /tmp/<topic>-pr-body.md
```

注意:

- `rtk` を使う環境では、git系コマンドに `rtk` を付ける。
- `gh` のPR作成結果からURLを確認する。
- PR作成後、親エージェントが `gh pr view` でURL・ブランチ・変更ファイルを確認する。

## Phase 4: proposal-system-reviewer によるレビュー報告書作成

Phase 3 で作成した提案書に対して、`proposal-system-reviewer` を使ってレビュー報告書を別Markdownで作成する。

レビュー報告書の配置:

```text
/Users/ynaragin/git/business/planning/<YYYYMMDD>-<short-topic>-system-review.md
```

レビュー報告書に含めるもの:

- 結論
- 前提整理（事実/仮定/要確認）
- コスト観点
- 実現可能性
- システム構成案（必要ならPlantUML）
- セキュリティリスク
- 障害点と対策
- キャッシュ/データ保持方針
- 既存サービス・代用手段との比較
- 提案書本文に反映すべき修正提案
- 人間レビューで決めるべき事項

GitHub作業:

```bash
rtk git -C /Users/ynaragin/git/business status --short --branch
rtk git -C /Users/ynaragin/git/business add planning/<system-review-file>.md planning/<proposal-file>.md
rtk git -C /Users/ynaragin/git/business commit -m "docs: add <topic> system review"
rtk git -C /Users/ynaragin/git/business push
```

完了後、PRにレビュー要点コメントを残す。

```bash
gh -R AIYGIN/business pr comment <PR番号> --body-file /tmp/<topic>-system-review-comment.md
```

## Phase 5: 人間指摘の反映ループ

このPhaseでは `pr-human-feedback-loop` を必ず併用する。

PRに人間から指摘があった場合、`pr-human-feedback-loop` の手順に従い、以下を分離して実施する。

1. 指摘収集サブエージェント
   - PRコメント/レビューコメントを取得する。
   - 指摘を重複排除し、事実修正、論理矛盾、不足情報、表現修正、スコープ変更、要ユーザー確認、対応不要/既対応に分類する。
2. 修正サブエージェント
   - 指摘一覧に基づき、`planning/` 内の提案書・レビュー報告書を修正する。
   - 未確認情報を断定しない。
   - スコープ変更や判断が必要なものは勝手に反映せず、要ユーザー確認に回す。
3. 矛盾チェックサブエージェント
   - 修正後の提案書とレビュー報告書を読み比べる。
   - 目的、実行計画、コスト、リスク、実現可能性、既存サービス/代用手段、未確認事項の扱いが矛盾していないか確認する。

親エージェントは、サブエージェントの自己申告では完了扱いにせず、`pr-human-feedback-loop` の親エージェント責任に従って、最終diff、対象ファイル、要ユーザー確認事項を確認してから commit/push する。

```bash
rtk git -C /Users/ynaragin/git/business diff -- planning/
rtk git -C /Users/ynaragin/git/business add planning/<files>
rtk git -C /Users/ynaragin/git/business commit -m "docs: address review feedback for <topic>"
rtk git -C /Users/ynaragin/git/business push
```

## リポジトリ内へのワークフロー資産配置

AIYGIN/business のように、リポジトリ内で Hermes skill を共有・再利用する場合は、ローカルの `~/.hermes/skills/` から対象リポジトリの `.hermes/skills/` へコピーする。

対象 skill:

- `proposal-review-drafter`
- `proposal-system-reviewer`
- `proposal-planning-workflow`
- `proposal-preflight-research`
- `user-confirmation-gate`
- `pr-human-feedback-loop`

配置例:

```bash
rtk mkdir -p /Users/ynaragin/git/business/.hermes/skills/productivity \
  /Users/ynaragin/git/business/.hermes/skills/workflow \
  /Users/ynaragin/git/business/.hermes/skills/github

rtk cp -R /Users/ynaragin/.hermes/skills/productivity/proposal-review-drafter \
  /Users/ynaragin/git/business/.hermes/skills/productivity/
rtk cp -R /Users/ynaragin/.hermes/skills/productivity/proposal-system-reviewer \
  /Users/ynaragin/git/business/.hermes/skills/productivity/
rtk cp -R /Users/ynaragin/.hermes/skills/productivity/proposal-planning-workflow \
  /Users/ynaragin/git/business/.hermes/skills/productivity/
rtk cp -R /Users/ynaragin/.hermes/skills/productivity/proposal-preflight-research \
  /Users/ynaragin/git/business/.hermes/skills/productivity/
rtk cp -R /Users/ynaragin/.hermes/skills/workflow/user-confirmation-gate \
  /Users/ynaragin/git/business/.hermes/skills/workflow/
rtk cp -R /Users/ynaragin/.hermes/skills/github/pr-human-feedback-loop \
  /Users/ynaragin/git/business/.hermes/skills/github/
```

注意:

- コピー先は skill ディレクトリ名そのものではなく、カテゴリ親ディレクトリにする。
- 例: `.../productivity/` にコピーする。`.../productivity/proposal-review-drafter` をコピー先にすると、既存ディレクトリがある場合に `proposal-review-drafter/proposal-review-drafter/` の二重ディレクトリになり得る。
- 既存ディレクトリを更新する場合は、対象 skill だけを削除してからコピーし直す。
- コピー後は `SKILL.md` が期待パスに存在することを確認する。

確認例:

```bash
rtk git -C /Users/ynaragin/git/business status --short --untracked-files=all
```

期待パス例:

```text
/Users/ynaragin/git/business/.hermes/skills/productivity/proposal-planning-workflow/SKILL.md
/Users/ynaragin/git/business/.hermes/skills/productivity/proposal-preflight-research/SKILL.md
/Users/ynaragin/git/business/.hermes/skills/workflow/user-confirmation-gate/SKILL.md
/Users/ynaragin/git/business/.hermes/skills/github/pr-human-feedback-loop/SKILL.md
```

## サブエージェント分離方針

親エージェント:

- ユーザーとの確認
- 作業範囲の決定
- サブエージェントへの指示
- 最終成果物の読み返し
- git/gh の実行確認
- ユーザーへの報告
- サブエージェント失敗時のフォールバック判断と明示的な記録

### サブエージェント失敗時のフォールバック

サブエージェントが timeout、Broken pipe、ネットワーク/API失敗、max_iterations などで完了しない場合でも、親エージェントが取得済みの入力・調査結果・skill本文だけで安全に進められる範囲なら、作業を止めずに以下を実行する。

1. 失敗した担当範囲を確認し、成果物の品質に影響する未確認事項を分ける。
2. 親エージェント側で不足調査・ドラフト・レビューを補完する。
3. 補完した成果物を `read_file` / diff / `gh pr view` などで実際に確認する。
4. `agent-memory write` に「どのサブエージェントが失敗し、親が何を補完したか」を記録する。
5. 最終報告では、サブエージェント失敗を隠さず、どの範囲を親エージェントが補完・検証したかを明記する。

ただし、法務判断、外部公開、費用発生、ユーザー判断が必要な前提が欠ける場合は、補完で進めず確認ゲートに戻す。

調査サブエージェント:

- コスト、リスク、実現可能性、代替手段の調査

ドラフト作成サブエージェント:

- `proposal-review-drafter` に従った提案書初稿の作成

システムレビューサブエージェント:

- `proposal-system-reviewer` に従ったレビュー報告書の作成

指摘収集サブエージェント:

- PRコメント/レビューコメントの分類

文書修正サブエージェント:

- 指摘に基づくMarkdown修正

矛盾チェックサブエージェント:

- 修正後文書の整合性確認

## 完了報告フォーマット

ユーザーへの報告は以下の順で行う。

1. 結論
2. 作成/更新したファイル
3. PR URL
4. 反映した要点
5. 残っている要確認事項
6. 次に人間が見るべきポイント

## Token/時間コスト最適化

このワークフローはサブエージェント、Web調査、GitHub確認を多用するため、以下で重複作業とtoken消費を抑える。

1. Markdown指定入力では、Phase 0で親エージェントが要件要約を1つ作り、以後のサブエージェントには全文ではなく「要件要約 + 変更不可の前提 + 担当観点」だけを渡す。
2. 事前調査サブエージェントは、観点ごとに分けすぎない。小規模/個人利用/検証用の提案では、原則1エージェントに `cost/risk/feasibility/alternatives` をまとめて依頼する。大規模・法務/技術不確実性が高い場合だけ2〜3分割する。
3. Web調査は、まず親エージェントが検索語と出典候補を絞り、サブエージェントには最大5〜8URL相当の調査に制限する。API/サービス候補は代表3件程度を初期上限にし、網羅調査・ベンダー比較・規約/再配信/キャッシュ可否の深掘りが必要そうなら、調査を広げる前にユーザー確認ゲートへ戻る。タイムアウトしたサブエージェントを再実行せず、親側で不足観点だけ補完する。
4. 提案書ドラフトとシステムレビューのサブエージェントは、短い文書・構成が明確な文書では使わず、親エージェントがテンプレートから直接作成してよい。サブエージェントを使うのは、専門性が高い、長大、または並列レビューの価値が明確な場合に限定する。
5. PR人間指摘が短い/構造化されている場合は、指摘分類と矛盾チェックをサブエージェントに分けず、親エージェントが表で分類し、`search_files` と `git diff` で確認する。大量コメントやコード変更を伴う場合だけサブエージェント分離する。
6. 画像つきPRコメントは、まず親エージェントが `vision_analyze` で抽出し、その抽出結果だけを修正作業に使う。画像URLやPR全文を複数サブエージェントに重複投入しない。
7. commit/push/PR確認は親エージェントだけが行う。サブエージェントには外部副作用を任せない。
8. agent-memory記録はPhase単位にまとめ、同一Phase内での細かい中間ログを増やしすぎない。ただし開始・確認ゲート・PR作成・人間レビュー反映・ブロックは記録する。

## Common Pitfalls

1. ユーザー確認前に提案書作成・PR化まで進める。
2. サブエージェントの調査結果を検証せずに断定する。
3. 既存サービスや代用手段の存在を調べずに内製前提で提案する。
4. `proposal-system-reviewer` の結果を提案書本文と矛盾したまま別紙にする。
5. PRコメントだけして、レビュー報告書ファイルをコミットし忘れる。
6. 人間指摘を反映した後に矛盾チェックをしない。
7. AIYGIN/business 以外のremoteや未確認のdirty treeで作業する。
8. サブエージェントが timeout / Broken pipe で失敗したのに、失敗範囲・親エージェント補完・検証結果を記録/報告しない。

## Verification Checklist

- [ ] 曖昧な依頼には最大3問で確認した、またはMarkdown文書を読んで意図を抽出した。
- [ ] 事前調査サブエージェントでコスト、リスク、実現可能性、既存サービス/代用手段を確認した。
- [ ] サブエージェントが失敗した場合、失敗範囲・親エージェント補完・実検証結果を agent-memory と最終報告に明記した。
- [ ] 調査結果をユーザーに提示し、提案書作成前に確認を取った。
- [ ] `proposal-review-drafter` に従う提案書を `planning/` 配下に作成した。
- [ ] 提案書を commit/push し、PR URLを確認した。
- [ ] `proposal-system-reviewer` に従うレビュー報告書を別ファイルとして作成した。
- [ ] レビュー報告書を同じPRブランチに commit/push した。
- [ ] PRにレビュー要点コメントを残した。
- [ ] 人間指摘がある場合、指摘収集・文書修正・矛盾チェックを分離して実施した。
- [ ] 最終diff、PR URL、残課題を親エージェントが確認した。
- [ ] 開始時、各Phase完了時、ブロック時、PR/コメント作成時、完了時の作業ログを `agent-memory write` で残した。
- [ ] 未完了TODOや人間確認待ちは `agent-memory scratchpad add` に残し、完了済みTODOは `done` した。
- [ ] ワークフロー skill 群をリポジトリ内 `.hermes/skills/` に共有配置する場合、カテゴリ親ディレクトリへコピーし、二重ディレクトリになっていないことを確認した。
