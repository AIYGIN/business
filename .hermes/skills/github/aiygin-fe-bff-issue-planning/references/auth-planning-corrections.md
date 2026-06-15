# 認証基盤 Issue 計画時の補足ルール

AIYGIN の FE/BFF 認証基盤を business Issue 化するとき、以下を見落とさない。

## FE 前提

- FE は BFF の OpenAPI 定義を元に Orval で API client / mock を自動生成する前提を書く。
- Orval 生成物は手動編集しない。
- BFF の API 契約変更時は OpenAPI 更新と FE 側 Orval 再生成をセットで記載する。
- Next.js middleware を使った認証基盤を FE 要件に含める。
- 未ログインで todo 画面などの保護対象 route にアクセスした場合は、BFF の OAuth login endpoint へ直接飛ばさず、まず FE の `/login` 画面へ redirect する前提を書く。
- `/login` 画面からユーザー操作で BFF の OAuth login endpoint へ top-level navigation する。
- ログイン成功後は `/auth/me` を再確認し、todo 画面などの保護対象画面へアクセスできることを acceptance criteria に入れる。

## BFF / DB 前提

- users / auth_accounts を「DB 導入前の in-memory repository」と決め打ちしない。
- ユーザー情報を DB に持たない前提が指定された場合は、users / auth_accounts table を作らない設計にする。
- Supabase 等の無料枠 managed Postgres は、ユーザー情報ではなく TODO 等のアプリケーションデータ保存用として扱う。
- 必要 env に `DATABASE_URL` を含める場合も、用途は users / auth_accounts ではなくアプリケーションデータ用だと明記する。
- JWT `sub` や owner key の設計はユーザー指定を優先する。Google `displayName` を TODO 所有者にする指定がある場合は、Google callback で取得した `displayName` を BFF JWT claim に含め、`access_token` Cookie 内 JWT から Guard が `CurrentUser.displayName` を復元する設計にする。
- displayName owner 設計では、TODO table は `owner_display_name` を持ち、TODO Service は request path/query/body ではなく `CurrentUser.displayName` を `owner_display_name` 条件に使う。
- displayName は重複・変更され得るため、リスクと将来の移行余地を Issue に明記する。
- Acceptance criteria には、users / auth_accounts を作らず、Cookie 内 JWT から復元した `CurrentUser.displayName` で TODO を紐づけることを入れる。
- リスクには無料枠 DB の制限、停止、接続数上限、migration / backup 方針を含める。

## Provider 置換時

- X OAuth など元仕様の provider 固有名称を、依頼された provider（例: Google OAuth / OIDC）へ本文全体で置換する。
- endpoint、cookie 名、env、scope、user 識別子、provider_user_id の意味も provider に合わせて更新する。
- Google の場合、scope は原則 `openid profile email`、provider_user_id は Google `sub` を正とする。
