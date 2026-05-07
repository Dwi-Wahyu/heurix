ALTER TABLE "session_report" ADD COLUMN "articulation_score" real;--> statement-breakpoint
ALTER TABLE "session_report" ADD COLUMN "intonation_score" real;--> statement-breakpoint
ALTER TABLE "session_report" ADD COLUMN "pacing_score" real;--> statement-breakpoint
ALTER TABLE "session_report" ADD COLUMN "filler_words_score" real;--> statement-breakpoint
ALTER TABLE "session_report" ADD COLUMN "sentence_structure_score" real;--> statement-breakpoint
ALTER TABLE "session_report" ADD COLUMN "answer_completeness_score" real;--> statement-breakpoint
ALTER TABLE "session_report" ADD COLUMN "articulation_feedback" text;--> statement-breakpoint
ALTER TABLE "session_report" ADD COLUMN "intonation_feedback" text;--> statement-breakpoint
ALTER TABLE "session_report" ADD COLUMN "pacing_feedback" text;--> statement-breakpoint
ALTER TABLE "session_report" ADD COLUMN "filler_words_feedback" text;--> statement-breakpoint
ALTER TABLE "session_report" ADD COLUMN "sentence_structure_feedback" text;--> statement-breakpoint
ALTER TABLE "session_report" ADD COLUMN "answer_completeness_feedback" text;--> statement-breakpoint
ALTER TABLE "session_report" ADD COLUMN "consistency_feedback" text;--> statement-breakpoint
ALTER TABLE "session_report" ADD COLUMN "confidence_feedback" text;