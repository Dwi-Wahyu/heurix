from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Index, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "user"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    emailVerified = Column("email_verified", Boolean, default=False, nullable=False)
    image = Column(String)
    createdAt = Column("created_at", DateTime, default=func.now(), nullable=False)
    updatedAt = Column("updated_at", DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    accounts = relationship("Account", back_populates="user", cascade="all, delete-orphan")
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    interview_sessions = relationship("InterviewSession", back_populates="user")
    reports = relationship("SessionReport", back_populates="user")

class Session(Base):
    __tablename__ = "session"

    id = Column(String, primary_key=True)
    expiresAt = Column("expires_at", DateTime, nullable=False)
    token = Column(String, nullable=False, unique=True)
    createdAt = Column("created_at", DateTime, default=func.now(), nullable=False)
    updatedAt = Column("updated_at", DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    ipAddress = Column("ip_address", String)
    userAgent = Column("user_agent", String)
    userId = Column("user_id", String, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)

    user = relationship("User", back_populates="sessions")

    __table_args__ = (
        Index("session_userId_idx", "user_id"),
    )

class Account(Base):
    __tablename__ = "account"

    id = Column(String, primary_key=True)
    accountId = Column("account_id", String, nullable=False)
    providerId = Column("provider_id", String, nullable=False)
    userId = Column("user_id", String, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    accessToken = Column("access_token", String)
    refreshToken = Column("refresh_token", String)
    idToken = Column("id_token", String)
    accessTokenExpiresAt = Column("access_token_expires_at", DateTime)
    refreshTokenExpiresAt = Column("refresh_token_expires_at", DateTime)
    scope = Column(String)
    password = Column(String)
    createdAt = Column("created_at", DateTime, default=func.now(), nullable=False)
    updatedAt = Column("updated_at", DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="accounts")

    __table_args__ = (
        Index("account_userId_idx", "user_id"),
    )

class Verification(Base):
    __tablename__ = "verification"

    id = Column(String, primary_key=True)
    identifier = Column(String, nullable=False)
    value = Column(String, nullable=False)
    expiresAt = Column("expires_at", DateTime, nullable=False)
    createdAt = Column("created_at", DateTime, default=func.now(), nullable=False)
    updatedAt = Column("updated_at", DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        Index("verification_identifier_idx", "identifier"),
    )
