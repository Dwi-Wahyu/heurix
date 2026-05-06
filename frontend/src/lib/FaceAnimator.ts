import * as THREE from "three";
import {
  VISEME_MAP,
  VISEME_SHAPE_KEYS,
  type ShapeKeyWeights,
} from "./visemeMap";
import {
  collectMorphMeshes,
  setMorph,
  resetAllMorphs,
} from "./visemeController";

export class FaceAnimator {
  public meshes: THREE.Mesh[];
  private currentWeights: ShapeKeyWeights = {};
  private targetWeights: ShapeKeyWeights = {};
  private lerpSpeed = 12;

  constructor(model: THREE.Group) {
    this.meshes = collectMorphMeshes(model);
    console.log("FaceAnimator initialized with meshes:", this.meshes.length);
    
    // Initialize weights to 0
    for (const key of VISEME_SHAPE_KEYS) {
        this.currentWeights[key] = 0;
        this.targetWeights[key] = 0;
    }
  }

  /**
   * Set bukaan mulut secara manual (biasanya untuk lip sync amplitude).
   * Ini akan mengupdate internal state agar tidak ditimpa oleh update().
   */
  setMouth(amplitude: number): void {
    const val = Math.max(0, Math.min(1, amplitude));
    // Update target & current agar update() loop tetap sinkron
    this.targetWeights["Open"] = val;
    this.currentWeights["Open"] = val;
    this.targetWeights["Mouth_Lips_Open"] = val;
    this.currentWeights["Mouth_Lips_Open"] = val;
    
    setMorph(this.meshes, "Open", val);
    setMorph(this.meshes, "Mouth_Lips_Open", val);
  }

  setViseme(visemeId: string): void {
    const weights = VISEME_MAP[visemeId] ?? {};
    this.targetWeights = {};
    for (const key of VISEME_SHAPE_KEYS) {
      this.targetWeights[key] = 0;
    }
    Object.assign(this.targetWeights, weights);
  }

  update(delta: number): void {
    for (const key of VISEME_SHAPE_KEYS) {
      const current = this.currentWeights[key] ?? 0;
      const target = this.targetWeights[key] ?? 0;

      if (Math.abs(current - target) < 0.001) {
        this.currentWeights[key] = target;
      } else {
        this.currentWeights[key] = THREE.MathUtils.lerp(
          current,
          target,
          1 - Math.exp(-this.lerpSpeed * delta),
        );
      }

      setMorph(this.meshes, key, this.currentWeights[key]);
    }
  }

  /** Set ekspresi (seperti blink, alis, dll) */
  setExpression(weights: ShapeKeyWeights): void {
    for (const [key, value] of Object.entries(weights)) {
      // Jika key ini ada di VISEME_SHAPE_KEYS, update internal state
      if (VISEME_SHAPE_KEYS.includes(key)) {
          this.currentWeights[key] = value;
          this.targetWeights[key] = value;
      }
      setMorph(this.meshes, key, value);
    }
  }

  resetFace(): void {
    resetAllMorphs(this.meshes);
    for (const key of VISEME_SHAPE_KEYS) {
        this.currentWeights[key] = 0;
        this.targetWeights[key] = 0;
    }
  }
}
