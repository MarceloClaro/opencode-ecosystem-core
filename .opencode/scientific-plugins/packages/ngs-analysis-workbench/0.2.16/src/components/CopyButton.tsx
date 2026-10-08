import { useState } from "react";
import { Icon } from "../design-system/Icon";
import { copyToClipboard, type CopyStatus } from "../report/format";
import ui from "../styles/ui.module.css";

export function CopyButton({
  value,
  label = "Copy path",
  accessibleLabel = label,
  failureLabel = "Copy failed",
  variant = "quiet",
}: {
  value: string;
  label?: string;
  accessibleLabel?: string;
  failureLabel?: string;
  variant?: "quiet" | "secondary";
}) {
  const [status, setStatus] = useState<CopyStatus>("idle");
  return (
    <button
      aria-label={accessibleLabel}
      className={`${ui.button} ${
        variant === "quiet" ? ui.buttonQuiet : ui.buttonSecondary
      }`}
      data-status={status}
      onClick={() => void copyToClipboard(value, setStatus)}
      title={accessibleLabel}
      type="button"
    >
      <Icon name={status === "copied" ? "check-md" : "copy"} size={16} />
      <span aria-live="polite">
        {status === "copied"
          ? "Copied"
          : status === "failed"
          ? failureLabel
          : label}
      </span>
    </button>
  );
}
