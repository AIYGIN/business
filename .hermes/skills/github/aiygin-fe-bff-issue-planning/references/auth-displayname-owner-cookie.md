# Google displayName を TODO 所有者として使う認証設計メモ

AIYGIN の認証/TODO 所有者設計で、ユーザーから「DB にユーザー情報を持たず、Google displayName を用いて TODO のユーザー情報を紐づける」「displayName も Cookie から取る設計にしたい」と指定された場合の補足。

## 前提

- `users` / `auth_accounts` table は作らない。
- Google user ID / Google `sub` は Frontend へ公開しない。
- Google access token / ID token / refresh token は DB に保存しない。
- Supabase 等 managed Postgres は TODO 等のアプリケーションデータ保存に使う。

## 設計方針

- Google callback 成功時に Google user 情報から `displayName` を取得する。
- BFF JWT に `displayName` claim を含める。
- BFF JWT は `access_token` HttpOnly Cookie に保存する。
- TODO API では request path/query/body から `userId` / `displayName` / `ownerDisplayName` を受け取らない。
- `JwtAuthGuard` が `access_token` Cookie 内 JWT を検証し、claim から `CurrentUser.displayName` を復元する。
- TODO Service は `CurrentUser.displayName` を `todos.owner_display_name` と照合する。

## TODO table 案

```text
todos
- id (primary key)
- owner_display_name (indexed, Google displayName from BFF JWT Cookie)
- title
- completed
- created_at
- updated_at
- INDEX(owner_display_name)
```

## Issue に入れるべき注意

- displayName は重複・変更され得るため、TODO 所有者紐づけとしては不安定になり得る。
- それでも今回の設計判断として displayName を owner key にする場合は、リスクとリスク対策に明記する。
- 将来、安定した owner key へ移行する余地を残す。
- `/auth/me` の公開 DTO に Google user ID は含めない。

## 受け入れ条件例

- Guard が `access_token` Cookie 内 JWT から `displayName` を復元する。
- TODO 作成・一覧・更新・削除では、request body/query/path ではなく `CurrentUser.displayName` を owner として使う。
- TODO は `owner_display_name` により Google `displayName` と紐づく。
- users / auth_accounts は DB に作成されない。
