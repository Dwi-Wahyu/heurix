CREATE TYPE "public"."scenario_type" AS ENUM('friendly', 'grilling', 'stress_test');--> statement-breakpoint
ALTER TABLE "interview_session" ADD COLUMN "scenario" "scenario_type" DEFAULT 'friendly' NOT NULL;--> statement-breakpoint
ALTER TABLE "interview_session" ADD COLUMN "pressure_level" integer DEFAULT 1 NOT NULL;--> statement-breakpoint
ALTER TABLE "session_report" ADD COLUMN "sri_score" real;--> statement-breakpoint
ALTER TABLE "user_profile" ADD COLUMN "last_sri" real;--> statement-breakpoint
ALTER TABLE "user_profile" ADD COLUMN "sri_history" jsonb;--> statement-breakpoint
ALTER TABLE "user_profile" ADD COLUMN "next_pressure_level" integer DEFAULT 1 NOT NULL;--> statement-breakpoint
ALTER TABLE "user_profile" ADD COLUMN "weakness_tags" jsonb;