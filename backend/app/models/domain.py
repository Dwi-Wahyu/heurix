import enum
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Index, JSON, func, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base

class InterviewTrack(str, enum.Enum):
    corporate = "corporate"
    military = "military"
    civil_service = "civil_service"
    stan = "stan"

class SessionStatus(str, enum.Enum):
    waiting = "waiting"
    active = "active"
    completed = "completed"
    abandoned = "abandoned"

class PersonaType(str, enum.Enum):
    friendly = "friendly"
    formal = "formal"
    intimidating = "intimidating"

class Difficulty(str, enum.Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"
    extreme = "extreme"

class MasterInstitution(Base):
    __tablename__ = "master_institution"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    track = Column(Enum(InterviewTrack), nullable=False)
    logoUrl = Column("logo_url", String)
    description = Column(String)
    llmContext = Column("llm_context", String)
    createdAt = Column("created_at", DateTime, default=func.now(), nullable=False)
    updatedAt = Column("updated_at", DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    positions = relationship("MasterPosition", back_populates="institution", cascade="all, delete-orphan")
    userProfiles = relationship("UserProfile", back_populates="targetInstitution")
    questions = relationship("QuestionBank", back_populates="institution")

class MasterPosition(Base):
    __tablename__ = "master_position"

    id = Column(String, primary_key=True)
    institutionId = Column("institution_id", String, ForeignKey("master_institution.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    llmContext = Column("llm_context", String)
    isActive = Column("is_active", Boolean, default=True, nullable=False)
    createdAt = Column("created_at", DateTime, default=func.now(), nullable=False)
    updatedAt = Column("updated_at", DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    institution = relationship("MasterInstitution", back_populates="positions")
    userProfiles = relationship("UserProfile", back_populates="targetPosition")
    questions = relationship("QuestionBank", back_populates="position")

class UserProfile(Base):
    __tablename__ = "user_profile"

    id = Column(String, primary_key=True)
    userId = Column("user_id", String, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, unique=True)
    targetPositionId = Column("target_position_id", String, ForeignKey("master_position.id", ondelete="SET NULL"))
    targetInstitutionId = Column("target_institution_id", String, ForeignKey("master_institution.id", ondelete="SET NULL"))
    preferredTrack = Column("preferred_track", Enum(InterviewTrack))
    totalSessions = Column("total_sessions", Integer, default=0, nullable=False)
    totalMinutesPracticed = Column("total_minutes_practiced", Integer, default=0, nullable=False)
    avgOverallScore = Column("avg_overall_score", Float)
    isPremium = Column("is_premium", Boolean, default=False, nullable=False)
    premiumExpiresAt = Column("premium_expires_at", DateTime)
    createdAt = Column("created_at", DateTime, default=func.now(), nullable=False)
    updatedAt = Column("updated_at", DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="profile")
    targetPosition = relationship("MasterPosition", back_populates="userProfiles")
    targetInstitution = relationship("MasterInstitution", back_populates="userProfiles")

class InterviewSession(Base):
    __tablename__ = "interview_session"

    id = Column(String, primary_key=True)
    userId = Column("user_id", String, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    track = Column(Enum(InterviewTrack), nullable=False)
    difficulty = Column(Enum(Difficulty), default=Difficulty.medium, nullable=False)
    avatarId = Column("avatar_id", String, ForeignKey("interview_avatar.id"), nullable=False)
    sessionContext = Column("session_context", String)
    status = Column(Enum(SessionStatus), default=SessionStatus.waiting, nullable=False)
    startedAt = Column("started_at", DateTime)
    completedAt = Column("completed_at", DateTime)
    durationSeconds = Column("duration_seconds", Integer)
    currentPersona = Column("current_persona", Enum(PersonaType), default=PersonaType.friendly)
    personaShiftCount = Column("persona_shift_count", Integer, default=0, nullable=False)
    overallScore = Column("overall_score", Float)
    communicationScore = Column("communication_score", Float)
    consistencyScore = Column("consistency_score", Float)
    confidenceScore = Column("confidence_score", Float)
    createdAt = Column("created_at", DateTime, default=func.now(), nullable=False)
    updatedAt = Column("updated_at", DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="interview_sessions")
    avatar = relationship("InterviewAvatar", back_populates="sessions")
    turns = relationship("SessionTurn", back_populates="session", cascade="all, delete-orphan")
    report = relationship("SessionReport", back_populates="session", uselist=False)

    __table_args__ = (
        Index("interview_session_userId_idx", "user_id"),
        Index("interview_session_status_idx", "status"),
        Index("interview_session_track_idx", "track"),
    )

class SessionTurn(Base):
    __tablename__ = "session_turn"

    id = Column(String, primary_key=True)
    sessionId = Column("session_id", String, ForeignKey("interview_session.id", ondelete="CASCADE"), nullable=False)
    turnNumber = Column("turn_number", Integer, nullable=False)
    questionText = Column("question_text", String, nullable=False)
    questionAudioUrl = Column("question_audio_url", String)
    visemeDataUrl = Column("viseme_data_url", String)
    personaAtTurn = Column("persona_at_turn", Enum(PersonaType), nullable=False)
    answerTranscript = Column("answer_transcript", String)
    answerAudioUrl = Column("answer_audio_url", String)
    answerDurationSeconds = Column("answer_duration_seconds", Integer)
    fillerWordCount = Column("filler_word_count", Integer, default=0)
    fillerWords = Column("filler_words", JSON)
    wordsPerMinute = Column("words_per_minute", Float)
    pauseCount = Column("pause_count", Integer, default=0)
    answerQuality = Column("answer_quality", Float)
    isPersonaShiftTurn = Column("is_persona_shift_turn", Boolean, default=False)
    llmAnalysis = Column("llm_analysis", String)
    createdAt = Column("created_at", DateTime, default=func.now())

    session = relationship("InterviewSession", back_populates="turns")

    __table_args__ = (
        Index("session_turn_sessionId_idx", "session_id"),
        Index("session_turn_session_number_idx", "session_id", "turn_number", unique=True),
    )

class SessionReport(Base):
    __tablename__ = "session_report"

    id = Column(String, primary_key=True)
    sessionId = Column("session_id", String, ForeignKey("interview_session.id", ondelete="CASCADE"), nullable=False, unique=True)
    userId = Column("user_id", String, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    totalFillerWords = Column("total_filler_words", Integer, default=0)
    fillerWordBreakdown = Column("filler_word_breakdown", JSON)
    avgWordsPerMinute = Column("avg_words_per_minute", Float)
    avgPauseDuration = Column("avg_pause_duration", Float)
    totalTurns = Column("total_turns", Integer, nullable=False)
    overallScore = Column("overall_score", Float, nullable=False)
    communicationScore = Column("communication_score", Float, nullable=False)
    consistencyScore = Column("consistency_score", Float, nullable=False)
    confidenceScore = Column("confidence_score", Float, nullable=False)
    stressResistanceScore = Column("stress_resistance_score", Float)
    strengths = Column(JSON)
    weaknesses = Column(JSON)
    recommendations = Column(JSON)
    evaluationNarrative = Column("evaluation_narrative", String)
    generatedAt = Column("generated_at", DateTime, default=func.now(), nullable=False)

    session = relationship("InterviewSession", back_populates="report")
    user = relationship("User", back_populates="reports")

    __table_args__ = (
        Index("session_report_userId_idx", "user_id"),
    )

class InterviewAvatar(Base):
    __tablename__ = "interview_avatar"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    track = Column(Enum(InterviewTrack), nullable=False)
    glbUrl = Column("glb_url", String, nullable=False)
    thumbnailUrl = Column("thumbnail_url", String)
    ttsVoiceId = Column("tts_voice_id", String, nullable=False)
    ttsFriendlyParams = Column("tts_friendly_params", JSON)
    ttsFormalParams = Column("tts_formal_params", JSON)
    ttsIntimidatingParams = Column("tts_intimidating_params", JSON)
    promptFriendly = Column("prompt_friendly", String)
    promptFormal = Column("prompt_formal", String)
    promptIntimidating = Column("prompt_intimidating", String)
    isActive = Column("is_active", Boolean, default=True, nullable=False)
    createdAt = Column("created_at", DateTime, default=func.now(), nullable=False)

    sessions = relationship("InterviewSession", back_populates="avatar")

class QuestionBank(Base):
    __tablename__ = "question_bank"

    id = Column(String, primary_key=True)
    track = Column(Enum(InterviewTrack), nullable=False)
    difficulty = Column(Enum(Difficulty), nullable=False)
    category = Column(String, nullable=False)
    questionText = Column("question_text", String, nullable=False)
    institutionId = Column("institution_id", String, ForeignKey("master_institution.id"))
    positionId = Column("position_id", String, ForeignKey("master_position.id"))
    isPersonaShiftTrigger = Column("is_persona_shift_trigger", Boolean, default=False)
    usageCount = Column("usage_count", Integer, default=0, nullable=False)
    createdAt = Column("created_at", DateTime, default=func.now(), nullable=False)

    institution = relationship("MasterInstitution", back_populates="questions")
    position = relationship("MasterPosition", back_populates="questions")

    __table_args__ = (
        Index("question_bank_track_difficulty_idx", "track", "difficulty"),
        Index("question_bank_institution_idx", "institution_id"),
        Index("question_bank_position_idx", "position_id"),
    )
