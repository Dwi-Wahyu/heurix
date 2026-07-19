I have implemented the missing interview report generation logic and improved the session completion user
experience.

Key Changes:

1.  Backend: Report Generation Logic
    - Added summarize_interview function in backend/app/services/brain.py. This function uses the Groq
      LLM to analyze the entire conversation history and generate scores for Communication, Consistency,
      Confidence, and Stress Resistance.
    - The report also includes qualitative analysis: strengths, weaknesses, recommendations, and a
      narrative evaluation.

2.  Backend: Enhanced Filler Word Analysis
    - Updated backend/app/services/transcriber.py to return a detailed breakdown of filler words (e.g.,
      "eh", "umm", "jadi").
    - Updated backend/app/api/websocket.py to store these breakdowns for each turn and aggregate them
      into a session-wide breakdown for the final report.

3.  Backend: Integrated Workflow
    - Updated the WebSocket handler to trigger the report generation automatically when an interview ends
      (either by the user clicking "Akhiri Sesi" or reaching the 10-turn limit).
    - The SESSION_END signal is now sent to the frontend only after the report has been successfully
      generated and saved to the database. This ensures the results page will always have data to
      display.

4.  Frontend: Improved User Experience
    - Modified frontend/src/routes/session/interview/+page.svelte to include a "Memproses Hasil
      Interview" loading UI.
    - When the user ends the session, they will now see a professional loading screen with the message
      "AI sedang menganalisis performa Anda..." instead of an immediate redirect to an empty results
      page.
    - The redirect now happens only after the backend confirms the report is ready.

These updates ensure that the "Laporan belum tersedia" message is replaced by a comprehensive evaluation
report as requested.
