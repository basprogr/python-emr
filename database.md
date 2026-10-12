## Table `logbook`

### Columns

| Name | Type | Constraints |
|------|------|-------------|
| `id` | `int8` | Primary Identity |
| `room` | `varchar` |  |
| `patient_name` | `varchar` |  Nullable |
| `tasks` | `jsonb` |  Nullable |
| `therapies` | `jsonb` |  Nullable |
| `created_at` | `varchar` |  |
| `vital_signs` | `jsonb` |  Nullable |
| `no_rm` | `varchar` |  Nullable |
| `diagnosa_medis` | `varchar` |  Nullable |

## Table `rooms`

### Columns

| Name | Type | Constraints |
|------|------|-------------|
| `id` | `text` | Primary |

## Table `messages`

### Columns

| Name | Type | Constraints |
|------|------|-------------|
| `id` | `int8` | Primary Identity |
| `room_id` | `text` |  Nullable |
| `user_name` | `text` |  |
| `content` | `text` |  |
| `reply_to_id` | `int8` |  Nullable |
| `created_at` | `timestamptz` |  Nullable |
| `file_url` | `text` |  Nullable |
| `file_type` | `varchar` |  Nullable |

## Table `user_logs`

### Columns

| Name | Type | Constraints |
|------|------|-------------|
| `id` | `int8` | Primary Identity |
| `room_id` | `text` |  Nullable |
| `user_name` | `text` |  |
| `last_seen` | `timestamptz` |  Nullable |

## Table `commands`

### Columns

| Name | Type | Constraints |
|------|------|-------------|
| `id` | `int8` | Primary Identity |
| `command` | `text` |  Unique |
| `url` | `text` |  |
| `description` | `text` |  Nullable |

## Table `push_subscriptions`

### Columns

| Name | Type | Constraints |
|------|------|-------------|
| `id` | `uuid` | Primary |
| `user_id` | `text` |  Nullable |
| `subscription` | `jsonb` |  |
| `created_at` | `timestamptz` |  |

## RLS Policies

### `rooms`

| Policy | Command | Roles | Action | USING | WITH CHECK |
|--------|---------|-------|--------|-------|------------|
| `Public Read Rooms` | SELECT | public | PERMISSIVE | `true` | — |

### `user_logs`

| Policy | Command | Roles | Action | USING | WITH CHECK |
|--------|---------|-------|--------|-------|------------|
| `Public Read User Logs` | SELECT | public | PERMISSIVE | `true` | — |
| `Public Upsert User Logs` | ALL | public | PERMISSIVE | `true` | `true` |

### `messages`

| Policy | Command | Roles | Action | USING | WITH CHECK |
|--------|---------|-------|--------|-------|------------|
| `Strict Bas Dalq Delete Messages` | DELETE | public | PERMISSIVE | `(user_name = ANY (ARRAY['bas'::text, 'dalq'::text]))` | — |
| `Strict Bas Dalq Insert Messages` | INSERT | public | PERMISSIVE | — | `((user_name = ANY (ARRAY['bas'::text, 'dalq'::text])) AND (room_id IS NOT NULL))` |
| `Strict Bas Dalq Read Messages` | SELECT | public | PERMISSIVE | `true` | — |

### `commands`

| Policy | Command | Roles | Action | USING | WITH CHECK |
|--------|---------|-------|--------|-------|------------|
| `Public Read-Only` | SELECT | public | PERMISSIVE | `true` | — |

### `push_subscriptions`

| Policy | Command | Roles | Action | USING | WITH CHECK |
|--------|---------|-------|--------|-------|------------|
| `Izinkan insert subscription untuk semua` | INSERT | public | PERMISSIVE | — | `true` |

### `logbook`

| Policy | Command | Roles | Action | USING | WITH CHECK |
|--------|---------|-------|--------|-------|------------|
| `Akses Publik Logbook` | ALL | public | PERMISSIVE | `true` | `true` |

