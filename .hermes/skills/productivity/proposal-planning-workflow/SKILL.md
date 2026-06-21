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

## サブエージェント分離方針

親エージェント:

- ユーザーとの確認
- 作業範囲の決定
- サブエージェントへの指示
- 最終成果物の読み返し
- git/gh の実行確認
- ユーザーへの報告

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

## Common Pitfalls

1. ユーザー確認前に提案書作成・PR化まで進める。
2. サブエージェントの調査結果を検証せずに断定する。
3. 既存サービスや代用手段の存在を調べずに内製前提で提案する。
4. `proposal-system-reviewer` の結果を提案書本文と矛盾したまま別紙にする。
5. PRコメントだけして、レビュー報告書ファイルをコミットし忘れる。
6. 人間指摘を反映した後に矛盾チェックをしない。
7. AIYGIN/business 以外のremoteや未確認のdirty treeで作業する。

## Verification Checklist

- [ ] 曖昧な依頼には最大3問で確認した、またはMarkdown文書を読んで意図を抽出した。
- [ ] 事前調査サブエージェントでコスト、リスク、実現可能性、既存サービス/代用手段を確認した。
- [ ] 調査結果をユーザーに提示し、提案書作成前に確認を取った。
- [ ] `proposal-review-drafter` に従う提案書を `planning/` 配下に作成した。
- [ ] 提案書を commit/push し、PR URLを確認した。
- [ ] `proposal-system-reviewer` に従うレビュー報告書を別ファイルとして作成した。
- [ ] レビュー報告書を同じPRブランチに commit/push した。
- [ ] PRにレビュー要点コメントを残した。
- [ ] 人間指摘がある場合、指摘収集・文書修正・矛盾チェックを分離して実施した。
- [ ] 最終diff、PR URL、残課題を親エージェントが確認した。
