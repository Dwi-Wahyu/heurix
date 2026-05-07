from fastapi import FastAPI, Body, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.api import websocket
from app.services.speech import speech_service
from app.core.database import get_db, SessionLocal
from app.models import (
    InterviewAvatar, 
    MasterPosition, 
    MasterInstitution, 
    InterviewSession, 
    InterviewTrack,
    UserProfile,
    SessionReport,
    SessionTurn
)
from sqlalchemy import func
from sqlalchemy.orm import Session
import uuid

app = FastAPI(title="HireReady AI Agent Backend")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(websocket.router)

@app.get("/")
async def root():
    return {"status": "ok", "message": "HireReady API is running"}

@app.get("/api/avatars")
async def get_avatars(track: str = None, db: Session = Depends(get_db)):
    query = db.query(InterviewAvatar).filter(InterviewAvatar.isActive == True)
    if track:
        query = query.filter(InterviewAvatar.track == track)
    return query.all()

@app.get("/api/positions")
async def get_positions(db: Session = Depends(get_db)):
    return db.query(MasterPosition).filter(MasterPosition.isActive == True).all()

@app.post("/api/sessions")
async def create_session(
    payload: dict = Body(...), 
    db: Session = Depends(get_db)
):
    userId = payload.get("userId")
    avatarId = payload.get("avatarId")
    track = payload.get("track")
    
    if not all([userId, avatarId, track]):
        raise HTTPException(status_code=400, detail="Missing required fields")
    
    session_id = str(uuid.uuid4())
    new_session = InterviewSession(
        id=session_id,
        userId=userId,
        avatarId=avatarId,
        track=track,
        status="waiting"
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

@app.post("/api/speech")
async def generate_speech(payload: dict = Body(...)):
    text = payload.get("text", "")
    if not text:
        return {"error": "Text is required"}
    
    audio_b64, visemes = await speech_service.generate_speech_with_visemes(text)
    return {
        "audio": audio_b64,
        "visemes": visemes
    }

@app.get("/api/institutions")
async def get_institutions(db: Session = Depends(get_db)):
    return db.query(MasterInstitution).all()

@app.get("/api/profile/{userId}")
async def get_user_profile(userId: str, db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.userId == userId).first()
    if not profile:
        # Create a default profile if it doesn't exist
        profile = UserProfile(id=str(uuid.uuid4()), userId=userId)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    
    # Auto-sync stats if they are zero but sessions exist (for existing history)
    if profile.totalSessions == 0:
        stats = db.query(
            func.count(InterviewSession.id),
            func.avg(InterviewSession.overallScore),
            func.sum(InterviewSession.durationSeconds)
        ).filter(
            InterviewSession.userId == userId,
            InterviewSession.status == "completed"
        ).first()
        
        if stats and stats[0] > 0:
            profile.totalSessions = stats[0]
            profile.avgOverallScore = float(stats[1]) if stats[1] is not None else 0
            profile.totalMinutesPracticed = int((stats[2] or 0) / 60)
            db.commit()
            db.refresh(profile)
            
    return profile

@app.patch("/api/profile")
async def update_user_profile(payload: dict = Body(...), db: Session = Depends(get_db)):
    userId = payload.get("userId")
    if not userId:
        raise HTTPException(status_code=400, detail="userId is required")
    
    profile = db.query(UserProfile).filter(UserProfile.userId == userId).first()
    if not profile:
        profile = UserProfile(id=str(uuid.uuid4()), userId=userId)
        db.add(profile)
    
    if "targetInstitutionId" in payload:
        profile.targetInstitutionId = payload["targetInstitutionId"]
    if "targetPositionId" in payload:
        profile.targetPositionId = payload["targetPositionId"]
    if "preferredTrack" in payload:
        profile.preferredTrack = payload["preferredTrack"]
        
    db.commit()
    db.refresh(profile)
    return profile

@app.get("/api/sessions")
async def get_sessions(userId: str, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(InterviewSession).filter(InterviewSession.userId == userId)\
        .order_by(InterviewSession.createdAt.desc())\
        .limit(limit).all()

@app.get("/api/sessions/{sessionId}")
async def get_session(sessionId: str, db: Session = Depends(get_db)):
    session = db.query(InterviewSession).filter(InterviewSession.id == sessionId).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "id": session.id,
        "userId": session.userId,
        "avatarId": session.avatarId,
        "track": session.track,
        "status": session.status,
        "avatar": {
            "id": session.avatar.id,
            "name": session.avatar.name,
            "glbUrl": session.avatar.glbUrl,
            "ttsVoiceId": session.avatar.ttsVoiceId,
            "cameraConfig": session.avatar.cameraConfig
        }
    }

@app.get("/api/sessions/{sessionId}/report")
async def get_session_report(sessionId: str, db: Session = Depends(get_db)):
    report = db.query(SessionReport).filter(SessionReport.sessionId == sessionId).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    turns = db.query(SessionTurn).filter(SessionTurn.sessionId == sessionId).order_by(SessionTurn.turnNumber).all()
    
    return {
        "report": report,
        "sessionTurns": turns
    }

if __name__ == "__main__":
    import uvicorn
    import os
    
    # Path to certs (relative to backend/)
    # Adjusted to look for frontend/certs directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ssl_key = os.path.join(base_dir, "../frontend/certs/key.pem")
    ssl_cert = os.path.join(base_dir, "../frontend/certs/cert.pem")
    
    if os.path.exists(ssl_key) and os.path.exists(ssl_cert):
        print(f"Starting backend with SSL (Key: {ssl_key})")
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8000,
            ssl_keyfile=ssl_key,
            ssl_certfile=ssl_cert
        )
    else:
        print("Starting backend without SSL (certificates not found)")
        uvicorn.run(app, host="0.0.0.0", port=8000)
