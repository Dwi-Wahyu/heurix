from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.services.brain import generate_next_turn, should_shift_persona, summarize_interview
from app.services.speech import speech_service
from app.services.transcriber import transcriber
from app.core.database import SessionLocal
from app.models import (
    InterviewSession, 
    InterviewAvatar, 
    SessionTurn, 
    PersonaType, 
    SessionStatus,
    UserProfile,
    MasterInstitution,
    MasterPosition,
    SessionReport
)
from sqlalchemy import desc, func
from sqlalchemy.orm import Session
import json
import uuid
import os
import base64
from datetime import datetime

router = APIRouter()

@router.websocket("/ws/{sessionId}")
async def websocket_endpoint(websocket: WebSocket, sessionId: str):
    await websocket.accept()
    db: Session = SessionLocal()
    
    try:
        # Fetch initial context
        interview_session = db.query(InterviewSession).filter(InterviewSession.id == sessionId).first()
        if not interview_session:
            await websocket.send_json({"type": "ERROR", "message": "Session not found"})
            await websocket.close()
            return

        # Initialize question_count from existing turns
        question_count = db.query(SessionTurn).filter(SessionTurn.sessionId == sessionId).count()
            
        while True:
            # Handle both text (JSON) and binary (Audio) messages
            message_data = await websocket.receive()
            
            if message_data["type"] == "websocket.disconnect":
                print(f"Client disconnected for session {sessionId}")
                break
                
            if "text" in message_data:
                message = json.loads(message_data["text"])
                
                if message["type"] == "START_INTERVIEW":
                    # Update status
                    interview_session.status = "active"
                    interview_session.startedAt = datetime.now()
                    db.commit()
                    
                    # If we already have turns, just resume (maybe re-send last question or send next)
                    if question_count > 0:
                        last_turn = db.query(SessionTurn).filter(SessionTurn.sessionId == sessionId).order_by(SessionTurn.turnNumber.desc()).first()
                        if last_turn and not last_turn.answerTranscript:
                             await re_send_last_question(websocket, db, last_turn, interview_session)
                        else:
                             await send_next_question(websocket, db, interview_session, question_count + 1)
                             question_count += 1
                    else:
                        # Generate first question
                        await send_next_question(websocket, db, interview_session, question_count + 1)
                        question_count += 1

                elif message["type"] == "END_SESSION":
                    await finish_and_report(websocket, db, interview_session)
                    break

                elif message["type"] == "FACE_METRICS":
                    metrics = message.get("metrics")
                    if metrics:
                        # Ensure it stays as a list in memory before SQLAlchemy handles it
                        current_metrics = list(interview_session.faceMetrics or [])
                        current_metrics.append(metrics)
                        interview_session.faceMetrics = current_metrics
                        db.commit()

            elif "bytes" in message_data:
                # Binary audio data
                audio_data = message_data["bytes"]
                
                if not audio_data or len(audio_data) < 100:
                    print(f"Received empty or too short audio data for session {sessionId}")
                    await websocket.send_json({"type": "ERROR", "message": "Audio data is empty or too short. Please try again."})
                    # Re-trigger recording on frontend
                    await websocket.send_json({"type": "QUESTION", "text": "Maaf, suara tidak terdengar jelas. Bisa diulangi?", "turnNumber": question_count})
                    continue

                await websocket.send_json({"type": "PROCESSING"})
                
                temp_filename = f"temp_{sessionId}_{question_count}.webm"
                print(f"Processing audio: {temp_filename} ({len(audio_data)} bytes)")
                
                with open(temp_filename, "wb") as f:
                    f.write(audio_data)
                
                try:
                    transcript_text, filler_count, filler_breakdown = transcriber.transcribe_and_detect_fillers(temp_filename)
                    print(f"Transcription result: '{transcript_text}'")
                except Exception as stt_err:
                    print(f"STT Error: {stt_err}")
                    await websocket.send_json({"type": "ERROR", "message": f"Transcription failed: {str(stt_err)}"})
                    if os.path.exists(temp_filename): os.remove(temp_filename)
                    continue

                if os.path.exists(temp_filename):
                    os.remove(temp_filename)
                
                # Send transcript back to frontend
                await websocket.send_json({"type": "TRANSCRIPT", "text": transcript_text})
                
                # Process answer and get next question
                await handle_user_answer(websocket, db, interview_session, transcript_text, question_count, filler_count, filler_breakdown)
                question_count += 1

    except WebSocketDisconnect:
        print(f"Sesi Wawancara {sessionId} Berakhir (Disconnected)")
        if interview_session and interview_session.status == "active":
            interview_session.status = "abandoned"
            db.commit()
    except Exception as e:
        print(f"Error in WebSocket: {e}")
        await websocket.send_json({"type": "ERROR", "message": str(e)})
    finally:
        db.close()

async def finish_and_report(websocket: WebSocket, db: Session, session: InterviewSession):
    """
    Mengakhiri sesi, men-generate laporan, dan mengirim sinyal selesai ke frontend.
    """
    if session.status == "completed":
        # Check if report already exists
        existing_report = db.query(SessionReport).filter(SessionReport.sessionId == session.id).first()
        if existing_report:
            await websocket.send_json({"type": "SESSION_END", "sessionId": session.id})
            return

    session.status = "completed"
    session.completedAt = datetime.now()
    if session.startedAt:
        session.durationSeconds = int((session.completedAt - session.startedAt).total_seconds())
    db.commit()

    # Trigger Report Generation
    user_profile = db.query(UserProfile).filter(UserProfile.userId == session.userId).first()
    institution = db.query(MasterInstitution).filter(MasterInstitution.id == user_profile.targetInstitutionId).first() if user_profile else None
    position = db.query(MasterPosition).filter(MasterPosition.id == user_profile.targetPositionId).first() if user_profile else None
    
    # Fallback
    if not institution: institution = MasterInstitution(name="Umum", llmContext="")
    if not position: position = MasterPosition(name="Umum", llmContext="")

    turns = db.query(SessionTurn).filter(SessionTurn.sessionId == session.id).order_by(SessionTurn.turnNumber).all()
    
    if turns:
        report_data = await summarize_interview(session, institution, position, turns)
        
        # Hitung filler words
        total_fillers = sum([t.fillerWordCount or 0 for t in turns])
        
        # Aggregated filler word breakdown
        combined_breakdown = {}
        for t in turns:
            if t.fillerWords:
                for word, count in t.fillerWords.items():
                    combined_breakdown[word] = combined_breakdown.get(word, 0) + count

        # Process face metrics
        face_expr_score = 75.0
        eye_contact_score = 80.0
        face_expr_feedback = "Ekspresi wajah Anda terlihat cukup tenang dan profesional."
        eye_contact_feedback = "Kontak mata Anda cukup konsisten selama sesi."

        if session.faceMetrics:
            metrics_list = session.faceMetrics
            smile_scores = [m.get("smileScore", 0) for m in metrics_list]
            eye_contact_samples = [m.get("isLookingAtCamera", True) for m in metrics_list]
            
            if smile_scores:
                # Average smile score (weighted towards positive)
                avg_smile = sum(smile_scores) / len(smile_scores)
                face_expr_score = 50 + (avg_smile * 50) # Scale to 50-100
                if avg_smile > 0.4:
                    face_expr_feedback = "Anda menunjukkan ekspresi wajah yang sangat positif dan ramah."
                elif avg_smile > 0.1:
                    face_expr_feedback = "Ekspresi wajah Anda cukup ramah, pertahankan senyum tipis."
                else:
                    face_expr_feedback = "Cobalah untuk lebih sering tersenyum agar terlihat lebih ramah dan tenang."
            
            if eye_contact_samples:
                consistency = sum([1 for x in eye_contact_samples if x]) / len(eye_contact_samples)
                eye_contact_score = consistency * 100
                if consistency > 0.8:
                    eye_contact_feedback = "Kontak mata Anda sangat baik dan konsisten."
                elif consistency > 0.5:
                    eye_contact_feedback = "Kontak mata Anda cukup baik, namun sesekali terlihat beralih."
                else:
                    eye_contact_feedback = "Usahakan untuk lebih konsisten menatap kamera agar membangun engagement."

        # Mapping dimensions
        dims = report_data.get("dimensions", {})

        # Save to DB
        new_report = SessionReport(
            id=str(uuid.uuid4()),
            sessionId=session.id,
            userId=session.userId,
            totalTurns=len(turns),
            totalFillerWords=total_fillers,
            fillerWordBreakdown=combined_breakdown,
            overallScore=report_data["overall_score"],
            communicationScore=dims.get("articulation", {}).get("score", report_data.get("overall_score")),
            consistencyScore=dims.get("consistency", {}).get("score", report_data.get("overall_score")),
            confidenceScore=dims.get("confidence", {}).get("score", report_data.get("overall_score")),
            stressResistanceScore=report_data.get("stress_resistance_score", report_data.get("overall_score")),
            
            # New 8 dimensions
            articulationScore=dims.get("articulation", {}).get("score"),
            intonationScore=dims.get("intonation", {}).get("score"),
            pacingScore=dims.get("pacing", {}).get("score"),
            fillerWordsScore=dims.get("filler_words", {}).get("score"),
            sentenceStructureScore=dims.get("sentence_structure", {}).get("score"),
            answerCompletenessScore=dims.get("answer_completeness", {}).get("score"),
            
            # Face & Eye Contact
            facialExpressionScore=face_expr_score,
            eyeContactScore=eye_contact_score,
            facialExpressionFeedback=face_expr_feedback,
            eyeContactFeedback=eye_contact_feedback,
            
            # Feedbacks
            articulationFeedback=dims.get("articulation", {}).get("feedback"),
            intonationFeedback=dims.get("intonation", {}).get("feedback"),
            pacingFeedback=dims.get("pacing", {}).get("feedback"),
            fillerWordsFeedback=dims.get("filler_words", {}).get("feedback"),
            sentenceStructureFeedback=dims.get("sentence_structure", {}).get("feedback"),
            answerCompletenessFeedback=dims.get("answer_completeness", {}).get("feedback"),
            consistencyFeedback=dims.get("consistency", {}).get("feedback"),
            confidenceFeedback=dims.get("confidence", {}).get("feedback"),

            strengths=report_data["strengths"],
            weaknesses=report_data["weaknesses"],
            recommendations=report_data["recommendations"],
            evaluationNarrative=report_data["evaluation_narrative"]
        )
        db.add(new_report)
        
        # Update session turns with question analysis
        qa_list = report_data.get("question_analysis", [])
        qa_map = {item["turn_number"]: item for item in qa_list if "turn_number" in item}
        
        for t in turns:
            if t.turnNumber in qa_map:
                analysis = qa_map[t.turnNumber]
                # Store as JSON string or structured text in llmAnalysis
                strength = analysis.get("strength", "")
                improvement = analysis.get("improvement", "")
                t.llmAnalysis = json.dumps({"strength": strength, "improvement": improvement})

        # Update session scores
        session.overallScore = report_data["overall_score"]
        session.communicationScore = new_report.communicationScore
        session.consistencyScore = new_report.consistencyScore
        session.confidenceScore = new_report.confidenceScore
        session.facialExpressionScore = new_report.facialExpressionScore
        session.eyeContactScore = new_report.eyeContactScore
        
        # Recalculate User Profile Aggregates
        if user_profile:
            stats = db.query(
                func.count(InterviewSession.id),
                func.avg(InterviewSession.overallScore),
                func.sum(InterviewSession.durationSeconds)
            ).filter(
                InterviewSession.userId == session.userId,
                InterviewSession.status == "completed"
            ).first()

            if stats:
                user_profile.totalSessions = stats[0] or 0
                user_profile.avgOverallScore = float(stats[1]) if stats[1] is not None else 0
                user_profile.totalMinutesPracticed = int((stats[2] or 0) / 60)
        
        db.commit()

    await websocket.send_json({"type": "SESSION_END", "sessionId": session.id})

async def send_next_question(websocket: WebSocket, db: Session, session: InterviewSession, turn_num: int, feedback: str = ""):
    avatar = db.query(InterviewAvatar).filter(InterviewAvatar.id == session.avatarId).first()
    user_profile = db.query(UserProfile).filter(UserProfile.userId == session.userId).first()
    institution = db.query(MasterInstitution).filter(MasterInstitution.id == user_profile.targetInstitutionId).first() if user_profile else None
    position = db.query(MasterPosition).filter(MasterPosition.id == user_profile.targetPositionId).first() if user_profile else None
    
    # Fallback
    if not institution: institution = MasterInstitution(name="Umum", llmContext="")
    if not position: position = MasterPosition(name="Umum", llmContext="")
    
    past_turns = db.query(SessionTurn).filter(SessionTurn.sessionId == session.id).order_by(SessionTurn.turnNumber).all()
    
    llm_result = await generate_next_turn(
        session=session,
        institution=institution,
        position=position,
        avatar=avatar,
        past_turns=past_turns,
        new_answer_transcript=None
    )
    
    question_text = llm_result["question"]
    full_text = f"{feedback} {question_text}".strip()
    
    # Save turn
    new_turn = SessionTurn(
        id=str(uuid.uuid4()),
        sessionId=session.id,
        turnNumber=turn_num,
        questionText=question_text,
        personaAtTurn=session.currentPersona or PersonaType.friendly,
    )
    db.add(new_turn)
    db.commit()

    # TTS
    audio_base64, visemes = await speech_service.generate_speech_with_visemes(full_text)
    
    await websocket_endpoint_send_json(websocket, {
        "type": "QUESTION",
        "text": full_text,
        "persona": session.currentPersona,
        "turnNumber": turn_num,
        "audio": audio_base64,
        "visemes": visemes
    })

# Helper for sending JSON safely
async def websocket_endpoint_send_json(websocket: WebSocket, data: dict):
    try:
        await websocket.send_json(data)
    except Exception as e:
        print(f"Error sending JSON: {e}")

async def handle_user_answer(websocket: WebSocket, db: Session, session: InterviewSession, transcript: str, question_count: int, filler_count: int, filler_breakdown: dict):
    # Update current turn
    current_turn = db.query(SessionTurn).filter(
        SessionTurn.sessionId == session.id, 
        SessionTurn.turnNumber == question_count
    ).first()
    
    if current_turn:
        current_turn.answerTranscript = transcript
        current_turn.fillerWordCount = filler_count
        current_turn.fillerWords = filler_breakdown
        db.commit()

    # Get feedback and shift persona if needed
    avatar = db.query(InterviewAvatar).filter(InterviewAvatar.id == session.avatarId).first()
    user_profile = db.query(UserProfile).filter(UserProfile.userId == session.userId).first()
    institution = db.query(MasterInstitution).filter(MasterInstitution.id == user_profile.targetInstitutionId).first() if user_profile else None
    position = db.query(MasterPosition).filter(MasterPosition.id == user_profile.targetPositionId).first() if user_profile else None
    
    # Ambil past_turns KECUALI turn yang sedang dijawab sekarang (karena transcript-nya dikirim terpisah di generate_next_turn)
    past_turns = db.query(SessionTurn).filter(
        SessionTurn.sessionId == session.id,
        SessionTurn.turnNumber < question_count
    ).order_by(SessionTurn.turnNumber).all()
    
    # Dapatkan pertanyaan turn yang sedang dijawab untuk melengkapi konteks
    current_turn_obj = db.query(SessionTurn).filter(
        SessionTurn.sessionId == session.id,
        SessionTurn.turnNumber == question_count
    ).first()
    
    llm_result = await generate_next_turn(
        session=session,
        institution=institution,
        position=position,
        avatar=avatar,
        past_turns=past_turns, # History turn-turn sebelumnya
        new_answer_transcript=transcript, # Jawaban dari turn saat ini
        current_question=current_turn_obj.questionText if current_turn_obj else None # Pertanyaan dari turn saat ini
    )
    
    score = llm_result.get("answer_quality_score", 50)
    feedback = llm_result.get("feedback", "")
    
    if current_turn:
        current_turn.answerQuality = score
        db.commit()

    # Persona Shift Logic
    new_persona = should_shift_persona(session, score)
    if new_persona:
        session.currentPersona = new_persona
        session.personaShiftCount += 1
        db.commit()

    await websocket_endpoint_send_json(websocket, {
        "type": "FEEDBACK",
        "score": score,
        "feedback": feedback
    })
    
    # Limit to 10 questions
    if question_count >= 10:
        await finish_and_report(websocket, db, session)
    else:
        await send_next_question(websocket, db, session, question_count + 1, feedback)

async def re_send_last_question(websocket: WebSocket, db: Session, last_turn: SessionTurn, session: InterviewSession):
    # TTS
    audio_base64, visemes = await speech_service.generate_speech_with_visemes(last_turn.questionText)
    
    await websocket_endpoint_send_json(websocket, {
        "type": "QUESTION",
        "text": last_turn.questionText,
        "persona": last_turn.personaAtTurn,
        "turnNumber": last_turn.turnNumber,
        "audio": audio_base64,
        "visemes": visemes
    })
