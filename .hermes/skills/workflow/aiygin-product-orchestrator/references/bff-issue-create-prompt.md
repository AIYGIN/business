# BFF Issue 作成 Codex プロンプト

あなたは `~/git/bff` の Codex エージェントです。

## 入力

- 承認済み Issue title: {{ISSUE_TITLE}}
- 承認済み Issue body: {{ISSUE_BODY}}

## タスク

承認済み title / body を変更せず、`AIYGIN/bff` に GitHub Issue を作成してください。

## 手順

1. `gh auth status` と `gh repo view AIYGIN/bff` を確認する。
2. body は一時ファイルに書く。
3. `gh issue create --repo AIYGIN/bff --title "..." --body-file <tmp>` を実行する。
4. 作成された URL を `gh issue view` で確認する。

## 禁止

- コードを編集しない。
- PR を作らない。
- 承認済み本文に勝手な仕様追加をしない。

## agent-memory 完了記録

作業が完了、停止、失敗のいずれで終わっても、対象 repository root で `agent-memory` に要約を保存してください。

```bash
agent-memory write --target daily --content "<YYYY-MM-DD> <phase>: <何をしたか>; business=<business issue URL>; artifact=<Issue/PR URL or none>; validation=<実行コマンドと結果要約>; remaining=<未完了があれば要約>"
```

未完了 TODO がある場合のみ:

```bash
agent-memory scratchpad add --text "<Issue/PR URL>: <次にやること>"
```

秘密情報、token、個人情報、大量ログは保存しないでください。

## 出力

```json
{
  "phase": "bff-issue-create",
  "repo": "AIYGIN/bff",
  "bff_issue_url": "https://github.com/AIYGIN/bff/issues/<number>",
  "commands": ["実行したコマンド要約"],
  "rationale": "作成 URL の検証結果"
}
```
