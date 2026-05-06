import type { FaceAnimator } from "./FaceAnimator";

export function startAutoBlink(animator: FaceAnimator): () => void {
  let timeoutId: ReturnType<typeof setTimeout>;

  function scheduleNextBlink() {
    const delay = 2000 + Math.random() * 4000;

    timeoutId = setTimeout(() => {
      const blinkDuration = 80 + Math.random() * 70;

      animator.setExpression({ Eye_Blink: 1.0 });

      setTimeout(() => {
        animator.setExpression({ Eye_Blink: 0 });
        scheduleNextBlink();
      }, blinkDuration);
    }, delay);
  }

  scheduleNextBlink();

  return () => clearTimeout(timeoutId);
}
