-- Align existing PostgreSQL / Supabase databases with current SQLAlchemy models.
-- Error fixed: undefined column responses.student_id, scores.session_id
--
-- Apply in Supabase: SQL Editor → New query → paste → Run.
-- Safe to re-run: uses IF NOT EXISTS / guarded constraints.

-- ---------------------------------------------------------------------------
-- responses.student_id
-- ---------------------------------------------------------------------------
ALTER TABLE responses ADD COLUMN IF NOT EXISTS student_id integer;

UPDATE responses r
SET student_id = ps.student_id
FROM practice_sessions ps
WHERE r.session_id = ps.id
  AND (r.student_id IS NULL);

-- Drop rows that cannot be linked (should not happen in normal use)
DELETE FROM responses r
WHERE r.student_id IS NULL;

ALTER TABLE responses ALTER COLUMN student_id SET NOT NULL;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'responses_student_id_fkey'
  ) THEN
    ALTER TABLE responses
      ADD CONSTRAINT responses_student_id_fkey
      FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE;
  END IF;
END $$;

CREATE INDEX IF NOT EXISTS ix_responses_student_id ON responses (student_id);

-- ---------------------------------------------------------------------------
-- scores.session_id (nullable: older score rows may have no session)
-- ---------------------------------------------------------------------------
ALTER TABLE scores ADD COLUMN IF NOT EXISTS session_id integer;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'scores_session_id_fkey'
  ) THEN
    ALTER TABLE scores
      ADD CONSTRAINT scores_session_id_fkey
      FOREIGN KEY (session_id) REFERENCES practice_sessions (id) ON DELETE CASCADE;
  END IF;
END $$;

CREATE INDEX IF NOT EXISTS ix_scores_session_id ON scores (session_id);
