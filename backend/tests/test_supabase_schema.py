from pathlib import Path


SCHEMA_PATH = Path(__file__).resolve().parents[1] / "supabase" / "schema.sql"
MIGRATION_PATH = (
    Path(__file__).resolve().parents[1]
    / "supabase"
    / "migrations"
    / "002_harden_rls_and_timestamps.sql"
)


def test_supabase_schema_has_rls_helpers_and_triggers():
    schema = SCHEMA_PATH.read_text(encoding="utf-8")

    assert "create or replace function app_user_id()" in schema
    assert "create or replace function app_user_role()" in schema
    assert "create or replace function app_is_staff()" in schema
    assert "create trigger set_users_updated_at" in schema
    assert "create trigger set_scores_updated_at" in schema


def test_supabase_schema_has_write_policies_for_runtime_flows():
    schema = SCHEMA_PATH.read_text(encoding="utf-8")

    assert "create policy users_self_insert" in schema
    assert "create policy students_self_insert" in schema
    assert "create policy scores_staff_insert" in schema
    assert "create policy sessions_self_or_staff_access" in schema
    assert "create policy responses_self_or_staff_access" in schema


def test_supabase_hardening_migration_exists_for_existing_databases():
    migration = MIGRATION_PATH.read_text(encoding="utf-8")

    assert "drop policy if exists users_self_or_staff_select" in migration
    assert "create policy users_self_insert" in migration
    assert "create trigger set_practice_sessions_updated_at" in migration
