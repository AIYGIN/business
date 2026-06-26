# AIYGIN FE/BFF 子 Issue 作成委譲 asset 調査メモ

このメモは `aiygin-fe-bff-issue-planning` で FE/BFF 子 Issue 作成を委譲するとき、各 repo-local asset の有無と扱いを確認するための補助資料である。

## 原則

- この skill から直接作成してよい Issue は `AIYGIN/business` の親 Issue だけ。
- FE/BFF 子 Issue は各 repo 内の template / script / skill / workflow に委譲する。
- repo-local asset が見つからない場合、代替としてこの skill から直接 `gh issue create --repo AIYGIN/fe` / `AIYGIN/bff` を実行しない。
- 未作成理由を business 親 Issue にコメントし、agent-memory scratchpad に未完了 TODO として残す。

## 2026-06 高配当分析画面 PoC で確認した状況

### AIYGIN/bff

確認済み asset:

- `/Users/ynaragin/git/bff/.github/ISSUE_TEMPLATE/api-interface.yml`

用途:

- PM が BFF API の公開 IF を決めるための Issue template。
- Controller mock PR の完了条件は Swagger/OpenAPI で契約が表現されること。
- 高配当分析画面 PoC では、この template に沿って以下の API IF Issue を作成できた。
  - `API IF: GET /api/dividend-analysis`
  - `API IF: GET /api/dividend-analysis/{symbol}`

使い方の要点:

- `api-if` と `pm` label が repo に存在することを確認する。
- 本文には必ず親 `AIYGIN/business` Issue URL を入れる。
- BFF の API IF Issue は endpoint 単位で分けると扱いやすい。
- 作成後は `gh issue view --repo AIYGIN/bff <number> --json url,title,body` で、親 Issue URL が本文に含まれることを検証する。

### AIYGIN/fe

確認済み asset:

- `/Users/ynaragin/git/fe/.codex/skills/plan-to-issue/SKILL.md`
- `/Users/ynaragin/git/fe/.codex/skills/plan-to-issue/references/rules.md`
- `/Users/ynaragin/git/fe/.codex/skills/plan-to-issue/assets/template.md`
- `/Users/ynaragin/git/fe/.codex/skills/plan-to-issue/scripts/create_issue.sh`
- `/Users/ynaragin/git/fe/.codex/agents/issue_responder.toml`

用途:

- `plan-to-issue` は、開発計画をコンポーネント設計・Store設計を含む GitHub Issue 形式へ変換し、`scripts/create_issue.sh` で FE repo に Issue を作成する repo-local skill。
- `create_issue.sh` は current working directory の GitHub repo に対して `gh issue create` を実行するため、必ず `/Users/ynaragin/git/fe` を workdir にして実行する。

使い方の要点:

1. 必ず以下を読む。
   - `SKILL.md`
   - `references/rules.md`
   - `assets/template.md`
   - `scripts/create_issue.sh`
2. `rules.md` の重要ルールを守る。
   - summary は要約可。
   - tasks は要約禁止・完全展開必須。
   - UI を含む場合は `コンポーネント設計` を必須にする。
   - API状態または共有状態を扱う場合は `Store設計` を必須にする。
   - 受け入れ条件にも `コンポーネント設計準拠` / `Store設計準拠` を入れる。
3. `assets/template.md` の見出し構成で本文を作る。
4. `/tmp/...md` などに本文を作成し、以下のように FE repo root で script を実行する。

```bash
cd /Users/ynaragin/git/fe
body=$(cat /tmp/<fe-issue-body>.md)
bash .codex/skills/plan-to-issue/scripts/create_issue.sh "feat: <タイトル>" "$body"
```

5. 作成後は `gh issue view --repo AIYGIN/fe <number> --json url,title,body` で、親 business Issue URL と必要な参照 Issue URL が本文に含まれることを検証する。

高配当分析画面 PoC での実績:

- 親: `https://github.com/AIYGIN/business/issues/23`
- FE: `https://github.com/AIYGIN/fe/issues/32`
- BFF:
  - `https://github.com/AIYGIN/bff/issues/25`
  - `https://github.com/AIYGIN/bff/issues/26`

注意:

- FE repo では `.github/ISSUE_TEMPLATE` ではなく `.codex/skills/plan-to-issue/` 配下を優先して探す。
- `.github/ISSUE_TEMPLATE` だけを探して「asset 未検出」と判断しない。
- `create_issue.sh` は `--repo` を取らないため、workdir を間違えると別 repo に Issue を作る恐れがある。必ず `/Users/ynaragin/git/fe` で実行する。

## business 親 Issue へのコメント例

```markdown
FE/BFF 子 Issue 作成結果です。

- BFF:
  - 一覧 API IF: <BFF issue URL>
  - 詳細 API IF: <BFF issue URL>
- FE:
  - 未作成
  - 理由: ローカルの `AIYGIN/fe` には子 Issue 作成専用の `.github/ISSUE_TEMPLATE` / `SKILL.md` / issue create script が見つかりませんでした。
  - `aiygin-fe-bff-issue-planning` のルール上、この workflow から `AIYGIN/fe` に直接 `gh issue create` することは禁止のため、FE 子 Issue は repo-local の作成手段が確認できるまで保留します。
```

## 今後の確認観点

- FE repo に `.github/ISSUE_TEMPLATE` や issue 作成 script が追加された場合、この reference を更新する。
- BFF の `api-interface.yml` が変更された場合、必須項目・label・作成手順を更新する。
- 子 Issue 作成を subagent に委譲した場合でも、親エージェントが `gh issue view` で URL/title/body/親 Issue URL 含有を検証してから成功報告する。
