# FE Issue 案作成 Codex プロンプト

あなたは `~/git/fe` の Codex PM エージェントです。

## 入力

- business 親 Issue: {{BUSINESS_ISSUE_URL}}
- BFF Issue: {{BFF_ISSUE_URL}}
- BFF mock PR: {{BFF_MOCK_PR_URL}}
- BFF OpenAPI / mock 要約: {{BFF_OPENAPI_SUMMARY}}
- FE 向け委譲入力: {{DELEGATION_INPUT}}

## 必ず読む

- `AGENTS.md`
- `src/AGENTS.md`
- `.codex/skills/plan-to-issue/SKILL.md`
- `.codex/skills/plan-to-issue/references/rules.md`
- `.codex/skills/plan-to-issue/assets/template.md`
- `.codex/workflows/sdd_flow.md`

## タスク

business 親 Issue と BFF mock PR の状況を見て、FE 開発 Issue 案を作成してください。

## 必須反映

- BFF OpenAPI から Orval で API client / mock を自動生成する前提。
- `src/apis/generated` の生成物は手動編集しない。
- 本番機能コードは `src/apis/generated` の API client / type を直接使う。
- `src/apis` 直下には本番用 API ラッパーや業務ロジックを追加しない。
- Story / test を先に作る SDD / TDD フロー。

## 禁止

- `gh issue create` を実行しない。
- コードを編集しない。
- PR を作らない。

## 出力

```json
{
  "phase": "fe-issue-draft",
  "repo": "AIYGIN/fe",
  "issue_title": "<FE Issue title>",
  "issue_body": "GitHub Issue body markdown",
  "needs_confirmation": true,
  "rationale": "FE Issue として十分だと判断した根拠"
}
```
