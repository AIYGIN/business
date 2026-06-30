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
| 補完データ | J-Quants無料範囲で不足する項目は手動CSVで補完する。実データCSVはGit管理せず、BFF repo内のgitignore/private localに置く |
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
Generated CSV (batch final artifact)
    ↓
Raw Data Store / CSV Import
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
pnpm dividend-analysis:fetch-edinet-cashflow --symbols 8058,9432,8306 --years 10 --out data/dividend-analysis/private/edinet-cashflow.csv
pnpm dividend-analysis:generate-csv --symbols 8058,9432,8306 --out data/dividend-analysis/private/manual-supplement.csv
pnpm dividend-analysis:import-csv --file data/dividend-analysis/private/manual-supplement.csv
pnpm dividend-analysis:recalculate --score-version dividend-score-v1
pnpm dividend-analysis:fetch-high-dividend-candidates --source yahoo-finance --limit 50 --out data/dividend-analysis/private/candidates-yahoo-high-dividend.csv
```

実装時にコマンド名はBFFの既存規約へ合わせる。batchの最終成果物はCSVにする。`generate-csv` はローカルで実行し、J-Quants/EDINET等で埋められる列を自動入力し、APIで取れない列は空欄ではなく `TODO:<固定文言>` または `notAvailableReason` 付きで出力する。人間はそのCSVを補完して `import-csv` に渡す。

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

実データCSVやJ-Quants由来Raw JSONはGit管理しない。BFF repoにはCSVテンプレート、schema、import/fetch/recalculateコマンド、テスト用fixtureだけを置き、実データは `data/dividend-analysis/private/` のようなgitignore配下に配置する。

### 4.2.1 batch最終成果物CSVとTODO固定文言

batchの最終成果物はCSVとする。BFFはこのCSVをimportし、正規化・スコア計算を行う。

CSV生成時の扱い:

- 自動取得できた値はCSVに値を入れる。
- 自動取得できなかった値は空欄にせず、`TODO:<理由>` の固定文言を入れる。
- `notAvailableReason` に不足理由を入れる。
- `sourceType` には `jquants_api` / `edinet_api` / `manual_csv` / `candidate_source` などを入れる。

TODO固定文言例:

| ケース | CSV値または `notAvailableReason` |
|---|---|
| J-Quants無料範囲で取れない | `TODO: jquants_free_unavailable` |
| EDINETから抽出失敗 | `TODO: edinet_extract_failed` |
| 金融業のためFCF対象外 | `TODO: fcf_not_applicable_financial_business` |
| Yahoo候補リストから銘柄候補だけ取得し、財務値未取得 | `TODO: candidate_only_metrics_pending` |
| 人間確認が必要 | `TODO: manual_review_required` |

この方針により、「CSVを見れば未補完項目が分かる」状態にする。

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

まず固定20銘柄で以下を確認し、その後同じ取得・補完フローを高配当上位50候補にも適用できるか確認する。

| 確認項目 | 判定 |
|---|---|
| J-Quants無料範囲で取得できる銘柄基本情報 | 可否確認 |
| 財務サマリーで配当性向・配当実績に近い値を取れるか | 可否確認 |
| 株価/終値から直近利回り計算に使える値を取れるか | 可否確認 |
| FCF算出に必要な営業CF・投資CFが無料範囲で取れるか | 不足想定。CSV補完候補 |
| 10年減配履歴・増配率に必要な履歴が無料範囲で足りるか | 不足想定。CSV補完候補 |
| 金融業のFCF N/A処理に必要な業種判定ができるか | 可否確認 |

### 6.1 BFF現状mockをどこまでJ-Quants APIで補填できるか

BFFの現状mock/API DTOが必要としている主な項目は以下。実装前スパイクでは、各項目を「J-Quants無料範囲で自動取得」「J-Quants無料範囲から計算」「手動CSV補完」「対象外/要確認」に分類する。

| BFF項目 | 現状mock/APIでの使い道 | J-Quants無料範囲での見込み | 補完方針 |
|---|---|---|---|
| `symbolId` | 銘柄コード | 上場銘柄一覧で取得できる見込み | API優先 |
| `companyName` | 企業名表示 | 上場銘柄一覧で取得できる見込み | API優先 |
| `sector` | 業種表示、金融業判定 | 上場銘柄一覧で取得できる見込み | API優先。不足時CSV |
| `latestDividendYield` | 一覧の直近利回り、利回りスコア | 株価と配当関連値が揃えば計算可能。ただし無料範囲の遅延・配当項目不足に注意 | APIで計算できない場合CSV |
| `payoutRatio` | 配当性向スコア | 財務サマリーで近い値が取れるかスパイク対象 | 取れない場合CSV |
| `per` / `pbr` / `roe` | 財務指標スコア | 財務サマリーまたは株価/財務値から取得・計算できるかスパイク対象 | 取れない場合CSV |
| `fcf` | FCFスコア | J-Quants無料範囲では営業CF・投資CFが不足する可能性が高い。一方、EDINET APIで有価証券報告書XBRLを取得し、営業CF・投資CFを抽出できれば無料で自動補完できる可能性がある | 第一候補はEDINET自動抽出。失敗・非対応時はCSVに `TODO: edinet_extract_failed` を出して手動補完 |
| `dividendGrowthRate10y` | 10年増配率スコア | 無料範囲では10年履歴が不足する可能性が高い | 基本CSV補完 |
| `dividendCutCount10y` | 10年減配履歴スコア | 無料範囲では10年履歴が不足する可能性が高い | 基本CSV補完 |
| `totalScore` / `judgement` / `safetyLabel` | BFF計算済み分析結果 | APIから取得しない | BFFで計算 |
| `scoreBreakdown.*` | スコア内訳、得点理由 | APIから取得しない | BFFで計算 |
| `dataSources` / `dataAsOfDate` / `updatedAt` | 出典・基準日・更新日時 | API取得日時とCSV出典から構成 | BFFで構成 |

原則は「APIで取れないものは全部CSV補完」でよい。ただし何が取れないかは実APIスパイクで確定する。したがって、BFF Issueでは最初のタスクを「BFF現状mock項目のJ-Quants無料範囲補填マトリックス作成」とする。

### 6.2 FCFを無料で自動取得する候補: EDINET API

FCFが取れないのはスコア設計上かなり痛い。J-Quants無料範囲では財務諸表BS/PL/CF詳細がPremium限定のため、営業CF・投資CFを直接取れない可能性が高い。一方、無料で自動化する候補としてEDINET APIがある。

根拠:

- 金融庁のEDINET API仕様書は、EDINET APIがプログラムを介してEDINETのデータベースから効率的にデータ取得できるAPIであると説明している。
- EDINET APIには書類一覧APIと書類取得APIがあり、書類取得APIでXBRL等の書類本体を取得できる。
- EDINET APIはAPIキー認証が必要だが、J-Quants Premium契約とは別で、無料で利用できる可能性がある。
- 有価証券報告書の閲覧期間は有価証券報告書で10年とされているため、10年減配/増配・FCF確認の補助データ源として相性がよい。

EDINETで狙う値:

- 営業活動によるキャッシュ・フロー
- 投資活動によるキャッシュ・フロー
- FCF = 営業CF + 投資CF、または 営業CF - 投資CFの表示符号に応じた正規化

注意:

- XBRLタグは会計基準、連結/非連結、企業ごとの差異があるため、実装難易度はJ-Quants APIより高い。
- 金融業は引き続きFCF N/A方針を維持する。
- EDINET抽出に失敗した場合はCSVに `TODO: edinet_extract_failed` を出し、人間が補完する。
- 最初から全銘柄対応を狙わず、固定20銘柄で営業CF・投資CFが抽出できるかをSpikeする。

EDINET取得は、BFF batchの「無料FCF補完スパイク」として扱う。成功した場合、FCFは手動CSV補完ではなく `edinet_api` 由来の自動補完に昇格する。

参照:

- EDINET API関連資料: https://disclosure2dl.edinet-fsa.go.jp/guide/static/disclosure/WZEK0110.html
- EDINET API仕様書: https://disclosure2dl.edinet-fsa.go.jp/guide/static/disclosure/download/ESE140206.pdf
- J-Quants data spec: https://jpx-jquants.com/en/spec/data-spec

### 6.3 対象銘柄リストの取得方針

対象銘柄は以下を同時並行で扱えるようにする。

1. 固定20銘柄リスト
   - 既存PoCの比較・画面確認用。
   - スコア計算・UI・CSV補完の安定した検証対象にする。
2. 高配当上位候補リスト
   - Yahoo!ファイナンスの高配当利回りスクリーニング（例: `https://finance.yahoo.co.jp/stocks/screening/highdividend?sort=-dividendYield`）などから上位50社候補を取得できる仕組みを検討する。
   - これは分析データ本体ではなく、対象銘柄候補の取得元として扱う。
   - 自動スクレイピング可否・利用条件は要確認。PoCではまずローカル手動コマンド、または人間が取得した候補CSVのimportから始める。

候補リスト取得コマンド例:

```bash
pnpm dividend-analysis:fetch-high-dividend-candidates --source yahoo-finance --limit 50 --out data/dividend-analysis/private/candidates-yahoo-high-dividend.csv
pnpm dividend-analysis:import-candidates --file data/dividend-analysis/private/candidates-yahoo-high-dividend.csv
```

BFFは固定20銘柄と候補上位50銘柄を入力セットとして扱い、J-Quants無料範囲で取れる項目を取得し、不足項目をCSV補完対象にする。

## 7. 手動CSV補完方針

CSVには最低限以下を持たせる。

```csv
symbolId,companyName,sector,dataAsOfDate,fcf,payoutRatio,dividendGrowthRate10y,dividendCutCount10y,latestDividendYield,per,pbr,roe,sourceName,sourceUrl,sourceType,fcfSource,notAvailableReason,note
```

注意:

- CSV値にも出典名と基準日を持たせる。
- 転記ミスを前提に、BFF import時に型・範囲・必須項目を検証する。
- 手動CSV由来の項目はFEで出典表示できるようにする。
- ローカルコマンドでAPI取得済み項目を埋めたCSVを生成し、人間が空欄・不足列を補完できる形にする。
- APIで取れない項目は全部CSV補完対象にする。補完対象はスパイク結果で確定し、CSV schemaに反映する。
- FCFはまずEDINET APIで無料自動取得を試し、失敗したものだけTODO固定文言つきで手動補完に回す。

### 7.1 CSV配置方式の議論と採用案

議論した選択肢は以下。

| 案 | 内容 | メリット | デメリット/リスク | 判断 |
|---|---|---|---|---|
| A | BFF repoに実データCSVもcommitする | 単純で再現性が高い | J-Quants由来データをGitHubに置くリスクがある。repoがprivateでも将来共有・漏洩・公開化の懸念が残る | 非採用 |
| B | 無料公開サーバー/S3的な場所にCSVを置き、BFFが参照する | 更新しやすく、BFF deployとデータ更新を分けやすい | 公開状態になりやすく、J-Quantsの本人私的利用/PoC前提と相性が悪い。第三者が使用できる状態に近づく | 非採用 |
| C | BFF repoにimport機構だけ置き、実データCSVはgitignore/private localに置く | 最小構成、安全寄り、PoC向き。BFFのNormalizer/Score Calculatorと近い場所で検証できる | 実行環境ごとにCSV配置が必要 | 採用 |
| D | private object storageにCSVを置き、BFFまたはbatchが認証付きで取得する | 実運用に近く、repoにデータを置かずに済む | 認証、権限、設定、運用が増える | Phase 2以降 |
| E | `batch` repoを新設し、取得・import・recalculateを分離する | 責務分離が明確 | PoC初期には過剰。BFF API/データ保存との調整が増える | 後回し |

採用案はC。

```text
/Users/ynaragin/git/bff
  data/
    dividend-analysis/
      templates/
        manual-supplement.example.csv   # Git管理OK
      private/
        manual-supplement.csv           # gitignore
        jquants-raw-YYYYMMDD.json       # gitignore
```

`.gitignore` 例:

```gitignore
data/dividend-analysis/private/
```

BFF repoに置くもの:

- CSVテンプレート
- CSV schema / import validation
- J-Quants fetch command
- CSV import command
- recalculate command
- Normalizer / Score Calculator
- テスト用fixture

BFF repoに置かないもの:

- J-Quants由来の実データCSV
- J-Quants APIキー
- 有料/規約対象データのRaw dump
- 第三者が再利用できる形の分析済みデータ

`batch` repoを新設する判断基準:

- J-Quants以外にEDINET、KABU+、複数CSVなどデータ源が増える。
- batchだけ依存ライブラリが重くなる。
- batchだけ別実行環境、別スケジュール、別deployにしたくなる。
- raw / normalized / score result の履歴管理が必要になる。
- 失敗通知、再実行、監査ログなどの運用要件が強くなる。

現時点では、責務分離よりPoCで実データを安全に扱えることを優先し、BFF repo内のgitignore/private local方式で進める。

## 8. 受け入れ条件

### BFF

- [ ] batchの最終成果物はCSVである。
- [ ] 手動batchでJ-Quants API無料範囲の実データを取得できる。
- [ ] EDINET APIから営業CF・投資CFを抽出し、FCFを無料自動補完できるかSpikeする。
- [ ] BFF現状mock項目について、J-Quants無料範囲で補填できる項目とCSV補完が必要な項目のマトリックスを作成する。
- [ ] ローカルコマンドでAPI取得済み項目を埋めたCSVを生成できる。
- [ ] 取れない項目は空欄ではなく `TODO:<固定文言>` と `notAvailableReason` を出力する。
- [ ] 手動CSVをimportできる。
- [ ] 実データCSVとJ-Quants由来Raw JSONはgitignore/private localに置き、Git管理しない。
- [ ] BFF repoにはCSVテンプレート、schema、import/fetch/recalculate/generate-csvコマンド、fixtureだけを置く。
- [ ] Raw Dataに取得元、基準日、取得日時が保存される。
- [ ] 固定20銘柄と高配当上位50候補の両方を入力セットとして扱える。
- [ ] Yahoo!ファイナンス等の高配当候補取得は、利用条件確認後にローカル手動コマンドまたは候補CSV importとして扱う。
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
| 公開CSV配置 | 無料公開サーバー/S3的な場所にCSVを置くと第三者が使用できる状態に近づく | 採用しない。実データCSVはBFF repoのgitignore/private localに置く |
| 高配当候補リスト取得 | Yahoo!ファイナンス等から上位50社を取る場合、利用条件や取得方法の確認が必要 | 分析データ本体ではなく候補銘柄リストとして扱う。まずローカル手動コマンドまたは候補CSV importで開始する |
| 無料範囲の不足 | J-Quants無料範囲では配当金情報、BS/PL/CF詳細、10年履歴が足りない可能性 | まずJ-Quants無料範囲でSpikeし、FCFはEDINET API自動抽出を試す。残りはTODO固定文言つきCSVで手動補完 |
| EDINET XBRL抽出難度 | EDINETから営業CF・投資CFを取れる可能性はあるが、XBRLタグ差異・会計基準差異がある | 固定20銘柄でSpikeし、失敗時は `TODO: edinet_extract_failed` としてCSVに残す |
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
  - 実データCSVをgitignore/private localに置く方針。
  - batch最終成果物をCSVにし、取れない項目をTODO固定文言にする設計。
  - J-Quants無料範囲でBFF現状mockをどこまで補填できるかのスパイク設計。
  - EDINET APIで営業CF・投資CFを抽出してFCFを無料自動補完するスパイク設計。
  - APIで取れない項目を全部CSV補完対象にする設計。
  - ローカルコマンドでCSV生成する設計。
  - CSV template/schema/import設計。
  - Normalizer/Score Calculator設計。
  - 固定20銘柄と高配当上位50候補リストを同時並行で扱う方針。
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

## 12. 人間コメント反映後の確定事項と残確認

### 確定事項

1. J-Quants APIでの実現可能性を確認する。
   - BFFの現状mock項目を、J-Quants無料範囲でどこまで補填できるかを見る。
   - 実装前スパイクの成果物は「APIで取れる項目 / 計算できる項目 / CSV補完が必要な項目」のマトリックスにする。
2. batchの最終成果物はCSVにする。
   - APIで埋められる列を自動入力し、取れない列は `TODO:<固定文言>` と `notAvailableReason` を出す。
3. 手動CSV補完は、基本的にAPIで取れないもの全部を対象にする。
   - 何が取れないかは現時点で断定せず、スパイクで判定する。
4. FCFは重要度が高いため、手動補完前にEDINET APIで無料自動取得を試す。
   - EDINETから営業CF・投資CFを抽出できればFCFを自動補完する。
   - 抽出失敗時だけ `TODO: edinet_extract_failed` として手動補完に回す。
5. 実データCSVはローカルコマンドで生成するイメージにする。
   - APIで埋められる列を自動入力し、足りない列を人間が補完する。
6. BFFスコア計算式の閾値は既存方針から変更しない。
7. 金融業のFCF N/A換算ルールは既存方針から変更しない。
8. 対象銘柄は、固定20銘柄と高配当上位50候補を同時並行で扱えるようにする。
   - 高配当上位50候補は、Yahoo!ファイナンス高配当利回りスクリーニング等から取得する仕組みを検討する。
   - ただし取得方法と利用条件は要確認であり、まずローカル手動コマンドまたは候補CSV importで扱う。

### 残確認

- J-Quants無料範囲で実際に取れる項目。
- EDINET APIで固定20銘柄の営業CF・投資CFをどれだけ安定抽出できるか。
- Yahoo!ファイナンス等の高配当候補リスト取得を自動化してよいか、または人間がCSVで渡す運用にするか。
- private localディレクトリ名とCSV生成/import手順の最終命名。
