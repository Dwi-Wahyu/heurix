# Implementation Report: Avatar Hassan Camera Config Adjustment

**Date**: July 23, 2026  
**Target File**: `frontend/src/lib/server/db/seeds/seeds-avatar-interviewer.ts`  
**Status**: Completed, Seeded & Verified  

---

## 1. Issue Description

During 3D avatar rendering in the interview session, the camera framing for **Hassan** (`avatar_hassan`) was zoomed in too closely onto the model's forehead/hairline, cutting off the face and neck.

### Root Cause
* In `frontend/src/routes/session/interview/+page.svelte`, camera focus and distance are calculated using:
  $$\text{focusHeight} = \text{size.y} \times (1 - \text{headHeightRatio})$$
  $$\text{distance} = \left(\frac{\text{focusHeight} / 2}{\tan(\text{fov}/2) \times \text{desiredCoverage}}\right) \times \text{distanceOffset}$$
* Setting `headHeightRatio` to an excessively high value (e.g. `0.86`) resulted in a tiny `focusHeight`, causing the camera distance to become extremely close to the forehead.
* Furthermore, there was an inconsistency in `seeds-avatar-interviewer.ts` between `.values()` (`headHeightRatio: 0.1`) and `.onConflictDoUpdate()` (`headHeightRatio: 0.82`).

---

## 2. Implemented Fix

1. **Updated `cameraConfig` for Avatar Hassan**:
   * Adjusted `cameraConfig` to `{ headHeightRatio: 0.25, distanceOffset: 1.2, lookAtOffset: 0.05 }`.
   * Synchronized both `.values()` and `.onConflictDoUpdate()` in `seeds-avatar-interviewer.ts` to ensure consistent upserts.
2. **Re-executed Seeding Script**:
   * Ran `npx tsx src/lib/server/db/seeds/seeds-avatar-interviewer.ts` to update the PostgreSQL database (`interview_avatar` table).
   * Verified that the seeder performs a clean **upsert** (`onConflictDoUpdate`) without deleting any database records.

---

## 3. Results & Verification

* **Camera Framing**: Hassan is now properly framed from head down to the neck and upper chest, with balanced portrait positioning matching the other avatars (Pak Subarjo & Indra).
* **Database State**: Seeding script completed with status `✅ Avatar "Hassan" berhasil di-seed.`
* **Code Graph Update**: Post-implementation protocol executed (`graphify update .` & `graphify cluster-only`).
