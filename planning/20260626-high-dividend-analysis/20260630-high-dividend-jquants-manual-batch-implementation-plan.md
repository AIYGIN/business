# 高配当分析ツール本格化 実装計画: J-Quants手動batch + BFFスコア計算

## 1. 結論

本人の個人利用/PoCに限定し、J-Quants APIの無料範囲と手動CSV補完を使って、任意タイミングで実データを取得できる高配当分析ツールへ進める。

v1本格化では、外部APIは「実データ取得」だけに使う。配当安全性スコア、判定、スコア内訳、得点理由、欠損時の扱いはBFFが計算する。FEはBFF APIの結果表示に徹し、スコア計算やJ-Quants APIキー管理を持たない。

## 2. 確定前提

| 項目 | 方針 |
|---|---|
| 利用範囲 | 本人の個人利用/PoCのみ |
| 公開範囲 | 一般公開、第三者提供、商用SaaS、社内外共有はv1対象外 |
| 外部データ | J-Quants APIを第一候補。ただし、まず無料範囲を使う |
| 補完データ | J-Quants無料範囲で不足する項目は手動CSVで補完する |
| 更新方式 | 自動cronではなく、人間が任意タイミングで起動する手動batch |
| 画面表示 | 画面リクエスト中にJ-Quants APIへ同期アクセスしない |
| スコア計算 | BFFがRaw/CSVデータから正規化・計算する |
| FE責務 | BFF APIレスポンスを表示する。Orval生成物は手動編集しない |
| AIサマリー | v1ではTODO。実装する場合も売買推奨・将来予測は禁止 |

## 3. 推奨アーキテクチャ

```text
Human Operator
    ↓ manual command
Manual Batch
    ↓
J-Quants API Free Scope / Manual CSV
    ↓
Raw Data Store
    ↓
BFF Normalizer
    ↓
BFF Score Calculator
    ↓
BFF API
    ↓
FE Dividend Analysis Page
```

### ポイント

- J-Quants APIキーはBFF/サーバー側だけに置く。
- 手動batchはBFFリポジトリ側のCLIまたはnpm scriptとして実装する。
- Raw Dataには取得元、取得日時、データ基準日、対象銘柄、取得方法を含める。
- BFF APIはRaw Dataを直接垂れ流さず、正規化済みの分析レスポンスを返す。
- `updatedAt` と `dataAsOfDate` を分ける。
- `isRealtime=false` を返す。
- `scoreVersion` を返し、計算式変更時に追跡できるようにする。

## 4. BFF実装方針

### 4.1 手動batch

BFF側に、任意タイミングで起動できる手動batchを追加する。

想定コマンド例:

```bash
pnpm dividend-analysis:fetch --symbols 8058,9432,8306 --as-of 2026-06-30
pnpm dividend-analysis:import-csv --file data/dividend-analysis/manual-supplement.csv
pnpm dividend-analysis:recalculate --score-version dividend-score-v1
```

実装時にコマンド名はBFFの既存規約へ合わせる。

### 4.2 Raw Data保存

保存対象:

- J-Quantsから取得した株価・財務サマリー等のRaw JSON
- 手動CSVから補完した配当履歴、減配履歴、FCF関連値など
- `sourceType`: `jquants_api` / `manual_csv`
- `sourceName`
- `dataAsOfDate`
- `fetchedAt`
- `symbolId`
- `rawPayload`
- `importBatchId`

v1ではJSONファイル、SQLite、既存DBのいずれでもよい。BFF実装時に既存技術スタックへ合わせる。

### 4.3 正規化

BFFはRaw Dataから以下のNormalized Dataを生成する。

- `symbolId`
- `companyName`
- `sector`
- `fcf`
- `payoutRatio`
- `dividendGrowthRate10y`
- `dividendCutCount10y`
- `latestDividendYield`
- `per`
- `pbr`
- `roe`
- `isFinancialBusiness`
- `dataSources`
- `dataAsOfDate`

無料範囲で不足する項目は、手動CSV補完または `notAvailableReason` を持たせる。

### 4.4 スコア計算

BFFが以下を計算する。

- `totalScore`
- `judgement`
- `safetyLabel`
- `scoreBreakdown.fcf`
- `scoreBreakdown.dividendCutHistory`
- `scoreBreakdown.dividendGrowth`
- `scoreBreakdown.payoutRatio`
- `scoreBreakdown.dividendYield`
- `scoreBreakdown.financialMetrics`

外部APIやFEはスコアを計算しない。

金融業はFCFをN/Aにし、残り指標で100点換算する。換算式はBFFのテストで固定する。

### 4.5 API

既存のBFF契約を活かす。

- `GET /enterprises/quantsInfo`
- `GET /enterprises/:symbolId/dividendAnalysis`

追加・修正候補:

- 一覧レスポンスに `scoreVersion` を含めるか検討する。
- 詳細レスポンスに欠損理由、補完データ有無、取得元情報を含める。
- API説明に「画面リクエスト中にJ-Quants APIへ同期アクセスしない」と明記する。

## 5. FE実装方針

FEは以下に限定する。

- Orval生成済みAPI clientを使ってBFFから一覧・詳細を取得する。
- `dataAsOfDate`、`updatedAt`、`isRealtime=false`、`scoreVersion` を表示する。
- スコア内訳、判定、得点理由、欠損理由を表示する。
- 免責注記を常時表示する。
- スコア計算、J-Quants API呼び出し、APIキー保持は行わない。

## 6. データ取得スパイク

最初に20銘柄で以下を確認する。

| 確認項目 | 判定 |
|---|---|
| J-Quants無料範囲で取得できる銘柄基本情報 | 可否確認 |
| 財務サマリーで配当性向・配当実績に近い値を取れるか | 可否確認 |
| 株価/終値から直近利回り計算に使える値を取れるか | 可否確認 |
| FCF算出に必要な営業CF・投資CFが無料範囲で取れるか | 不足想定。CSV補完候補 |
| 10年減配履歴・増配率に必要な履歴が無料範囲で足りるか | 不足想定。CSV補完候補 |
| 金融業のFCF N/A処理に必要な業種判定ができるか | 可否確認 |

## 7. 手動CSV補完方針

CSVには最低限以下を持たせる。

```csv
symbolId,companyName,sector,dataAsOfDate,fcf,payoutRatio,dividendGrowthRate10y,dividendCutCount10y,latestDividendYield,per,pbr,roe,sourceName,sourceUrl,note
```

注意:

- CSV値にも出典名と基準日を持たせる。
- 転記ミスを前提に、BFF import時に型・範囲・必須項目を検証する。
- 手動CSV由来の項目はFEで出典表示できるようにする。

## 8. 受け入れ条件

### BFF

- [ ] 手動batchでJ-Quants API無料範囲の実データを取得できる。
- [ ] 手動CSVをimportできる。
- [ ] Raw Dataに取得元、基準日、取得日時が保存される。
- [ ] BFFがRaw/CSVからNormalized Dataを生成する。
- [ ] BFFがスコア計算を行う。
- [ ] 金融業のFCF N/Aと100点換算ルールがテストされている。
- [ ] APIレスポンスに `updatedAt`、`dataAsOfDate`、`scoreVersion`、`isRealtime=false`、`dataSources` が含まれる。
- [ ] 画面リクエスト中にJ-Quants APIへ同期アクセスしない。
- [ ] J-Quants APIキーがFEへ露出しない。

### FE

- [ ] 一覧画面でBFF計算済みスコア順に表示される。
- [ ] 詳細画面でスコア内訳と得点理由が表示される。
- [ ] `updatedAt` と `dataAsOfDate` が区別して表示される。
- [ ] リアルタイムではない旨が表示される。
- [ ] 免責注記が表示される。
- [ ] FE側でスコア計算しない。

## 9. リスクと対策

| リスク | 内容 | 対策 |
|---|---|---|
| J-Quants規約 | 本人の私的利用を超えると制限に触れる可能性 | v1は本人PoC限定。第三者共有・公開・商用化は別途再設計 |
| 無料範囲の不足 | 配当金情報、BS/PL/CF詳細、10年履歴が足りない可能性 | まず無料範囲でSpikeし、不足は手動CSV補完 |
| 転記ミス | CSV補完で誤入力が入り得る | import時バリデーション、出典・基準日管理、レビュー欄 |
| スコア定義の揺れ | 計算式変更で過去スコアと混同する | `scoreVersion` を必須にする |
| 投資助言誤認 | スコアや文言が売買推奨に見える | 免責注記、禁止語、AIサマリーv1 TODO |
| APIキー漏洩 | FEやログにAPIキーが出る | APIキーはサーバー側のみ。ログ出力禁止 |

## 10. BFF委譲用入力

- 対象repo: `/Users/ynaragin/git/bff`
- 目的: J-Quants無料範囲/手動CSVを使った手動batchと、BFF内スコア計算を実装するためのIssue案を作る。
- 重要前提:
  - 本人の個人利用/PoCのみ。
  - 外部APIは実データ取得だけに使う。
  - スコア計算はBFFが担当する。
  - 画面リクエスト中にJ-Quants APIへ同期アクセスしない。
  - APIキーはFEへ露出しない。
  - OpenAPIには内部Raw Dataモデルを出さず、公開DTOだけを出す。
- 期待成果物:
  - 手動batch設計。
  - Raw Data保存設計。
  - CSV import設計。
  - Normalizer/Score Calculator設計。
  - 既存 `enterprises` APIの更新方針。
  - test方針。

## 11. FE委譲用入力

- 対象repo: `/Users/ynaragin/git/fe`
- 目的: BFF APIの計算済みレスポンスを使い、高配当分析画面で実データ分析結果を表示するためのIssue案を作る。
- 重要前提:
  - FEはスコア計算しない。
  - FEはJ-Quants APIを直接呼ばない。
  - Orval生成物は手動編集しない。
  - `updatedAt`、`dataAsOfDate`、`scoreVersion`、`isRealtime=false`、`dataSources`、免責注記を表示する。
- 期待成果物:
  - 一覧/詳細画面の表示更新。
  - 欠損理由・補完データ表示。
  - 非リアルタイム表示。
  - Story/test方針。

## 12. 次に人間が見るべきポイント

1. J-Quants無料範囲でどの指標が取れるか。
2. 手動CSV補完で許容する項目と出典。
3. BFFスコア計算式の閾値。
4. 金融業のFCF N/A換算ルール。
5. 20銘柄固定をいつ拡張するか。
