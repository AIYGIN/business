# agent-memory 完了記録ルール

AIYGIN product orchestration では、Codex に委譲した各 phase が完了したら、作業した repository の `agent-memory` に要約を保存する。

## 対象 phase

- BFF Issue 作成
- BFF Controller mock PR 作成
- FE Issue 作成
- FE 開発 PR 作成
- 途中停止 / blocker 発生

## 保存先

対象 repository root で実行する。

- BFF 作業: `/Users/ynaragin/git/bff`
- FE 作業: `/Users/ynaragin/git/fe`
- business 横断判断: `/Users/ynaragin/git/business` が存在する場合は business 側にも daily 要約を残してよい

## daily 記録

```bash
agent-memory write --target daily --content "<YYYY-MM-DD> <phase>: <何をしたか>; business=<business issue URL>; bff=<BFF issue/PR URL or none>; fe=<FE issue/PR URL or none>; validation=<実行コマンドと結果要約>; remaining=<未完了>"
```

## scratchpad

未完了 TODO がある場合だけ追加する。

```bash
agent-memory scratchpad add --text "<対象repo> <issue/pr URL>: <次にやること>"
```

## long_term

設計判断や運用方針として今後も使うものだけ保存する。

```bash
agent-memory write --target long_term --content "<安定した設計判断>"
```

## 禁止

- 秘密情報、token、個人情報を保存しない。
- 大量ログ、raw JSON、差分全文を保存しない。
- 一週間程度で陳腐化する一時メモを long_term に入れない。
