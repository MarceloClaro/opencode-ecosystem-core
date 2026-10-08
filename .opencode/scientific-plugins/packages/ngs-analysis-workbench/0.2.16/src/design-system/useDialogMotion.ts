import { useCallback, useEffect, useRef, type RefObject } from "react";

/** Keep the native modal/focus trap until its short exit has finished. */
export function useDialogMotion(
  dialogRef: RefObject<HTMLDialogElement | null>,
) {
  const exitAnimation = useRef<Animation | null>(null);
  useEffect(
    () => () => {
      exitAnimation.current?.cancel();
    },
    [],
  );

  return useCallback(() => {
    const dialog = dialogRef.current;
    if (!dialog?.open || exitAnimation.current) return;
    const style = getComputedStyle(dialog);
    const durationToken = style.getPropertyValue("--oai-duration-fast").trim();
    // Minifiers may normalize 140ms to .14s; Web Animations expects milliseconds.
    const duration =
      (parseFloat(durationToken) || 0) *
      (durationToken.endsWith("ms") ? 1 : 1000);
    if (!duration || matchMedia("(prefers-reduced-motion: reduce)").matches) {
      dialog.close();
      return;
    }
    const animation = dialog.animate(
      [
        { opacity: 1, transform: "scale(1)" },
        { opacity: 0, transform: "scale(0.98)" },
      ],
      {
        duration,
        easing: style.getPropertyValue("--oai-ease-exit").trim(),
        fill: "forwards",
      },
    );
    exitAnimation.current = animation;
    void animation.finished
      .then(
        () => {
          if (dialog.isConnected && dialog.open) dialog.close();
        },
        () => {},
      )
      .finally(() => {
        animation.cancel();
        exitAnimation.current = null;
      });
  }, [dialogRef]);
}
