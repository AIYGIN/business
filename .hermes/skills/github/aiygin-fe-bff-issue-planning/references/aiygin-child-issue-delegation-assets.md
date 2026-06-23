# AIYGIN FE/BFF 子 Issue 委譲先 asset 調査メモ

この reference は、`aiygin-fe-bff-issue-planning` で business 親 Issue 作成後に FE/BFF 子 Issue を各 repo 側へ委譲するとき、委譲先 asset を見落とさないための調査メモである。

## 背景

TODOリストの Supabase DB 永続化 / BFF 疎通計画で、business 親 Issue 作成前の FE/BFF 調査に加えて、各 repo 内の子 Issue 作成 asset も確認したところ、repo ごとに委譲方法が異なった。

## FE: AIYGIN/fe

確認できた asset:

- `.codex/skills/plan-to-issue/SKILL.md`
- `.codex/skills/plan-to-issue/references/rules.md`
- `.codex/skills/plan-to-issue/assets/template.md`
- `.codex/skills/plan-to-issue/scripts/create_issue.sh`
- `.codex/agents/issue_responder.toml`
- `.codex/agents/pm.toml`

委譲方針:

- FE 子 Issue は repo 内の `plan-to-issue` skill と `scripts/create_issue.sh` に委譲する。
- `create_issue.sh` の想定は概ね `./create_issue.sh "タイトル" "本文"`。
- FE 子 Issue 本文では以下を明記すると後続実装へつながりやすい。
  - 親 business Issue URL
  - Orval 生成物を手動編集しないこと
  - BFF 契約変更時は OpenAPI 更新後に FE 側で Orval 再生成すること
  - Storybook/test は MSW 継続、実 BFF 疎通は mock 無効化・環境切替を別途扱うこと

## BFF: AIYGIN/bff

確認できた asset:

- `.github/ISSUE_TEMPLATE/api-interface.yml`
- `.codex/workflows/api_implementation_flow.md`
- `.codex/workflows/foundation_implementation_flow.md`
- `.codex/agents/implementation_planner.toml`
- `docs/layer-boundaries.md`

確認できなかった asset:

- FE の `create_issue.sh` に相当する、明確な repo-local Issue 作成 script は確認できなかった。

委譲方針:

- BFF 子 Issue は repo 内の GitHub Issue template / implementation workflow / implementation planner の観点に沿って作る。
- 専用作成 script が見つからない場合でも、repo 内 template/workflow に合わせた本文を作り、委譲先サブエージェント側で `gh issue create --repo AIYGIN/bff` を実行してよい。
- 親の `aiygin-fe-bff-issue-planning` skill 自体が直接 `AIYGIN/bff` に Issue 作成するのではなく、BFF repo の文脈を読んだ委譲先が作る。

## 親エージェントの検証

子 Issue 作成後、サブエージェントの自己申告だけで完了扱いにしない。

必ず親エージェントが以下を検証する。

```bash
gh issue view <FE_ISSUE_NUMBER> --repo AIYGIN/fe --json url,title,number,body --jq \
  '{number,title,url,hasParent:(.body|contains("<BUSINESS_ISSUE_URL>"))}'

gh issue view <BFF_ISSUE_NUMBER> --repo AIYGIN/bff --json url,title,number,body --jq \
  '{number,title,url,hasParent:(.body|contains("<BUSINESS_ISSUE_URL>"))}'
```

検証後、business 親 Issue に FE/BFF 子 Issue URL をコメントする。

## 調査フェーズへの反映

FE/BFF 調査サブエージェントへは、コード構成だけでなく「子 Issue 作成用の repo-local asset も確認する」ことを明示的に依頼するとよい。

調査結果には以下を含める。

- 子 Issue 作成用 skill / template / script / workflow の path
- 使い方
- 見つからなかった場合の fallback 方針
- その repo の Issue 本文に必ず入れるべき注意点
