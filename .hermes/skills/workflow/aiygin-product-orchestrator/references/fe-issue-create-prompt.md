# FE Issue 作成 Codex プロンプト

あなたは `~/git/fe` の Codex エージェントです。

## 入力

- 承認済み Issue title: {{ISSUE_TITLE}}
- 承認済み Issue body: {{ISSUE_BODY}}

## タスク

承認済み title / body を変更せず、FE リポジトリの仕組みを使って GitHub Issue を作成してください。

## 手順

1. `gh auth status` と repo remote を確認する。
2. `.codex/skills/plan-to-issue/scripts/create_issue.sh` を優先して使う。
3. 作成された URL を `gh issue view` で確認する。

## 禁止

- コードを編集しない。
- PR を作らない。
- 承認済み本文に勝手な仕様追加をしない。

## 出力

```json
{
  "phase": "fe-issue-create",
  "repo": "AIYGIN/fe",
  "fe_issue_url": "https://github.com/AIYGIN/fe/issues/<number>",
  "commands": ["実行したコマンド要約"],
  "rationale": "作成 URL の検証結果"
}
```
