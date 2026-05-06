import * as THREE from "three";

export function collectMorphMeshes(model: THREE.Group): THREE.Mesh[] {
  const meshes: THREE.Mesh[] = [];
  model.traverse((obj) => {
    const mesh = obj as THREE.Mesh;
    if (mesh.isMesh && mesh.morphTargetDictionary) {
      meshes.push(mesh);
    }
  });
  return meshes;
}

export function setMorph(
  meshes: THREE.Mesh[],
  shapeName: string,
  value: number,
): void {
  for (const mesh of meshes) {
    const idx = mesh.morphTargetDictionary?.[shapeName];
    if (idx !== undefined && mesh.morphTargetInfluences) {
      mesh.morphTargetInfluences[idx] = Math.max(0, Math.min(1, value));
    }
  }
}

export function resetAllMorphs(meshes: THREE.Mesh[]): void {
  for (const mesh of meshes) {
    if (mesh.morphTargetInfluences) {
      mesh.morphTargetInfluences.fill(0);
    }
  }
}
