---
name: github-pr-summarizer
description: GitHubの複数リポジトリからオープンPRを取得し、タイトル・作成者・説明文・Diffを日本語で簡潔に要約してSlackへ通知するワークフロー。
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [github, pull-request, slack, summary, review]
    related_skills: [github-pr-workflow, pr-summary]
---

# GitHub PR 要約通知

## 概要

このスキルは、指定された GitHub リポジトリ群の現在オープンなプルリクエスト（PR）を取得し、各 PR のタイトル、作成者、本文、変更ファイル、差分の要点を LLM で日本語要約し、接続済み Slack チャンネルへ通知するための手順です。

既定の対象リポジトリは次の2つです。

- https://github.com/AIYGIN/fe
- https://github.com/AIYGIN/bff

## 使用する場面

以下の依頼で使います。

- `AIYGIN/fe と AIYGIN/bff のPRを要約してSlackに送って`
- `オープンPRを一覧化して #pr-review に通知して`
- `PRレビュー用のサマリーを作って`
- 定期実行ジョブでPRレビュー対象をSlackへ流す

## 前提条件

- `gh` CLIがインストール済みで、対象リポジトリを読めるGitHubアカウントで認証済みであること。
- `jq` があると整形が楽。
- Hermesの `send_message` でSlack接続先が利用可能であること。
- Slackの特定チャンネルへ送る場合は、送信前に必ず `send_message(action='list')` で実際のターゲット名を確認すること。

## 手順

### 1. GitHub認証とツールを確認

```bash
command -v gh
command -v jq
gh auth status
```

`gh auth status` が失敗する場合は、`github-auth` スキルを参照して認証を先に直します。

### 2. Slack送信先を確認

Hermesのメッセージ送信ツールで接続先を列挙します。

```text
send_message(action='list')
```

指定チャンネル（例: `#pr-review`）が見つかる場合、その正確なターゲットを使います。見つからない場合はSlack通知は未完了としてユーザーへ明示し、作成した要約本文をそのまま提示します。

**cron / 自動配送ジョブでの例外:** ユーザーまたはジョブ設定が「final response を配送するので `send_message` を使わない」と明示している場合は、その指示を優先し、`send_message(action='list')` と送信をどちらも実行しません。PR要約本文を最終応答そのものに含めます。

**Hermes cron の Slack 投稿方式:** Slack へ定期投稿する cron は、次のどちらか一方に統一します。

- `deliver='slack:<target>'`: cron scheduler が最終応答を Slack へ配送する。prompt には「send_message は使わず、final response を Slack 投稿本文にする」と明記する。
- `deliver='local'` + `send_message(target='slack:<target>')`: agent が実行中に明示投稿する。message_id を確認したい場合はこちら。

このユーザーの PR 要約 cron では、特に指定がなければ `deliver='slack:all-aiynaragin'` を優先し、final response 配送方式にする。`deliver='local'` のままだと Slack には投稿されないため注意する。

### 3. PR一覧を取得

まず対象リポジトリがリネーム・転送されていないか確認し、GitHubが返す正規の `nameWithOwner` とURLを把握します。依頼名と正規名が異なる場合（例: `AIYGIN/todo` が `AIYGIN/fe` に解決される）は、最終報告で補足します。

```bash
for repo in AIYGIN/fe AIYGIN/bff; do
  gh repo view "$repo" --json nameWithOwner,url,description,isArchived,isPrivate
 done
```

既定対象:

```bash
for repo in AIYGIN/fe AIYGIN/bff; do
  echo "## $repo"
  gh pr list \
    --repo "$repo" \
    --state open \
    --limit 50 \
    --json number,title,author,headRefName,baseRefName,isDraft,updatedAt,url,additions,deletions,mergeStateStatus,reviewDecision
  echo
done
```

または、既存の `pr-summary` スキルが利用可能なら、次のスクリプトで説明文・コミット・変更ファイルもまとめて取得できます。

```bash
bash /Users/ynaragin/git/work/.hermes/skills/github/pr-summary/scripts/pr-summary.sh all open
```

ただし、この絶対パスは環境依存です。存在しない場合は上の `gh pr list` と次項の `gh pr view` を使います。

### 4. 各PRの詳細を取得

PR番号ごとに本文、コミット、変更ファイルを取得します。

```bash
repo=AIYGIN/fe
pr=9
gh pr view "$pr" \
  --repo "$repo" \
  --json number,title,body,author,commits,files,reviews,comments,url,additions,deletions,mergeStateStatus,reviewDecision
```

Diffのファイル一覧とパッチ要点も取得します。

```bash
gh api "repos/$repo/pulls/$pr/files" --paginate \
  --jq '.[] | [.filename, .status, .additions, .deletions, .changes] | @tsv'

gh pr diff "$pr" --repo "$repo" --color never | head -n 400
```

大きいPRではDiff全文をLLMへ渡しすぎないよう、変更ファイル一覧、追加削除行数、本文、コミット見出し、Diff冒頭または重要ファイルのパッチだけを使って要約します。

### 5. LLMで日本語要約する

各PRにつき、以下を必ず含めます。

- PR番号とタイトル
- URL
- 作成者
- 変更量（additions/deletions）
- 簡潔な要約（2〜4文）
- 必要ならレビュー観点または注意点

要約例:

```text
1) #9 auto: Todo APIをOrval生成クライアントへ移行
- URL: https://github.com/AIYGIN/fe/pull/9
- 作成者: AIYGIN
- 変更量: +750 / -18、merge state: CLEAN
- 要約: Todo画面のAPI呼び出しを手書きfetchからOrval生成クライアントへ移行するPR。BFF OpenAPI定義由来のTodo DTO・operation・mockを生成し、画面向けラッパーとエラー変換、API契約テストを追加しています。
```

PRがないリポジトリは `オープンPRなし` と明記します。

### 6. Slackへ通知

接続先確認済みのターゲットへ送ります。

```text
send_message(
  action='send',
  target='slack:#pr-review',
  message='<PR要約本文>'
)
```

`Could not resolve` や `No messaging platforms connected` が返った場合は、Slack通知は失敗です。要約の生成自体は完了として、Slack接続またはチャンネル解決が必要であることをユーザーへ報告します。

## 出力形式

Slack本文は短く読みやすくします。

```text
【PR要約】
対象: AIYGIN/fe, AIYGIN/bff

AIYGIN/fe: オープンPR N件

1) #<number> <title>
- URL: <url>
- 作成者: <author>
- 変更量: +<additions> / -<deletions>、merge state: <state>
- 要約: <2〜4文>

AIYGIN/bff: オープンPRなし
```

## よくある失敗

1. Slackターゲットを確認せずに送ると失敗しやすい。必ず `send_message(action='list')` を先に実行する。
2. Hermes cron で Slack へ投稿したいのに `deliver: local` のままにすると、ジョブは成功しても Slack には投稿されない。cron job の配送先を `slack:<target>` に設定するか、ジョブ内で `send_message` を明示的に使う。手動実行後に Slack で見えない場合は、まず `cronjob(action='list')` で `deliver` / `last_delivery_error` / `last_status` を確認する。
3. AIYGIN の FE repository は `AIYGIN/fe` が正であり、古い cron prompt やローカル remote に `AIYGIN/todo` が残っていたら修正する。PR 要約対象を `AIYGIN/todo` として扱わない。
4. `gh pr diff --stat` は環境によって使えない。代わりに `gh api repos/<owner>/<repo>/pulls/<pr>/files` を使う。
5. Diff全文をそのままLLMへ渡すと長すぎる。ファイル一覧、追加削除行数、PR本文、コミット、重要Diffに絞る。
6. PRなしのリポジトリも省略せず、`オープンPRなし` と明記する。
7. Slack未接続の場合、通知成功と報告してはいけない。送信ツールの実結果を根拠に報告する。

## 完了確認チェックリスト

- [ ] `gh auth status` が成功した
- [ ] 対象リポジトリが `AIYGIN/fe` と `AIYGIN/bff` であることを確認した（`AIYGIN/todo` が残っていない）
- [ ] 対象リポジトリごとのオープン PR 件数を取得した
- [ ] 各PRのタイトル、作成者、本文、変更ファイル、Diff要点を確認した
- [ ] LLM要約にURL、作成者、変更量、要約が含まれている
- [ ] Slack送信ツールまたは cron delivery の返却結果を確認した
- [ ] cron 配信の場合は `deliver` が Slack target であり、`last_delivery_error` がないことを確認した
- [ ] Slack送信に失敗した場合は、失敗理由と要約本文をユーザーへ提示した
