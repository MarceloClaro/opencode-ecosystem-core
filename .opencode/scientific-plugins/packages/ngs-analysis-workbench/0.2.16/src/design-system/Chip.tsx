import type { HTMLAttributes, ReactNode } from "react";
import { StatusIcon } from "./Icon";
import styles from "./Chip.module.css";

export type ChipTone = "neutral" | "info" | "success" | "warning" | "danger";

export function Chip({
  children,
  className,
  icon,
  tone = "neutral",
  ...props
}: HTMLAttributes<HTMLSpanElement> & {
  icon?: ReactNode;
  tone?: ChipTone;
}) {
  return (
    <span
      {...props}
      className={[styles.chip, className].filter(Boolean).join(" ")}
      data-ngs-chip=""
      data-tone={tone}
    >
      {icon}
      {children}
    </span>
  );
}

export function StatusChip({
  active = false,
  tone,
  ...props
}: Omit<Parameters<typeof Chip>[0], "icon"> & { active?: boolean }) {
  return (
    <Chip
      {...props}
      tone={tone}
      icon={<StatusIcon tone={tone ?? "neutral"} active={active} />}
    />
  );
}
