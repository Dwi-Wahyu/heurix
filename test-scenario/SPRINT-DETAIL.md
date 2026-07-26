---
config:
  layout: fixed
---
flowchart TB
 subgraph SP1["Sprint 1: Fondasi (2 minggu)"]
        S1A["Setup FastAPI Backend"]
        S1B["Database PostgreSQL + Drizzle"]
        S1C["WebSocket Connection"]
        S1D["Struktur Project"]
  end
 subgraph SP2["Sprint 2: Avatar 3D (2 minggu)"]
        S2A["Three.js + WebGL Setup"]
        S2B["FaceAnimator + Ekspresi"]
        S2C["LipSync Implementation"]
        S2D["Draco Decoder Integration"]
  end
 subgraph SP3["Sprint 3: Speech (2 minggu)"]
        S3A["VAD + Whisper STT"]
        S3B["Kokoro TTS Integration"]
        S3C["Viseme Generation"]
        S3D["Audio Streaming"]
  end
 subgraph SP4["Sprint 4: AI Engine (2 minggu)"]
        S4A["Groq API Integration"]
        S4B["brain.py - Prompt Engine"]
        S4C["Dynamic Stress Logic"]
        S4D["Persona Shift Implementation"]
  end
 subgraph SP5["Sprint 5: Testing (2 minggu)"]
        S5B["Bug Fixing"]
        S5C["Performance Optimization"]
        S5D["Laporan Evaluasi"]
  end
    SP1 --> SP2
    SP2 --> SP3
    SP3 --> SP4
    SP4 --> SP5

    style SP1 fill:#e3f2fd,stroke:#1976d2
    style SP2 fill:#e8f5e9,stroke:#388e3c
    style SP3 fill:#fff3e0,stroke:#e65100
    style SP4 fill:#f3e5f5,stroke:#6a1b9a
    style SP5 fill:#ffebee,stroke:#c62828P