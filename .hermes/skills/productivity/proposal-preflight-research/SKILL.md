---
name: proposal-preflight-research
description: Use when running pre-proposal research before drafting Japanese proposals. Orchestrates subagent investigation of cost, risks, feasibility, and existing services/substitutes, then returns decision-ready findings with facts, assumptions, sources, and confirmation items.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [proposal, research, subagents, cost, risk, feasibility, japanese]
    related_skills: [proposal-planning-workflow, research-intelligence]
---

# 提案前 事前調査サブエージェント運用

## 目的

提案書を作り始める前に、別サブエージェントで以下を調査し、ユーザーが「この提案を進める価値があるか」を判断できる材料を作る。

- コスト
- リスク
- 実現可能性
- 既存サービス・代用手段

このスキルは、提案書本文を書くスキルではない。提案書作成前の意思決定材料を作るために使う。

## 使うタイミング

以下の依頼で使う。

- 「提案書を作る前に調査して」
- 「コスト、リスク、実現可能性を見て」
- 「似たサービスや代替手段がないか調べて」
- `proposal-planning-workflow` の Phase 1 を実行するとき

使わないケース:

- ユーザーが明示的に事前調査を不要としている場合
- 単純な文章整形だけの場合
- 法務・会計・投資判断の最終結論を出す目的の場合

## 入力として受け取る情報

親エージェントは、サブエージェントへ渡す前に以下を整理する。

- テーマ
- 背景
- 読み手・決裁者
- 期待する意思決定
- 制約条件
- 既知の候補案
- Markdown文書やIssueなどの前提資料

不足が大きく、調査観点が変わる場合は、先に最大3問だけユーザーへ確認する。

## 調査観点

### 1. コスト

- 初期実装コスト
- 運用コスト
- 外部サービス/API利用料
- 保守・監視・人手対応コスト
- 将来の拡張時に増えるコスト

### 2. リスク

- 技術リスク
- セキュリティ/プライバシーリスク
- 法務/規約/ライセンスリスク
- 運用リスク
- ユーザー体験上のリスク
- 組織・意思決定上のリスク

### 3. 実現可能性

- v1で実現できる範囲
- PoCで検証すべき範囲
- 前提技術・API・データの入手性
- スケジュール上の不確実性
- 既存システムとの接続難易度

### 4. 既存サービス・代用手段

- 類似SaaS
- 既存OSS
- 外部API
- 手動運用
- 既存社内運用の改善
- 内製しない選択肢

## サブエージェント依頼テンプレート

```text
日本語で回答してください。
以下の提案テーマについて、提案書作成前の事前調査をしてください。

テーマ:
<テーマ>

背景・制約:
<背景・制約>

読み手・期待する意思決定:
<読み手・意思決定>

調査観点:
1. コスト（初期/運用/外部サービス/API/保守）
2. リスク（技術/セキュリティ/法務規約/運用/UX）
3. 実現可能性（v1/PoC/前提技術/不確実性）
4. 既存サービス・代用手段

出力形式:
- 結論
- 事実
- 仮定/推論
- 要確認
- 推奨方針
- ユーザーに確認すべき判断事項（最大5個）

外部情報を調べた場合はURLを付けてください。不明な点は断定せず「要確認」としてください。
```

## 親エージェントの集約ルール

サブエージェントの結果をそのまま貼らない。親エージェントは次の形に要約する。

```markdown
## 事前調査サマリー

### 結論

### コスト見立て

### 主要リスク

### 実現可能性

### 既存サービス・代用手段

### 推奨方針

### ユーザーに確認したい判断事項
```

## agent-memory 記録ルール

`proposal-planning-workflow` の一部として事前調査を行う場合、親エージェントは作業自体を `agent-memory` コマンドで必ず記録する。サブエージェントに調査を任せた場合も、最終的な記録責任は親エージェントが持つ。

```bash
rtk agent-memory write --content "proposal research: <topic> 調査開始。観点=cost/risk/feasibility/alternatives / input=<概要>"
rtk agent-memory write --content "proposal research: <topic> 調査完了。結論=<要約> / sources=<主要URL> / 要確認=<項目> / next=<確認ゲートまたは追加調査>"
rtk agent-memory scratchpad add --text "proposal research <topic>: <未確認事項または追加調査TODO>"
```

記録する内容:

- 調査開始時: テーマ、前提資料、調査観点。
- 調査完了時: 結論、主要な根拠URL、未確認事項、推奨方針。
- ブロック時: 取得できなかった情報、代替調査、再開条件。

注意:

- 作業ログ・一時的な調査結果は daily log に残す。Hermes persistent memory には保存しない。
- `agent-memory write --target long_term` は、今後も再利用する安定した調査方針や運用決定ができた場合だけ使う。

## 品質基準

- 事実、仮定、推論、要確認を混ぜない。
- 外部情報にはURLを付ける。
- コストは断定せず、初期/運用/外部サービス/保守に分ける。
- 「既存サービスがあるなら内製不要」と短絡しない。内製理由、差別化、制約を比較する。
- わからないことは「不明」「要確認」と書く。

## Common Pitfalls

1. 事前調査なのに提案書本文を書き始める。
2. 既存サービス調査を省略し、内製前提で進める。
3. 無料APIを「無料だから低リスク」と扱う。
4. サブエージェントの出力を検証せず事実として断定する。
5. ユーザーが判断すべき事項を曖昧にしたまま次工程へ進む。

## Verification Checklist

- [ ] コスト、リスク、実現可能性、既存サービス/代用手段を調査した。
- [ ] 事実、仮定、推論、要確認を分けた。
- [ ] 外部情報にURLを付けた、または未調査/不明と明記した。
- [ ] 推奨方針を出した。
- [ ] ユーザーに確認すべき判断事項を最大5個に絞った。
- [ ] 調査開始、調査完了、ブロック/未確認事項を `agent-memory write` または `agent-memory scratchpad add` で記録した。
