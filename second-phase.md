Avatar Optimization Finalized: Finalizing 3D avatar optimization and shape key standardization.

✦ I have successfully completed the 3D avatar optimizations and shape key standardization as outlined in
model-optimization.md.

Summary of Improvements:

1.  Mandatory Shape Key Standardization:
    - Contract Alignment: Standardized all shape key names across the project. Renamed Tight-O to Tight_O
      and Mouth_Open to Mouth_Lips_Open in visemeMap.ts, FaceAnimator.ts, and emotionPresets.ts.
    - Robustness: Ensured FaceAnimator uses the correct Mouth_Lips_Open target for amplitude-based
      lip-sync.

2.  Optimized Loading & Caching:
    - GLB Cache: Created src/lib/avatarCache.ts which stores model ArrayBuffer in memory. This allows
      near-instant avatar loading if a user repeats a session or restarts.
    - Prefetching: Added background preloading to the disclaimer page. The browser now fetches the 47MB
      avatar while the user reads the instructions, so it's ready by the time they click "Mulai".
    - Progressive UI: Implemented a loading state in the interview page featuring a skeleton placeholder
      and a dynamic progress bar, ensuring users are never left with a blank screen.

3.  Professional Studio Rendering:
    - Cinematic Framing: Configured the Three.js camera with a narrow 28 FOV for a professional
      "head-and-shoulders" interview shot, eliminating lens distortion on the face.
    - Three-point Lighting: Implemented a studio lighting setup consisting of a warm Key light, a cool
      Fill light, and a Rim light to provide depth and highlight the avatar's silhouette.
    - Body Mesh Culling: Automatically hides lower-body meshes (shoes, pants) during rendering to
      optimize performance without sacrificing visual quality in the close-up view.

The 3D avatar system is now significantly more efficient, visually polished, and fully compliant with the
project's technical requirements.
