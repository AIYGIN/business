# AIYGIN pnpm audit loop

この repository は `AIYGIN/business` を横断管理面として使い、BFF/FE の pnpm audit 結果を Issue 化する。

## 週次 audit

GitHub Actions:

- `.github/workflows/weekly-pnpm-audit.yml`
- 毎週月曜 09:00 JST
- `AIYGIN/bff` と `AIYGIN/fe` を checkout
- `pnpm audit --json` を実行
- 脆弱性がある場合は `AIYGIN/business` に Issue を作成・更新

private repository を checkout する場合は repository secret `AIYGIN_AUDIT_TOKEN` が必要。

## Hermes loop

Hermes 側では `aiygin-vulnerability-loop` skill と cron job `AIYGIN pnpm audit issue watcher` が `pnpm-audit` Issue を捕捉する。

対象 Issue の label:

- `security`
- `pnpm-audit`
- `agent:todo`
- `repo:bff` または `repo:fe`
- `severity:*`

Hermes は対象 Issue を見つけたら、対象 repo の Codex に dependency 修正 PR 作成を指示する。

各対応が完了・停止・失敗したら、対象 repository root で `agent-memory write --target daily --content "..."` を実行し、作業要約を保存する。未完了 TODO がある場合は `agent-memory scratchpad add --text "..."` も実行する。
