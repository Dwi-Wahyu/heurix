export type ShapeKeyWeights = Record<string, number>;

/**
 * Peta viseme → shape key weights.
 * Semua nilai 0.0 – 1.0.
 * Shape keys yang tidak disebutkan akan di-reset ke 0.
 * Mengikuti instruksi di static/face/professional-man/instruction.md
 */
export const VISEME_MAP: Record<string, ShapeKeyWeights> = {
  sil: {},
  PP: { Explosive: 1.0, Mouth_Lips_Tight: 0.3 },
  FF: { Dental_Lip: 1.0 },
  TH: { Open: 0.2, Dental_Lip: 0.4 },
  DD: { Mouth_Plosive: 0.8, Open: 0.15 },
  kk: { Mouth_Plosive: 0.6, Open: 0.2 },
  CH: { Affricate: 1.0, Tight_O: 0.3 },
  SS: { Wide: 0.5, Mouth_Lips_Part: 0.4 },
  nn: { Open: 0.1, Mouth_Lips_Open: 0.2 },
  RR: { Tight_O: 0.5, Open: 0.2 },
  AA: { Open: 1.0, Mouth_Lips_Open: 0.8 },
  EE: { Wide: 0.8, Open: 0.4 },
  II: { Wide: 1.0, Open: 0.2 },
  OO: { Tight_O: 1.0, Open: 0.5 },
  UU: { Tight_O: 0.8, Mouth_Pucker: 0.6 },
  // Tambahan untuk backward compatibility atau variasi
  WW: { Tight_O: 0.8, Mouth_Pucker: 0.4 },
};

/** Shape keys yang relevan untuk viseme (untuk reset selektif) */
export const VISEME_SHAPE_KEYS = [
  "Open",
  "Explosive",
  "Dental_Lip",
  "Tight_O",
  "Wide",
  "Affricate",
  "Lip_Open",
  "Mouth_Plosive",
  "Mouth_Pucker",
  "Mouth_Lips_Part",
  "Mouth_Lips_Open",
  "Mouth_Lips_Tight",
  "Mouth_Bottom_Lip_Down",
  "Mouth_Widen_Sides",
  "Mouth_Smile",
  "Mouth_Frown",
  "Eye_Blink",
  "Brow_Raise_Inner_L",
  "Brow_Raise_Inner_R",
  "Brow_Raise_Outer_L",
  "Brow_Raise_Outer_R",
  "Brow_Drop_L",
  "Brow_Drop_R",
  "Eye_Wide_L",
  "Eye_Wide_R",
  "Eye_Squint_L",
  "Eye_Squint_R",
  "Nose_Scrunch",
  "Nose_Nostrils_Flare",
  "Cheek_Raise_L",
  "Cheek_Raise_R",
];
