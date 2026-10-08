import type { HTMLAttributes } from "react";
import { Icon } from "./Icon";

export function DisclosureSummary({
  children,
  chevronPosition = "start",
  ...props
}: HTMLAttributes<HTMLElement> & { chevronPosition?: "start" | "end" }) {
  const chevron = (
    <Icon
      className="ngs-disclosure-chevron"
      name="chevron-right-sm"
      size={16}
    />
  );
  return (
    <summary {...props} data-chevron-position={chevronPosition}>
      {chevronPosition === "start" ? chevron : null}
      {children}
      {chevronPosition === "end" ? chevron : null}
    </summary>
  );
}
