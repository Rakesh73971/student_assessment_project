-- Hardens Supabase/PostgreSQL behavior for existing databases.
-- Run after 001_* migrations if the database was created before this file.

do $$
begin
    create type userrole as enum ('ADMIN', 'INSTRUCTOR', 'STUDENT');
exception
    when duplicate_object then null;
end $$;

do $$
begin
    create type testtype as enum ('PRACTICE', 'ASSESSMENT', 'QUIZ');
exception
    when duplicate_object then null;
end $$;

do $$
begin
    create type questiontype as enum ('MULTIPLE_CHOICE', 'SHORT_ANSWER', 'ESSAY', 'TRUE_FALSE');
exception
    when duplicate_object then null;
end $$;

create or replace function set_updated_at()
returns trigger as $$
begin
    new.updated_at = now();
    return new;
end;
$$ language plpgsql;

drop trigger if exists set_users_updated_at on users;
create trigger set_users_updated_at before update on users
for each row execute function set_updated_at();

drop trigger if exists set_cohorts_updated_at on cohorts;
create trigger set_cohorts_updated_at before update on cohorts
for each row execute function set_updated_at();

drop trigger if exists set_students_updated_at on students;
create trigger set_students_updated_at before update on students
for each row execute function set_updated_at();

drop trigger if exists set_tests_updated_at on tests;
create trigger set_tests_updated_at before update on tests
for each row execute function set_updated_at();

drop trigger if exists set_questions_updated_at on questions;
create trigger set_questions_updated_at before update on questions
for each row execute function set_updated_at();

drop trigger if exists set_practice_sessions_updated_at on practice_sessions;
create trigger set_practice_sessions_updated_at before update on practice_sessions
for each row execute function set_updated_at();

drop trigger if exists set_responses_updated_at on responses;
create trigger set_responses_updated_at before update on responses
for each row execute function set_updated_at();

drop trigger if exists set_scores_updated_at on scores;
create trigger set_scores_updated_at before update on scores
for each row execute function set_updated_at();

create or replace function app_user_id()
returns integer as $$
begin
    return nullif(current_setting('app.current_user_id', true), '')::integer;
exception
    when invalid_text_representation then
        return null;
end;
$$ language plpgsql stable;

create or replace function app_user_role()
returns text as $$
begin
    return lower(nullif(current_setting('app.current_user_role', true), ''));
end;
$$ language plpgsql stable;

create or replace function app_is_staff()
returns boolean as $$
begin
    return app_user_role() in ('admin', 'instructor', 'service');
end;
$$ language plpgsql stable;

alter table users enable row level security;
alter table students enable row level security;
alter table cohorts enable row level security;
alter table tests enable row level security;
alter table questions enable row level security;
alter table practice_sessions enable row level security;
alter table responses enable row level security;
alter table scores enable row level security;

drop policy if exists users_self_or_staff_select on users;
create policy users_self_or_staff_select on users
    for select using (app_is_staff() or id = app_user_id());

drop policy if exists users_self_insert on users;
create policy users_self_insert on users
    for insert with check (
        app_user_role() in ('service', 'admin')
        or (app_user_id() is null and role = 'STUDENT')
    );

drop policy if exists users_self_or_staff_update on users;
create policy users_self_or_staff_update on users
    for update using (app_is_staff() or id = app_user_id())
    with check (app_is_staff() or id = app_user_id());

drop policy if exists students_self_or_staff_select on students;
create policy students_self_or_staff_select on students
    for select using (app_is_staff() or user_id = app_user_id());

drop policy if exists students_self_insert on students;
create policy students_self_insert on students
    for insert with check (app_is_staff() or user_id = app_user_id());

drop policy if exists students_self_update on students;
create policy students_self_update on students
    for update using (app_is_staff() or user_id = app_user_id())
    with check (app_is_staff() or user_id = app_user_id());

drop policy if exists cohorts_staff_access on cohorts;
create policy cohorts_staff_access on cohorts
    for all using (app_user_role() = 'admin' or instructor_id = app_user_id())
    with check (app_user_role() = 'admin' or instructor_id = app_user_id());

drop policy if exists tests_student_or_staff_select on tests;
create policy tests_student_or_staff_select on tests
    for select using (app_is_staff() or is_published = true);

drop policy if exists tests_staff_write on tests;
create policy tests_staff_write on tests
    for all using (app_user_role() = 'admin' or created_by = app_user_id())
    with check (app_user_role() = 'admin' or created_by = app_user_id());

drop policy if exists questions_visible_with_test on questions;
create policy questions_visible_with_test on questions
    for select using (
        exists (
            select 1
            from tests
            where tests.id = questions.test_id
              and (tests.is_published = true or app_is_staff())
        )
    );

drop policy if exists questions_staff_write on questions;
create policy questions_staff_write on questions
    for all using (app_is_staff()) with check (app_is_staff());

drop policy if exists sessions_self_or_staff_access on practice_sessions;
create policy sessions_self_or_staff_access on practice_sessions
    for all using (
        app_is_staff()
        or exists (
            select 1
            from students
            where students.id = practice_sessions.student_id
              and students.user_id = app_user_id()
        )
    )
    with check (
        app_is_staff()
        or exists (
            select 1
            from students
            where students.id = practice_sessions.student_id
              and students.user_id = app_user_id()
        )
    );

drop policy if exists responses_self_or_staff_access on responses;
create policy responses_self_or_staff_access on responses
    for all using (
        app_is_staff()
        or exists (
            select 1
            from practice_sessions
            join students on students.id = practice_sessions.student_id
            where practice_sessions.id = responses.session_id
              and students.user_id = app_user_id()
        )
    )
    with check (
        app_is_staff()
        or exists (
            select 1
            from practice_sessions
            join students on students.id = practice_sessions.student_id
            where practice_sessions.id = responses.session_id
              and students.user_id = app_user_id()
        )
    );

drop policy if exists scores_self_or_staff_select on scores;
create policy scores_self_or_staff_select on scores
    for select using (
        app_is_staff()
        or exists (
            select 1
            from students
            where students.id = scores.student_id
              and students.user_id = app_user_id()
        )
    );

drop policy if exists scores_staff_insert on scores;
create policy scores_staff_insert on scores
    for insert with check (app_is_staff());
