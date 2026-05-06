import type { ShapeKeyWeights } from "./visemeMap";

/**
 * Preset emosi sesuai dengan instruksi di static/face/professional-man/instruction.md
 */
export const EMOTIONS: Record<string, ShapeKeyWeights> = {
  neutral: {},
  happy: {
    Mouth_Smile: 0.7,
    Cheek_Raise_L: 0.5,
    Cheek_Raise_R: 0.5,
    Eye_Squint_L: 0.3,
    Eye_Squint_R: 0.3,
    Brow_Raise_L: 0.2,
    Brow_Raise_R: 0.2,
  },
  sad: {
    Mouth_Frown: 0.6,
    Brow_Raise_Inner_L: 0.7,
    Brow_Raise_Inner_R: 0.7,
    Brow_Drop_L: 0.3,
    Brow_Drop_R: 0.3,
    Eye_Squint_L: 0.2,
    Eye_Squint_R: 0.2,
  },
  surprised: {
    Open: 0.6,
    Eye_Wide_L: 0.9,
    Eye_Wide_R: 0.9,
    Brow_Raise_L: 0.9,
    Brow_Raise_R: 0.9,
    Mouth_Lips_Open: 0.5,
  },
  angry: {
    Mouth_Frown: 0.5,
    Brow_Drop_L: 0.8,
    Brow_Drop_R: 0.8,
    Nose_Scrunch: 0.4,
    Eye_Squint_L: 0.5,
    Eye_Squint_R: 0.5,
    // Mouth_Snarl_Upp in instruction, but often model has L/R
    Mouth_Snarl_Upper_L: 0.3,
    Mouth_Snarl_Upper_R: 0.3,
  },
  disgusted: {
    Nose_Scrunch: 0.8,
    Nose_Nostrils_Flare: 0.4,
    Mouth_Frown_L: 0.4,
    Mouth_Frown_R: 0.4,
    Eye_Squint_L: 0.4,
    Eye_Squint_R: 0.4,
    Cheek_Raise_L: 0.3,
    Cheek_Raise_R: 0.3,
  },
  fearful: {
    Eye_Wide_L: 0.8,
    Eye_Wide_R: 0.8,
    Brow_Raise_Inner_L: 1.0,
    Brow_Raise_Inner_R: 1.0,
    Mouth_Lips_Open: 0.3,
    Mouth_Lips_Part: 0.5,
  },
  confused: {
    Brow_Raise_Outer_L: 0.7,
    Brow_Drop_R: 0.5,
    Mouth_R: 0.2,
  },
};

export const EMOTION_PRESETS = EMOTIONS;
