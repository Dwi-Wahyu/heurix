CREATE TYPE "public"."difficulty" AS ENUM('easy', 'medium', 'hard', 'extreme');--> statement-breakpoint
CREATE TYPE "public"."interview_track" AS ENUM('corporate', 'military', 'civil_service', 'stan');--> statement-breakpoint
CREATE TYPE "public"."persona_type" AS ENUM('friendly', 'formal', 'intimidating');--> statement-breakpoint
CREATE TYPE "public"."session_status" AS ENUM('waiting', 'active', 'completed', 'abandoned');--> statement-breakpoint
CREATE TABLE "interview_avatar" (
	"id" text PRIMARY KEY NOT NULL,
	"name" text NOT NULL,
	"track" "interview_track" NOT NULL,
	"glb_url" text NOT NULL,
	"thumbnail_url" text,
	"tts_voice_id" text NOT NULL,
	"tts_friendly_params" jsonb,
	"tts_formal_params" jsonb,
	"tts_intimidating_params" jsonb,
	"prompt_friendly" text,
	"prompt_formal" text,
	"prompt_intimidating" text,
	"is_active" boolean DEFAULT true NOT NULL,
	"created_at" timestamp DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "interview_session" (
	"id" text PRIMARY KEY NOT NULL,
	"user_id" text NOT NULL,
	"track" "interview_track" NOT NULL,
	"difficulty" "difficulty" DEFAULT 'medium' NOT NULL,
	"avatar_id" text NOT NULL,
	"session_context" text,
	"status" "session_status" DEFAULT 'waiting' NOT NULL,
	"started_at" timestamp,
	"completed_at" timestamp,
	"duration_seconds" integer,
	"current_persona" "persona_type" DEFAULT 'friendly',
	"persona_shift_count" integer DEFAULT 0 NOT NULL,
	"overall_score" real,
	"communication_score" real,
	"consistency_score" real,
	"confidence_score" real,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "master_institution" (
	"id" text PRIMARY KEY NOT NULL,
	"name" text NOT NULL,
	"logo_url" text,
	"description" text,
	"llm_context" text,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "master_position" (
	"id" text PRIMARY KEY NOT NULL,
	"institution_id" text NOT NULL,
	"name" text NOT NULL,
	"description" text,
	"llm_context" text,
	"is_active" boolean DEFAULT true NOT NULL,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "question_bank" (
	"id" text PRIMARY KEY NOT NULL,
	"track" "interview_track" NOT NULL,
	"difficulty" "difficulty" NOT NULL,
	"category" text NOT NULL,
	"question_text" text NOT NULL,
	"institution_id" text,
	"position_id" text,
	"is_persona_shift_trigger" boolean DEFAULT false,
	"usage_count" integer DEFAULT 0 NOT NULL,
	"created_at" timestamp DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "session_report" (
	"id" text PRIMARY KEY NOT NULL,
	"session_id" text NOT NULL,
	"user_id" text NOT NULL,
	"total_filler_words" integer DEFAULT 0,
	"filler_word_breakdown" jsonb,
	"avg_words_per_minute" real,
	"avg_pause_duration" real,
	"total_turns" integer NOT NULL,
	"overall_score" real NOT NULL,
	"communication_score" real NOT NULL,
	"consistency_score" real NOT NULL,
	"confidence_score" real NOT NULL,
	"stress_resistance_score" real,
	"strengths" jsonb,
	"weaknesses" jsonb,
	"recommendations" jsonb,
	"evaluation_narrative" text,
	"generated_at" timestamp DEFAULT now() NOT NULL,
	CONSTRAINT "session_report_session_id_unique" UNIQUE("session_id")
);
--> statement-breakpoint
CREATE TABLE "session_turn" (
	"id" text PRIMARY KEY NOT NULL,
	"session_id" text NOT NULL,
	"turn_number" integer NOT NULL,
	"question_text" text NOT NULL,
	"question_audio_url" text,
	"viseme_data_url" text,
	"persona_at_turn" "persona_type" NOT NULL,
	"answer_transcript" text,
	"answer_audio_url" text,
	"answer_duration_seconds" integer,
	"filler_word_count" integer DEFAULT 0,
	"filler_words" jsonb,
	"words_per_minute" real,
	"pause_count" integer DEFAULT 0,
	"answer_quality" real,
	"is_persona_shift_turn" boolean DEFAULT false,
	"llm_analysis" text,
	"created_at" timestamp DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "user_profile" (
	"id" text PRIMARY KEY NOT NULL,
	"user_id" text NOT NULL,
	"target_position_id" text,
	"target_institution_id" text,
	"preferred_track" "interview_track",
	"total_sessions" integer DEFAULT 0 NOT NULL,
	"total_minutes_practiced" integer DEFAULT 0 NOT NULL,
	"avg_overall_score" real,
	"is_premium" boolean DEFAULT false NOT NULL,
	"premium_expires_at" timestamp,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL,
	CONSTRAINT "user_profile_user_id_unique" UNIQUE("user_id")
);
--> statement-breakpoint
DROP TABLE "task" CASCADE;--> statement-breakpoint
ALTER TABLE "interview_session" ADD CONSTRAINT "interview_session_user_id_user_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."user"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "master_position" ADD CONSTRAINT "master_position_institution_id_master_institution_id_fk" FOREIGN KEY ("institution_id") REFERENCES "public"."master_institution"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "question_bank" ADD CONSTRAINT "question_bank_institution_id_master_institution_id_fk" FOREIGN KEY ("institution_id") REFERENCES "public"."master_institution"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "question_bank" ADD CONSTRAINT "question_bank_position_id_master_position_id_fk" FOREIGN KEY ("position_id") REFERENCES "public"."master_position"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "session_report" ADD CONSTRAINT "session_report_session_id_interview_session_id_fk" FOREIGN KEY ("session_id") REFERENCES "public"."interview_session"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "session_report" ADD CONSTRAINT "session_report_user_id_user_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."user"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "session_turn" ADD CONSTRAINT "session_turn_session_id_interview_session_id_fk" FOREIGN KEY ("session_id") REFERENCES "public"."interview_session"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "user_profile" ADD CONSTRAINT "user_profile_user_id_user_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."user"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "user_profile" ADD CONSTRAINT "user_profile_target_position_id_master_position_id_fk" FOREIGN KEY ("target_position_id") REFERENCES "public"."master_position"("id") ON DELETE set null ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "user_profile" ADD CONSTRAINT "user_profile_target_institution_id_master_institution_id_fk" FOREIGN KEY ("target_institution_id") REFERENCES "public"."master_institution"("id") ON DELETE set null ON UPDATE no action;--> statement-breakpoint
CREATE INDEX "interview_session_userId_idx" ON "interview_session" USING btree ("user_id");--> statement-breakpoint
CREATE INDEX "interview_session_status_idx" ON "interview_session" USING btree ("status");--> statement-breakpoint
CREATE INDEX "interview_session_track_idx" ON "interview_session" USING btree ("track");--> statement-breakpoint
CREATE INDEX "question_bank_track_difficulty_idx" ON "question_bank" USING btree ("track","difficulty");--> statement-breakpoint
CREATE INDEX "question_bank_institution_idx" ON "question_bank" USING btree ("institution_id");--> statement-breakpoint
CREATE INDEX "question_bank_position_idx" ON "question_bank" USING btree ("position_id");--> statement-breakpoint
CREATE INDEX "session_report_userId_idx" ON "session_report" USING btree ("user_id");--> statement-breakpoint
CREATE INDEX "session_turn_sessionId_idx" ON "session_turn" USING btree ("session_id");--> statement-breakpoint
CREATE UNIQUE INDEX "session_turn_session_number_idx" ON "session_turn" USING btree ("session_id","turn_number");