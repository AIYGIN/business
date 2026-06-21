---
name: aiygin-product-orchestrator
description: AIYGIN の business / BFF / FE を Hermes Agent が指示系統としてつなぎ、aiygin-fe-bff-issue-planning の親 Issue から BFF Issue、BFF mock PR、FE Issue、FE 実装 PR までを Codex に段階委譲する日本語ワークフロー。
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [macos, linux]
metadata:
  hermes:
    tags: [aiygin, orchestration, bff, fe, codex, github, issues, pull-requests]
    related_skills: [aiygin-fe-bff-issue-planning, aiygin-vulnerability-loop, ai-coding-agents, github-workflows, user-communication-standards]
---

# AIYGIN Product Orchestrator

## 目的

この skill は、Hermes Agent を「プロダクト間の指示系統」として使い、`AIYGIN/business` の親 Issue を正本にしながら、`~/git/bff` と `~/git/fe` へ Codex 経由で順番に作業を渡すための運用手順である。

狙いは次の流れを壊さずに自動化すること。

1. `aiygin-fe-bff-issue-planning` で business 親 Issue を作る、または既存親 Issue を特定する。
2. BFF リポジトリで API IF Issue 案を作る。
3. Hermes がユーザー確認を取り、承認後に BFF Issue を作成する。
4. BFF Issue とコメントをもとに、Codex が Controller mock / OpenAPI 契約の draft PR を作る。
5. BFF mock PR / OpenAPI 契約の状況を Hermes が FE へ渡せる形に要約する。
6. FE リポジトリで、business 親 Issue と BFF mock 状況を見て FE Issue 案を作る。
7. Hermes がユーザー確認を取り、承認後に FE Issue を作成する。
8. FE Issue をもとに、Codex が SDD / TDD で FE 開発を進め、draft PR を作る。

## 重要な責務分離

- Hermes Agent: 横断の正本管理、順番制御、ユーザー確認、Codex への指示、成果物 URL の回収、business Issue への結果反映を担当する。
- `~/git/bff` の Codex: BFF リポジトリ内の `.codex/agents/*.toml` と `.codex/workflows/*.md` に従い、BFF Issue 案、Issue 作成、Controller mock PR 作成を担当する。
- `~/git/fe` の Codex: FE リポジトリ内の `.codex/skills/plan-to-issue`、`.codex/workflows/sdd_flow.md`、`.codex/agents/*.toml` に従い、FE Issue 案、Issue 作成、FE 開発 PR 作成を担当する。
- `aiygin-fe-bff-issue-planning` skill: `AIYGIN/business` の親 Issue 作成だけを担当する。`AIYGIN/fe` / `AIYGIN/bff` の子 Issue を直接作ってはいけない。

## 前提リポジトリ

デフォルトのローカルパスは以下。

```text
BFF_REPO=/Users/ynaragin/git/bff
FE_REPO=/Users/ynaragin/git/fe
```

ただし、別パスをユーザーが指定した場合はその指定を優先する。Hermes のプロンプトや説明では、必要に応じて `BFF_REPO` / `FE_REPO` と呼び、別環境に固定パスを押し付けない。

GitHub repository 名は `BFF_REPO=AIYGIN/bff`、`FE_REPO=AIYGIN/fe` を正とする。`~/git/fe` の `git remote -v` が別 repository を指している場合は、canonical repo ではなくローカル remote 設定の誤りとして扱い、Issue / PR 作成前に `AIYGIN/fe` へ向け直す。

## 必須事前確認

実行前に Hermes が確認する。

```bash
rtk git status --short
rtk git remote -v
rtk git branch --show-current
command -v headroom
command -v codex
command -v gh
command -v agent-memory
gh auth status
```

BFF では以下が存在することを確認する。

- `AGENTS.md`
- `docs/ai-api-harness.md`
- `.codex/agents/pm.toml`
- `.codex/agents/mock_issue_responder.toml`
- `.codex/workflows/api_controller_mock_flow.md`

FE では以下が存在することを確認する。

- `AGENTS.md`
- `src/AGENTS.md`
- `.codex/skills/plan-to-issue/SKILL.md`
- `.codex/skills/plan-to-issue/scripts/create_issue.sh`
- `.codex/workflows/sdd_flow.md`
- `.codex/agents/issue_responder.toml`

## フェーズ 0: business 親 Issue

まず `aiygin-fe-bff-issue-planning` を使う。

- business 親 Issue を新規作成する、または既存 Issue を親として特定する。
- 親 Issue には FE / BFF へ渡す `委譲用入力` を含める。
- 作成後に `BUSINESS_ISSUE_URL` を控える。

この skill から `AIYGIN/fe` / `AIYGIN/bff` へ直接 Issue を作ってはいけない。

## フェーズ 1: BFF Issue 案作成

Hermes は `~/git/bff` で Codex に `pm` 役割を明示して、Issue 作成ではなく「Issue 案」だけを出させる。

推奨プロンプトは `references/bff-issue-draft-prompt.md`、または `scripts/render_prompt.py --phase bff-issue-draft` で生成する。

Codex への要点:

- `AIYGIN/business` 親 Issue と委譲用入力を読む。
- BFF の `docs/ai-api-harness.md` と `.codex/agents/pm.toml` に従う。
- API IF Issue の `issue_title` と `issue_body` を JSON で出す。
- この段階では `gh issue create`、ブランチ作成、コード編集、PR 作成をしない。

Hermes は Codex 出力を確認し、ユーザーに BFF Issue 作成可否を確認する。

## フェーズ 2: BFF Issue 作成

ユーザーが承認したら、Hermes は `~/git/bff` の Codex に Issue 作成を指示する。

Codex への要点:

- 承認済みの `issue_title` / `issue_body` だけを使う。
- `gh issue create` で `AIYGIN/bff` に Issue を作る。
- 作成された URL を JSON の `bff_issue_url` で返す。
- まだコード編集や PR 作成はしない。

Hermes は `gh issue view` 等で URL を検証し、必要なら business Issue に BFF Issue URL をコメントする。

## フェーズ 3: BFF Controller mock PR 作成

BFF Issue 作成後、ユーザーが「mock PR へ進めてよい」と確認したら、Hermes は `~/git/bff` の Codex に `mock_issue_responder` として作業を渡す。

Codex への要点:

- 対象 BFF Issue と最新コメントを読む。
- `.codex/workflows/api_controller_mock_flow.md` に従う。
- Controller mock PR の範囲だけを実装する。
- Service / Resource / DB / Provider 実装はしない。
- draft PR を作成し、Issue に PR URL と実行ログを残す。
- `pnpm lint`、`pnpm typecheck`、`pnpm test --runInBand`、`pnpm build` を可能な範囲で実行する。
- 出力 JSON に `bff_mock_pr_url`、`branch`、`openapi_summary`、`commands`、`files_changed` を含める。

Hermes は PR URL を `gh pr view` で検証し、OpenAPI / mock の状況を FE に渡せるよう要約する。

## フェーズ 4: FE Issue 案作成

BFF mock PR が存在する、または FE が依存できる OpenAPI 契約情報が得られたら、Hermes は `~/git/fe` の Codex に FE Issue 案を作らせる。

入力には必ず以下を含める。

- `BUSINESS_ISSUE_URL`
- `BFF_ISSUE_URL`
- `BFF_MOCK_PR_URL`
- BFF mock PR の OpenAPI / mock 要約
- `aiygin-fe-bff-issue-planning` の FE 向け委譲用入力

Codex への要点:

- FE の `.codex/skills/plan-to-issue` を使う。
- `src/apis/generated` の Orval 生成物は手動編集しない前提を書く。
- BFF API 契約変更時は BFF OpenAPI 更新後に FE で Orval 再生成する前提を書く。
- Issue 案だけを出し、まだ `gh issue create`、コード編集、PR 作成をしない。

Hermes は Codex 出力を確認し、ユーザーに FE Issue 作成可否を確認する。

## フェーズ 5: FE Issue 作成

ユーザーが承認したら、Hermes は `~/git/fe` の Codex に Issue 作成を指示する。

Codex への要点:

- 承認済みの FE Issue タイトル・本文だけを使う。
- `.codex/skills/plan-to-issue/scripts/create_issue.sh` を優先して Issue を作る。
- 作成された URL を JSON の `fe_issue_url` で返す。
- まだコード編集や PR 作成はしない。

Hermes は FE Issue URL を検証し、business Issue に FE/BFF 子 Issue 作成結果をコメントする。

## フェーズ 6: FE 開発 PR 作成

FE Issue 作成後、ユーザーが「FE 開発へ進めてよい」と確認したら、Hermes は `~/git/fe` の Codex に `issue_responder` として作業を渡す。

Codex への要点:

- 対象 FE Issue、business Issue、BFF Issue、BFF mock PR を読む。
- `.codex/workflows/sdd_flow.md`、`AGENTS.md`、`src/AGENTS.md` に従う。
- Story / test を先に作り、レビュー可能な状態を経由する。
- Orval 生成物を手動編集しない。
- API 利用では `src/apis/generated` の API client / type / mock を直接利用する。
- `src/apis` 直下に本番用 API ラッパーや業務ロジックを置かない。
- draft PR を作成し、Issue に PR URL と実行ログを残す。
- `pnpm check` と該当 test を可能な範囲で実行する。

Hermes は PR URL、diff、実行結果を検証してから完了報告する。

## Codex 実行コマンド例

Hermes から Codex を起動する場合は、Codex CLI の性質上 `pty=true` で実行する。加えて、`codex` を直接呼ばず、必ず `headroom wrap codex ...` で起動する。

```text
terminal(command="headroom wrap codex exec --full-auto '<prompt>'", workdir=BFF_REPO, pty=true, timeout=600)
terminal(command="headroom wrap codex exec --full-auto '<prompt>'", workdir=FE_REPO, pty=true, timeout=600)
```

禁止:

```text
terminal(command="codex exec --full-auto '<prompt>'", ...)
```

`headroom` が見つからない場合は、Codex を直接起動して続行せず、ユーザーに未導入であることを報告する。ユーザーが明示的に「今回は headroom なしでよい」と指示した場合だけ例外にできるが、その例外理由も `agent-memory` に残す。

Codex 起動時は、起動前・完了時・失敗時を対象 repo の `agent-memory` に必ず記録する。

```bash
rtk agent-memory write --content "aiygin codex: <phase> 開始。repo=<repo> command=headroom wrap codex exec --full-auto / input=<要約>"
rtk agent-memory write --content "aiygin codex: <phase> 完了。repo=<repo> result=<要約> / urls=<Issue or PR URL> / next=<次作業>"
rtk agent-memory write --content "aiygin codex: <phase> 失敗。repo=<repo> exit=<code> / reason=<理由> / next=<再開条件>"
```

未完了TODOや人間確認待ちは `agent-memory scratchpad add` に残す。

Hermes gateway / service コンテキストで Codex sandbox が壊れる場合だけ、`--sandbox danger-full-access` を検討する。その場合も `headroom wrap codex exec --sandbox danger-full-access "<task>"` の形を維持し、作業ディレクトリを限定し、事前の git status、事後の git diff / test / PR URL 検証を行う。

長いプロンプトは `scripts/render_prompt.py` で生成する。

```bash
python ~/.hermes/skills/workflow/aiygin-product-orchestrator/scripts/render_prompt.py \
  --phase bff-issue-draft \
  --business-url "$BUSINESS_ISSUE_URL" \
  --input-file /tmp/aiygin-delegation.md
```

## ユーザー確認ゲート

以下は必ず Hermes がユーザー確認を取る。

1. BFF Issue 作成前。
2. BFF mock PR 作成前。
3. FE Issue 作成前。
4. FE 開発 PR 作成前。

確認時は、タイトル、本文要約、対象 repo、実行予定の Codex phase、作成/変更される GitHub artifact を示す。

## ユーザー向け報告スタイル

AIYGIN の横断 orchestration は、ユーザーが判断するための中間報告が多い。報告・確認・完了通知では `user-communication-standards` も併用し、次を守る。

- 原則として「結論 → 根拠 → 具体的なアクション → 代替案 → リスク・注意点」の順で書く。
- BFF/FE/business の Issue/PR URL、検証コマンド、未確認事項を根拠として明記する。
- 未作成、確認待ち、失敗、未検証を成功扱いにしない。
- ユーザー案に工程上の矛盾や抜けがあれば、忖度せず指摘する。
- 最新の GitHub 状態や repo 状態は、記憶ではなく `gh` / `git` / file inspection で確認してから述べる。
- 件数、差分数、文字数などを含む場合は暗算せず Python 等で検証する。

## agent-memory 完了記録

各 phase が完了、停止、失敗のいずれで終わっても、作業した repository の root で `agent-memory` に要約を保存する。詳細は `references/agent-memory-completion.md` を参照する。

最低限、以下を `daily` に残す。

- phase 名
- business Issue URL
- BFF / FE の Issue URL または PR URL
- 実行した command と結果要約
- 停止理由または remaining work

未完了 TODO は `agent-memory scratchpad add` に追加する。長期的に再利用できる設計判断だけ `long_term` に保存する。

## business Issue への反映

BFF Issue / BFF mock PR / FE Issue / FE PR の URL が得られたら、business Issue にコメントする。

```text
AIYGIN FE/BFF オーケストレーション進捗

- BFF Issue: <url or 未作成理由>
- BFF mock PR: <url or 未作成理由>
- FE Issue: <url or 未作成理由>
- FE PR: <url or 未作成理由>
```

未作成・失敗・ユーザー確認待ちは成功扱いにしない。

## 完了確認チェックリスト

- [ ] business 親 Issue URL がある。
- [ ] BFF Issue URL を検証した、または未作成理由を説明できる。
- [ ] BFF mock PR URL を検証した、または未作成理由を説明できる。
- [ ] FE Issue URL を検証した、または未作成理由を説明できる。
- [ ] FE PR URL を検証した、または未作成理由を説明できる。
- [ ] BFF / FE の Issue 作成と PR 作成は、それぞれの repo の Codex / skill / workflow に委譲している。
- [ ] Orval 生成物を手動編集する前提にしていない。
- [ ] draft PR の実行コマンド、失敗、未実施項目を隠さず報告している。
- [ ] Hermes から Codex を起動した場合、`headroom wrap codex ...` で実行し、直接 `codex ...` を呼んでいない。
- [ ] Codex 起動・完了・失敗を対象 repo の `agent-memory` daily log に記録した。
