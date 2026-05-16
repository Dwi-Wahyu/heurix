import { relations } from 'drizzle-orm';
import {
	pgTable,
	pgEnum,
	text,
	timestamp,
	boolean,
	integer,
	real,
	jsonb,
	index,
	uniqueIndex
} from 'drizzle-orm/pg-core';

// ============================================================
// RE-EXPORT AUTH SCHEMA
// ============================================================
export { user, session, account, verification } from './auth.schema';
import { user } from './auth.schema';

// ============================================================
// ENUMS
// ============================================================

export const interviewTrackEnum = pgEnum('interview_track', [
	'corporate', // Wawancara Korporat Swasta (BEI)
	'military', // Akmil / Akpol
	'civil_service', // CPNS Umum
	'stan' // PKN STAN
]);

export const sessionStatusEnum = pgEnum('session_status', [
	'waiting', // Belum mulai
	'active', // Sedang berlangsung
	'completed', // Selesai normal
	'abandoned' // Ditinggal / timeout
]);

export const personaTypeEnum = pgEnum('persona_type', [
	'friendly', // Ramah & suportif
	'formal', // Formal & netral
	'intimidating' // Formal ketat / tekan
]);

export const difficultyEnum = pgEnum('difficulty', ['easy', 'medium', 'hard', 'extreme']);

// ============================================================
// MASTER DATA — Institusi & Posisi
// ============================================================

export const masterInstitution = pgTable('master_institution', {
	id: text('id').primaryKey(),
	name: text('name').notNull(),
	track: interviewTrackEnum('track').notNull(),
	defaultAvatarId: text('default_avatar_id').references(() => interviewAvatar.id),
	logoUrl: text('logo_url'),
	description: text('description'), // Penjelasan singkat
	llmContext: text('llm_context'), // Konteks khusus untuk LLM (budaya, nilai, dll)
	createdAt: timestamp('created_at').defaultNow().notNull(),
	updatedAt: timestamp('updated_at')
		.defaultNow()
		.$onUpdate(() => new Date())
		.notNull()
});

export const masterPosition = pgTable('master_position', {
	id: text('id').primaryKey(),
	institutionId: text('institution_id')
		.notNull()
		.references(() => masterInstitution.id, { onDelete: 'cascade' }),
	name: text('name').notNull(),
	description: text('description'),
	llmContext: text('llm_context'), // Konteks khusus posisi (hard skills, soft skills)
	isActive: boolean('is_active').default(true).notNull(),
	createdAt: timestamp('created_at').defaultNow().notNull(),
	updatedAt: timestamp('updated_at')
		.defaultNow()
		.$onUpdate(() => new Date())
		.notNull()
});

// ============================================================
// USER PROFILE — Ekstensi data pengguna Heurix
// ============================================================

export const userProfile = pgTable('user_profile', {
	id: text('id').primaryKey(),
	userId: text('user_id')
		.notNull()
		.unique()
		.references(() => user.id, { onDelete: 'cascade' }),

	// Profil karir
	targetPositionId: text('target_position_id').references(() => masterPosition.id, {
		onDelete: 'set null'
	}),
	targetInstitutionId: text('target_institution_id').references(() => masterInstitution.id, {
		onDelete: 'set null'
	}),
	preferredTrack: interviewTrackEnum('preferred_track'),

	// Statistik agregat (diupdate setiap sesi selesai)
	totalSessions: integer('total_sessions').default(0).notNull(),
	totalMinutesPracticed: integer('total_minutes_practiced').default(0).notNull(),
	avgOverallScore: real('avg_overall_score'), // 0.0 - 100.0

	// Plan
	isPremium: boolean('is_premium').default(false).notNull(),
	premiumExpiresAt: timestamp('premium_expires_at'),

	createdAt: timestamp('created_at').defaultNow().notNull(),
	updatedAt: timestamp('updated_at')
		.defaultNow()
		.$onUpdate(() => new Date())
		.notNull()
});

// ============================================================
// INTERVIEW SESSION — Satu sesi simulasi wawancara
// ============================================================

export const interviewSession = pgTable(
	'interview_session',
	{
		id: text('id').primaryKey(),
		userId: text('user_id')
			.notNull()
			.references(() => user.id, { onDelete: 'cascade' }),

		// Konfigurasi sesi
		track: interviewTrackEnum('track').notNull(),
		difficulty: difficultyEnum('difficulty').default('medium').notNull(),
		avatarId: text('avatar_id').notNull(), // FK ke interview_avatar

		// Konteks dinamis untuk LLM
		sessionContext: text('session_context'), // Info tambahan (e.g. CV singkat, info lowongan)

		// Status & timing
		status: sessionStatusEnum('status').default('waiting').notNull(),
		startedAt: timestamp('started_at'),
		completedAt: timestamp('completed_at'),
		durationSeconds: integer('duration_seconds'), // total durasi aktual

		// Persona state akhir
		currentPersona: personaTypeEnum('current_persona').default('friendly'),
		personaShiftCount: integer('persona_shift_count').default(0).notNull(),

		// Skor akhir (diisi setelah sesi selesai)
		overallScore: real('overall_score'), // 0–100
		communicationScore: real('communication_score'), // 0–100
		consistencyScore: real('consistency_score'), // 0–100
		confidenceScore: real('confidence_score'), // 0–100
		facialExpressionScore: real('facial_expression_score'), // 0–100
		eyeContactScore: real('eye_contact_score'), // 0–100
		faceMetrics: jsonb('face_metrics'), // Array of { smileScore, isLookingAtCamera, timestamp }

		createdAt: timestamp('created_at').defaultNow().notNull(),
		updatedAt: timestamp('updated_at')
			.defaultNow()
			.$onUpdate(() => new Date())
			.notNull()
	},
	(table) => [
		index('interview_session_userId_idx').on(table.userId),
		index('interview_session_status_idx').on(table.status),
		index('interview_session_track_idx').on(table.track)
	]
);

// ============================================================
// SESSION TURN — Satu giliran tanya-jawab dalam sesi
// ============================================================

export const sessionTurn = pgTable(
	'session_turn',
	{
		id: text('id').primaryKey(),
		sessionId: text('session_id')
			.notNull()
			.references(() => interviewSession.id, { onDelete: 'cascade' }),

		turnNumber: integer('turn_number').notNull(), // Urutan dalam sesi (1, 2, 3, ...)

		// Pertanyaan dari Avatar
		questionText: text('question_text').notNull(),
		questionAudioUrl: text('question_audio_url'), // URL file .wav Kokoro TTS
		visemeDataUrl: text('viseme_data_url'), // URL JSON data viseme lip-sync
		personaAtTurn: personaTypeEnum('persona_at_turn').notNull(),

		// Jawaban Kandidat
		answerTranscript: text('answer_transcript'), // Hasil Whisper STT
		answerAudioUrl: text('answer_audio_url'), // Rekaman kandidat (opsional)
		answerDurationSeconds: integer('answer_duration_seconds'),

		// Metrik objektif per turn
		fillerWordCount: integer('filler_word_count').default(0),
		fillerWords: jsonb('filler_words'), // { "em": 3, "anu": 1, "ya": 5 }
		wordsPerMinute: real('words_per_minute'),
		pauseCount: integer('pause_count').default(0),

		// Analisis AI per turn
		answerQuality: real('answer_quality'), // 0–100, dinilai LLM
		isPersonaShiftTurn: boolean('is_persona_shift_turn').default(false),
		llmAnalysis: text('llm_analysis'), // Catatan internal LLM untuk probing

		createdAt: timestamp('created_at').defaultNow().notNull()
	},
	(table) => [
		index('session_turn_sessionId_idx').on(table.sessionId),
		uniqueIndex('session_turn_session_number_idx').on(table.sessionId, table.turnNumber)
	]
);

// ============================================================
// SESSION REPORT — Laporan analitik pasca-sesi
// ============================================================

export const sessionReport = pgTable(
	'session_report',
	{
		id: text('id').primaryKey(),
		sessionId: text('session_id')
			.notNull()
			.unique()
			.references(() => interviewSession.id, { onDelete: 'cascade' }),
		userId: text('user_id')
			.notNull()
			.references(() => user.id, { onDelete: 'cascade' }),

		// Ringkasan metrik komunikasi
		totalFillerWords: integer('total_filler_words').default(0),
		fillerWordBreakdown: jsonb('filler_word_breakdown'), // { "em": 10, "anu": 3 }
		avgWordsPerMinute: real('avg_words_per_minute'),
		avgPauseDuration: real('avg_pause_duration'), // detik
		totalTurns: integer('total_turns').notNull(),

		// Skor dimensi
		overallScore: real('overall_score').notNull(),
		communicationScore: real('communication_score').notNull(),
		consistencyScore: real('consistency_score').notNull(),
		confidenceScore: real('confidence_score').notNull(),
		stressResistanceScore: real('stress_resistance_score'), // khusus jika ada Persona Shift

		// New 8 dimensions
		articulationScore: real('articulation_score'),
		intonationScore: real('intonation_score'),
		pacingScore: real('pacing_score'),
		fillerWordsScore: real('filler_words_score'),
		sentenceStructureScore: real('sentence_structure_score'),
		answerCompletenessScore: real('answer_completeness_score'),

		// Skor tambahan non-verbal
		facialExpressionScore: real('facial_expression_score'),
		eyeContactScore: real('eye_contact_score'),

		// Rekomendasi
		strengths: jsonb('strengths'), // string[]
		weaknesses: jsonb('weaknesses'), // string[]
		recommendations: jsonb('recommendations'), // string[]

		// Full narasi evaluasi dari LLM
		evaluationNarrative: text('evaluation_narrative'),

		// Feedbacks tambahan
		articulationFeedback: text('articulation_feedback'),
		intonationFeedback: text('intonation_feedback'),
		pacingFeedback: text('pacing_feedback'),
		fillerWordsFeedback: text('filler_words_feedback'),
		sentenceStructureFeedback: text('sentence_structure_feedback'),
		answerCompletenessFeedback: text('answer_completeness_feedback'),
		consistencyFeedback: text('consistency_feedback'),
		confidenceFeedback: text('confidence_feedback'),
		facialExpressionFeedback: text('facial_expression_feedback'),
		eyeContactFeedback: text('eye_contact_feedback'),

		generatedAt: timestamp('generated_at').defaultNow().notNull()
	},
	(table) => [index('session_report_userId_idx').on(table.userId)]
);

// ============================================================
// INTERVIEW AVATAR — Data avatar pewawancara
// ============================================================

export const interviewAvatar = pgTable('interview_avatar', {
	id: text('id').primaryKey(),

	name: text('name').notNull(), // "Pak Budi", "Kolonel Ahmad"
	description: text('description'),
	track: interviewTrackEnum('track').notNull(),
	glbUrl: text('glb_url').notNull(), // URL model .glb
	backgroundPath: text('background_path'),
	thumbnailUrl: text('thumbnail_url'),

	// Konfigurasi TTS per persona
	ttsVoiceId: text('tts_voice_id').notNull(), // ID voice Kokoro
	ttsFriendlyParams: jsonb('tts_friendly_params'), // { speed: 1.0, pitch: 1.0 }
	ttsFormalParams: jsonb('tts_formal_params'), // { speed: 0.9, pitch: 0.95 }
	ttsIntimidatingParams: jsonb('tts_intimidating_params'), // { speed: 0.85, pitch: 0.9 }

	// Sistem prompt LLM per persona
	promptFriendly: text('prompt_friendly'),
	promptFormal: text('prompt_formal'),
	promptIntimidating: text('prompt_intimidating'),

	// Konfigurasi Kamera (untuk positioning wajah)
	// format: { headHeightRatio: 0.82, distanceOffset: 1.0, lookAtOffset: 0.05 }
	cameraConfig: jsonb('camera_config'),

	isActive: boolean('is_active').default(true).notNull(),
	createdAt: timestamp('created_at').defaultNow().notNull()
});

// ============================================================
// ============================================================
// QUESTION BANK — Bank soal per track (opsional, untuk caching)
// ============================================================

export const questionBank = pgTable(
	'question_bank',
	{
		id: text('id').primaryKey(),
		track: interviewTrackEnum('track').notNull(),
		difficulty: difficultyEnum('difficulty').notNull(),
		category: text('category').notNull(), // "mental_ideologi", "behavioral", "stress"
		questionText: text('question_text').notNull(),

		// Links ke master data
		institutionId: text('institution_id').references(() => masterInstitution.id),
		positionId: text('position_id').references(() => masterPosition.id),

		isPersonaShiftTrigger: boolean('is_persona_shift_trigger').default(false),
		usageCount: integer('usage_count').default(0).notNull(),
		createdAt: timestamp('created_at').defaultNow().notNull()
	},
	(table) => [
		index('question_bank_track_difficulty_idx').on(table.track, table.difficulty),
		index('question_bank_institution_idx').on(table.institutionId),
		index('question_bank_position_idx').on(table.positionId)
	]
);

// ============================================================
// RELATIONS
// ============================================================

export const masterInstitutionRelations = relations(masterInstitution, ({ one, many }) => ({
	positions: many(masterPosition),
	userProfiles: many(userProfile),
	questions: many(questionBank),
	defaultAvatar: one(interviewAvatar, {
		fields: [masterInstitution.defaultAvatarId],
		references: [interviewAvatar.id]
	})
}));

export const masterPositionRelations = relations(masterPosition, ({ one, many }) => ({
	institution: one(masterInstitution, {
		fields: [masterPosition.institutionId],
		references: [masterInstitution.id]
	}),
	userProfiles: many(userProfile),
	questions: many(questionBank)
}));

export const userProfileRelations = relations(userProfile, ({ one }) => ({
	user: one(user, { fields: [userProfile.userId], references: [user.id] }),
	targetPosition: one(masterPosition, {
		fields: [userProfile.targetPositionId],
		references: [masterPosition.id]
	}),
	targetInstitution: one(masterInstitution, {
		fields: [userProfile.targetInstitutionId],
		references: [masterInstitution.id]
	})
}));

export const interviewSessionRelations = relations(interviewSession, ({ one, many }) => ({
	user: one(user, { fields: [interviewSession.userId], references: [user.id] }),
	avatar: one(interviewAvatar, {
		fields: [interviewSession.avatarId],
		references: [interviewAvatar.id]
	}),
	turns: many(sessionTurn),
	report: one(sessionReport, {
		fields: [interviewSession.id],
		references: [sessionReport.sessionId]
	})
}));

export const sessionTurnRelations = relations(sessionTurn, ({ one }) => ({
	session: one(interviewSession, {
		fields: [sessionTurn.sessionId],
		references: [interviewSession.id]
	})
}));

export const sessionReportRelations = relations(sessionReport, ({ one }) => ({
	session: one(interviewSession, {
		fields: [sessionReport.sessionId],
		references: [interviewSession.id]
	}),
	user: one(user, { fields: [sessionReport.userId], references: [user.id] })
}));

export const interviewAvatarRelations = relations(interviewAvatar, ({ many }) => ({
	sessions: many(interviewSession)
}));

export const questionBankRelations = relations(questionBank, ({ one }) => ({
	institution: one(masterInstitution, {
		fields: [questionBank.institutionId],
		references: [masterInstitution.id]
	}),
	position: one(masterPosition, {
		fields: [questionBank.positionId],
		references: [masterPosition.id]
	})
}));

export * from './auth.schema';
