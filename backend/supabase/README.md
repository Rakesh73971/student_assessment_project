# Supabase Setup

Alembic has been removed from this project. The live SQLAlchemy models in
`app/models` are the application source of truth, and `schema.sql` is the
Supabase/PostgreSQL bootstrap script that mirrors those models.

## New Supabase Project

1. Open the Supabase SQL editor.
2. Run `schema.sql` once against the target database.
3. Configure the FastAPI database variables in `backend/.env`.
4. Restart the FastAPI backend.

`CREATE TABLE IF NOT EXISTS` in `schema.sql` does **not** add new columns to old tables; use migrations when upgrading.

## Existing Supabase Project

Run each file in `migrations/` in filename order:

1. `001_add_responses_student_id_and_scores_session_id.sql`
2. `002_harden_rls_and_timestamps.sql`

Use this path when you already created tables before the latest schema changes.

## RLS Context

The included policies use PostgreSQL settings:

- `app.current_user_id`
- `app.current_user_role`

The FastAPI dependency layer sets these values after JWT authentication. The
database session helper then applies them with `set_config(..., true)` for the
current transaction. This lets RLS understand which user is making the request.

## Connection Settings

Use Supabase database connection values in `backend/.env`:

```env
DATABASE_HOSTNAME=db.your-project-ref.supabase.co
DATABASE_PORT=5432
DATABASE_PASSWORD=your-supabase-db-password
DATABASE_NAME=postgres
DATABASE_USERNAME=postgres
```

For production, keep the password in Railway/Render environment variables, not
in source control.

## Verification Queries

After running SQL, these should return rows:

```sql
select tablename, policyname
from pg_policies
where schemaname = 'public'
order by tablename, policyname;

select tgname
from pg_trigger
where tgname like 'set_%_updated_at'
order by tgname;
```
