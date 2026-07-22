-- ============================================================================
-- Migration: Adaptive Personalization Engine (APE)
-- Menambahkan kolom untuk Pilar 1 (Progresi Beban), Pilar 2 (Profil Kelemahan),
-- dan Pilar 3 (Kontrol Skenario Suasana).
--
-- Aman dijalankan pada database dengan data eksisting: kolom baru dibuat
-- nullable/dengan default dulu, lalu di-backfill, baru NOT NULL bila perlu.
-- Jika Anda memakai Drizzle Kit, jalankan `db:generate` lalu bandingkan hasilnya
-- dengan file ini sebelum `db:migrate` / `db:push`.
-- ============================================================================

BEGIN;

-- ── ENUM BARU: scenario ──────────────────────────────────────────────────
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'scenario_type') THEN
        CREATE TYPE scenario_type AS ENUM ('friendly', 'grilling', 'stress_test');
    END IF;
END$$;

-- ── user_profile: Pilar 1 & Pilar 2 ─────────────────────────────────────
ALTER TABLE user_profile
    ADD COLUMN IF NOT EXISTS last_sri real,
    ADD COLUMN IF NOT EXISTS sri_history jsonb,
    ADD COLUMN IF NOT EXISTS next_pressure_level integer NOT NULL DEFAULT 1,
    ADD COLUMN IF NOT EXISTS weakness_tags jsonb;

-- ── interview_session: Pilar 1 & Pilar 3 ────────────────────────────────
ALTER TABLE interview_session
    ADD COLUMN IF NOT EXISTS scenario scenario_type,
    ADD COLUMN IF NOT EXISTS pressure_level integer;

-- Backfill sesi lama: scenario -> 'friendly', pressure_level -> 1 (normal)
UPDATE interview_session
    SET scenario = 'friendly'
    WHERE scenario IS NULL;

UPDATE interview_session
    SET pressure_level = 1
    WHERE pressure_level IS NULL;

ALTER TABLE interview_session
    ALTER COLUMN scenario SET DEFAULT 'friendly',
    ALTER COLUMN scenario SET NOT NULL,
    ALTER COLUMN pressure_level SET DEFAULT 1,
    ALTER COLUMN pressure_level SET NOT NULL;

-- ── session_report: Pilar 1 (skor SRI terhitung, terpisah dari LLM stress score) ──
ALTER TABLE session_report
    ADD COLUMN IF NOT EXISTS sri_score real;

COMMIT;

-- ============================================================================
-- Catatan rollback (jalankan manual jika perlu membatalkan migrasi):
--
-- BEGIN;
-- ALTER TABLE session_report DROP COLUMN IF EXISTS sri_score;
-- ALTER TABLE interview_session DROP COLUMN IF EXISTS scenario;
-- ALTER TABLE interview_session DROP COLUMN IF EXISTS pressure_level;
-- ALTER TABLE user_profile DROP COLUMN IF EXISTS last_sri;
-- ALTER TABLE user_profile DROP COLUMN IF EXISTS sri_history;
-- ALTER TABLE user_profile DROP COLUMN IF EXISTS next_pressure_level;
-- ALTER TABLE user_profile DROP COLUMN IF EXISTS weakness_tags;
-- DROP TYPE IF EXISTS scenario_type;
-- COMMIT;
-- ============================================================================
