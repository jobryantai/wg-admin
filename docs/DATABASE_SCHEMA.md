# Database Schema — Phase One

## peers
| column      | type      | notes |
|-------------|-----------|-------|
| id          | serial PK |       |
| name        | text      | optional |
| public_key  | text      | unique |
| ip_address  | inet      | unique |
| created_at  | timestamp | default now() |
| enabled     | boolean   | default true |

## users
| column      | type      | notes |
|-------------|-----------|-------|
| id          | serial PK |       |
| username    | text      | unique |
| password    | text      | bcrypt hash |
| created_at  | timestamp | default now() |

