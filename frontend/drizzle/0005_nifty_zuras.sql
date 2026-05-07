ALTER TABLE "interview_session" ADD COLUMN "facial_expression_score" real;--> statement-breakpoint
ALTER TABLE "interview_session" ADD COLUMN "eye_contact_score" real;--> statement-breakpoint
ALTER TABLE "interview_session" ADD COLUMN "face_metrics" jsonb;--> statement-breakpoint
ALTER TABLE "session_report" ADD COLUMN "facial_expression_score" real;--> statement-breakpoint
ALTER TABLE "session_report" ADD COLUMN "eye_contact_score" real;--> statement-breakpoint
ALTER TABLE "session_report" ADD COLUMN "facial_expression_feedback" text;--> statement-breakpoint
ALTER TABLE "session_report" ADD COLUMN "eye_contact_feedback" text;