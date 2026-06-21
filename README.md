# business

このリポジトリでは、事業・企画・提案に関するドキュメントを `planning/` 配下で管理します。

## 提案書作成・レビューPR化ワークフロー

Hermes Agent で提案書を作成・レビュー・PR化する場合は、以下のワークフローを使います。

### 目的

曖昧なアイデア、口頭依頼、または指定された Markdown 文書から「やりたいこと」を理解し、以下を一連の流れで実施します。

1. ヒアリングまたは Markdown 文書の読み取り
2. 事前調査
3. ユーザー確認
4. 提案書ドラフト作成
5. `planning/` 配下への commit / push / PR 作成
6. システム観点レビュー報告書の作成
7. 同じ PR ブランチへの追加 commit / push
8. PR 上の人間指摘の反映
9. 矛盾チェック後の再 commit / push

このワークフローでは、提案書作成を急がず、事前調査とユーザー確認を必須ゲートとして扱います。

## 使用する Hermes Skill

### 司令塔

| Skill | 役割 |
|---|---|
| `proposal-planning-workflow` | 提案書作成、レビュー、PR化、人間指摘反映までの全体ワークフローを統括する |

### 部品化された再利用 Skill

| Skill | 役割 |
|---|---|
| `proposal-preflight-research` | 提案書作成前に、コスト・リスク・実現可能性・既存サービス/代用手段を調査する |
| `user-confirmation-gate` | 次工程へ進む前に、調査結果・選択肢・リスクを提示してユーザー確認を取る |
| `pr-human-feedback-loop` | PR 上の人間コメントを収集・分類し、修正・矛盾チェック・commit/push まで管理する |

### 提案書作成・レビュー Skill

| Skill | 役割 |
|---|---|
| `proposal-review-drafter` | エレベーターピッチ先行の提案書ドラフトを作成する |
| `proposal-system-reviewer` | 提案書に対して、コスト・BE構成・セキュリティ・障害点・キャッシュなどのシステム観点レビューを行う |

## Workflow Phase

### Phase 0: 入力理解・ヒアリング

ユーザーの依頼から、以下を抽出します。

- 提案テーマ
- 読み手・決裁者
- 期待する意思決定
  - 例: 承認、予算化、PoC開始、採用、廃止
- 背景・課題
- 期限・制約
- 既知の競合案・代替案

曖昧な依頼の場合は、回答・作業開始前に最大3つまで確認質問をします。

確認質問例:

1. この提案の読み手・決裁者は誰ですか。
2. 最終的に承認してほしい判断は何ですか。
3. 既に前提として使いたい Markdown 文書、既存 Issue、参考 URL はありますか。

Markdown 文書が指定された場合は、先にその内容を読み、目的・対象者・意思決定・制約・未確認事項を抽出します。

### Phase 1: 事前調査サブエージェント

使用 Skill:

- `proposal-preflight-research`

提案書作成前に、別サブエージェントで以下を調査します。

| 観点 | 確認内容 |
|---|---|
| コスト | 初期実装コスト、運用コスト、外部サービス/API利用料、保守・監視・人手対応コスト |
| リスク | 技術、セキュリティ/プライバシー、法務/規約/ライセンス、運用、UX |
| 実現可能性 | v1範囲、PoC範囲、前提技術・API・データ入手性、スケジュール不確実性 |
| 既存サービス・代用手段 | 類似SaaS、OSS、外部API、手動運用、既存運用改善、内製しない選択肢 |

サブエージェント結果はそのまま採用せず、親エージェントが以下に整理します。

- 事実
- 仮定/推論
- 要確認
- 推奨方針
- ユーザーに確認すべき判断事項

### Phase 2: ユーザー確認ゲート

使用 Skill:

- `user-confirmation-gate`

Phase 1 の調査結果を提示し、ユーザー確認が取れるまで提案書作成・PR化へ進みません。

提示する内容:

- 理解したやりたいこと
- 事実、仮定/推論、要確認
- コスト見立て
- 主要リスク
- 実現可能性
- 既存サービス/代用手段
- 推奨方針
- 次に作る成果物
- ユーザーに確認したいこと（最大3問）

確認文例:

```text
この方針で提案書ドラフト作成に進めてよいですか。
変更したい前提、除外したい範囲、強調したい観点があれば教えてください。
```

### Phase 3: 提案書ドラフト作成とPR化

使用 Skill:

- `proposal-review-drafter`
- `github-workflows`

ユーザー確認後、提案書ドラフトを作成します。

提案書には以下を含めます。

- エレベーターピッチ
- 人間レビュー用サマリー
- 提案の骨子
- SCQA
- 実行計画
- 数字・根拠の確認リスト
- 決裁者からの想定質問
- 弱点と改善案
- 人間レビュー欄
- AI作業メモ

配置先:

```text
planning/<YYYYMMDD>-<short-topic>-proposal.md
```

GitHub 作業例:

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

### Phase 4: システム観点レビュー報告書作成

使用 Skill:

- `proposal-system-reviewer`

Phase 3 の提案書に対して、別 Markdown としてレビュー報告書を作成します。

配置先:

```text
planning/<YYYYMMDD>-<short-topic>-system-review.md
```

レビュー報告書に含める内容:

- 結論
- 前提整理
  - 事実
  - 仮定
  - 要確認
- コスト観点
- 実現可能性
- システム構成案
- セキュリティリスク
- 障害点と対策
- キャッシュ/データ保持方針
- 既存サービス・代用手段との比較
- 提案書本文に反映すべき修正提案
- 人間レビューで決めるべき事項

GitHub 作業例:

```bash
rtk git -C /Users/ynaragin/git/business status --short --branch
rtk git -C /Users/ynaragin/git/business add planning/<system-review-file>.md planning/<proposal-file>.md
rtk git -C /Users/ynaragin/git/business commit -m "docs: add <topic> system review"
rtk git -C /Users/ynaragin/git/business push
```

必要に応じて、PR にレビュー要点コメントを残します。

```bash
gh -R AIYGIN/business pr comment <PR番号> --body-file /tmp/<topic>-system-review-comment.md
```

### Phase 5: 人間指摘の反映ループ

使用 Skill:

- `pr-human-feedback-loop`

PR に人間から指摘があった場合、以下をサブエージェント分離で実施します。

1. 指摘収集サブエージェント
   - PRコメント/レビューコメントを取得する
   - 指摘を重複排除する
   - 指摘を分類する
2. 修正サブエージェント
   - `planning/` 内の提案書・レビュー報告書を修正する
   - 未確認情報を断定しない
   - スコープ変更や判断が必要なものは要ユーザー確認に回す
3. 矛盾チェックサブエージェント
   - 提案書とレビュー報告書を読み比べる
   - 目的、実行計画、コスト、リスク、実現可能性、代替手段、未確認事項の扱いに矛盾がないか確認する

親エージェントは、サブエージェントの自己申告だけで完了扱いにせず、最終 diff と対象ファイルを確認します。

GitHub 作業例:

```bash
rtk git -C /Users/ynaragin/git/business diff -- planning/
rtk git -C /Users/ynaragin/git/business add planning/<files>
rtk git -C /Users/ynaragin/git/business commit -m "docs: address review feedback for <topic>"
rtk git -C /Users/ynaragin/git/business push
```

## サブエージェント分離方針

| 担当 | 役割 |
|---|---|
| 親エージェント | ユーザー確認、作業範囲決定、サブエージェント指示、成果物確認、git/gh実行確認、ユーザー報告 |
| 調査サブエージェント | コスト、リスク、実現可能性、代替手段の調査 |
| ドラフト作成サブエージェント | `proposal-review-drafter` に従った提案書初稿作成 |
| システムレビューサブエージェント | `proposal-system-reviewer` に従ったレビュー報告書作成 |
| 指摘収集サブエージェント | PRコメント/レビューコメントの分類 |
| 文書修正サブエージェント | 指摘に基づく Markdown 修正 |
| 矛盾チェックサブエージェント | 修正後文書の整合性確認 |

## 重要ルール

- ユーザー確認前に提案書作成・PR化へ進まない。
- サブエージェントの調査結果を検証せずに断定しない。
- 既存サービスや代用手段の調査を省略しない。
- `proposal-system-reviewer` の結果を、提案書本文と矛盾したまま別紙にしない。
- PRコメントだけして、レビュー報告書ファイルの commit を忘れない。
- 人間指摘を反映した後は、必ず矛盾チェックを行う。
- AIYGIN/business 以外の remote や未確認の dirty tree で作業しない。
- `rtk` を使える環境では、git 系コマンドに `rtk` を付ける。

## 完了報告フォーマット

ユーザーへの報告は、原則として以下の順で行います。

1. 結論
2. 作成/更新したファイル
3. PR URL
4. 反映した要点
5. 残っている要確認事項
6. 次に人間が見るべきポイント
