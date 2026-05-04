
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

create table if not exists users (
    id serial primary key,
    email varchar(255) not null unique,
    password_hash varchar(255) not null,
    full_name varchar(255),
    is_active boolean not null default true,
    is_verified boolean not null default false,
    role userrole not null default 'STUDENT',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    last_login timestamptz,
    bio text
);

create index if not exists ix_users_id on users (id);
create unique index if not exists ix_users_email on users (email);

create table if not exists cohorts (
    id serial primary key,
    name varchar(255) not null,
    description text,
    instructor_id integer not null references users(id),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index if not exists ix_cohorts_id on cohorts (id);
create index if not exists ix_cohorts_name on cohorts (name);

create table if not exists students (
    id serial primary key,
    user_id integer not null unique references users(id) on delete cascade,
    cohort_id integer references cohorts(id) on delete set null,
    grade_level varchar(50),
    school_name varchar(255),
    enrollment_date timestamptz not null default now(),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    bio text,
    profile_picture_url varchar(500)
);

create index if not exists ix_students_id on students (id);
create index if not exists ix_students_cohort_id on students (cohort_id);

create table if not exists tests (
    id serial primary key,
    title varchar(255) not null,
    description text,
    cohort_id integer references cohorts(id) on delete set null,
    created_by integer not null references users(id),
    test_type testtype not null default 'PRACTICE',
    subject varchar(100),
    duration_minutes integer,
    passing_score integer not null default 70,
    is_published boolean not null default false,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index if not exists ix_tests_id on tests (id);
create index if not exists ix_tests_title on tests (title);
create index if not exists ix_tests_cohort_id on tests (cohort_id);

create table if not exists questions (
    id serial primary key,
    test_id integer not null references tests(id) on delete cascade,
    question_text text not null,
    question_type questiontype not null default 'MULTIPLE_CHOICE',
    options jsonb,
    correct_answer text,
    explanation text,
    points integer not null default 1,
    "order" integer not null,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index if not exists ix_questions_id on questions (id);
create index if not exists ix_questions_test_id on questions (test_id);

create table if not exists practice_sessions (
    id serial primary key,
    student_id integer not null references students(id) on delete cascade,
    test_id integer not null references tests(id) on delete cascade,
    started_at timestamptz not null default now(),
    completed_at timestamptz,
    score double precision,
    ai_feedback text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index if not exists ix_practice_sessions_id on practice_sessions (id);
create index if not exists ix_practice_sessions_student_id on practice_sessions (student_id);
create index if not exists ix_practice_sessions_test_id on practice_sessions (test_id);
create index if not exists idx_student_test on practice_sessions (student_id, test_id);

create table if not exists responses (
    id serial primary key,
    session_id integer not null references practice_sessions(id) on delete cascade,
    question_id integer not null references questions(id) on delete cascade,
    student_id integer not null references students(id) on delete cascade,
    answer_text text not null,
    is_correct boolean,
    points_earned double precision,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    constraint unique_response_per_question unique (session_id, question_id)
);

create index if not exists ix_responses_id on responses (id);
create index if not exists ix_responses_session_id on responses (session_id);
create index if not exists ix_responses_question_id on responses (question_id);
create index if not exists ix_responses_student_id on responses (student_id);

create table if not exists scores (
    id serial primary key,
    student_id integer not null references students(id) on delete cascade,
    test_id integer not null references tests(id) on delete cascade,
    session_id integer references practice_sessions(id) on delete cascade,
    score double precision not null,
    max_points double precision not null,
    earned_points double precision not null,
    is_passed boolean,
    attempt_number integer not null default 1,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index if not exists ix_scores_id on scores (id);
create index if not exists ix_scores_student_id on scores (student_id);
create index if not exists ix_scores_test_id on scores (test_id);
create index if not exists ix_scores_session_id on scores (session_id);

create or replace function set_updated_at()
returns trigger as $$
begin
    new.updated_at = now();
    return new;
end;
$$ language plpgsql;

drop trigger if exists set_users_updated_at on users;
create trigger set_users_updated_at
before update on users
for each row execute function set_updated_at();

drop trigger if exists set_cohorts_updated_at on cohorts;
create trigger set_cohorts_updated_at
before update on cohorts
for each row execute function set_updated_at();

drop trigger if exists set_students_updated_at on students;
create trigger set_students_updated_at
before update on students
for each row execute function set_updated_at();

drop trigger if exists set_tests_updated_at on tests;
create trigger set_tests_updated_at
before update on tests
for each row execute function set_updated_at();

drop trigger if exists set_questions_updated_at on questions;
create trigger set_questions_updated_at
before update on questions
for each row execute function set_updated_at();

drop trigger if exists set_practice_sessions_updated_at on practice_sessions;
create trigger set_practice_sessions_updated_at
before update on practice_sessions
for each row execute function set_updated_at();

drop trigger if exists set_responses_updated_at on responses;
create trigger set_responses_updated_at
before update on responses
for each row execute function set_updated_at();

drop trigger if exists set_scores_updated_at on scores;
create trigger set_scores_updated_at
before update on scores
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

-- RLS: these policies assume the backend sets app.current_user_id and
-- app.current_user_role per transaction when connecting directly as an app user.
-- If only the FastAPI service role connects to Supabase, keep RLS enforcement in
-- the API layer or add SET LOCAL statements in the DB session middleware.

alter table users enable row level security;
alter table students enable row level security;
alter table cohorts enable row level security;
alter table tests enable row level security;
alter table questions enable row level security;
alter table practice_sessions enable row level security;
alter table responses enable row level security;
alter table scores enable row level security;

create policy users_self_or_staff_select on users
    for select using (
        app_is_staff()
        or id = app_user_id()
    );

create policy users_self_insert on users
    for insert with check (
        app_user_role() in ('service', 'admin')
        or (app_user_id() is null and role = 'STUDENT')
    );

create policy users_self_or_staff_update on users
    for update using (
        app_is_staff()
        or id = app_user_id()
    )
    with check (
        app_is_staff()
        or id = app_user_id()
    );

create policy students_self_or_staff_select on students
    for select using (
        app_is_staff()
        or user_id = app_user_id()
    );

create policy students_self_insert on students
    for insert with check (
        app_is_staff()
        or user_id = app_user_id()
    );

create policy students_self_update on students
    for update using (
        app_is_staff()
        or user_id = app_user_id()
    )
    with check (
        app_is_staff()
        or user_id = app_user_id()
    );

create policy cohorts_staff_access on cohorts
    for all using (
        app_user_role() = 'admin'
        or instructor_id = app_user_id()
    )
    with check (
        app_user_role() = 'admin'
        or instructor_id = app_user_id()
    );

create policy tests_student_or_staff_select on tests
    for select using (
        app_is_staff()
        or is_published = true
    );

create policy tests_staff_write on tests
    for all using (
        app_user_role() = 'admin'
        or created_by = app_user_id()
    )
    with check (
        app_user_role() = 'admin'
        or created_by = app_user_id()
    );

create policy questions_visible_with_test on questions
    for select using (
        exists (
            select 1
            from tests
            where tests.id = questions.test_id
              and (
                tests.is_published = true
                or app_is_staff()
              )
        )
    );

create policy questions_staff_write on questions
    for all using (
        app_is_staff()
    )
    with check (
        app_is_staff()
    );

create policy sessions_self_or_staff_access on practice_sessions
    for all using (
        app_is_staff()
        or exists (
            select 1 from students
            where students.id = practice_sessions.student_id
              and students.user_id = app_user_id()
        )
    )
    with check (
        app_is_staff()
        or exists (
            select 1 from students
            where students.id = practice_sessions.student_id
              and students.user_id = app_user_id()
        )
    );

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

create policy scores_self_or_staff_select on scores
    for select using (
        app_is_staff()
        or exists (
            select 1 from students
            where students.id = scores.student_id
              and students.user_id = app_user_id()
        )
    );

create policy scores_staff_insert on scores
    for insert with check (app_is_staff());
