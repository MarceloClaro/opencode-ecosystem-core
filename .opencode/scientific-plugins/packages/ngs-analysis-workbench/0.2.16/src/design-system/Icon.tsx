import type { CSSProperties, HTMLAttributes } from "react";

import arrowLeft from "./icons/arrow-left.svg?inline";
import arrowTopRight from "./icons/arrow-top-right-sm-thin.svg?inline";
import barChart from "./icons/bar-chart.svg?inline";
import buildingBlocks from "./icons/building-blocks.svg?inline";
import checkMd from "./icons/check-md.svg?inline";
import chevronDown from "./icons/chevron-down-sm.svg?inline";
import chevronRight from "./icons/chevron-right-sm.svg?inline";
import close from "./icons/close-small.svg?inline";
import closeMedium from "./icons/close-medium.svg?inline";
import copy from "./icons/copy.svg?inline";
import info from "./icons/info-sm.svg?inline";
import menu from "./icons/menu.svg?inline";
import regenerate from "./icons/regenerate.svg?inline";
import spinner from "./icons/spinner.svg?inline";
import squareGrid from "./icons/square-grid.svg?inline";
import document from "./icons/upload-documents.svg?inline";

const icons = {
  "arrow-left": arrowLeft,
  "arrow-top-right-sm-thin": arrowTopRight,
  "bar-chart": barChart,
  "building-blocks": buildingBlocks,
  "check-md": checkMd,
  "chevron-down-sm": chevronDown,
  "chevron-right-sm": chevronRight,
  "close-small": close,
  "close-medium": closeMedium,
  copy,
  "info-sm": info,
  menu,
  regenerate,
  spinner,
  "square-grid": squareGrid,
  "upload-documents": document,
};

export type IconName = keyof typeof icons;

// The foundation Icon primitive, with inlined source assets so packaged MCP
// resources never depend on a host-relative /icons URL or external fetch.
export function Icon({
  className,
  label,
  name,
  size = 18,
  style,
  ...props
}: Omit<HTMLAttributes<HTMLSpanElement>, "children"> & {
  name: IconName;
  label?: string;
  size?: number;
}) {
  return (
    <span
      {...props}
      aria-hidden={label ? undefined : true}
      aria-label={label}
      className={["oai-icon", className].filter(Boolean).join(" ")}
      role={label ? "img" : undefined}
      style={
        {
          ...style,
          "--oai-icon-size": `${size}px`,
          "--oai-icon-source": `url("${icons[name]}")`,
        } as CSSProperties
      }
    />
  );
}

export function StatusIcon({
  tone,
  active = false,
  size,
}: {
  tone: string;
  active?: boolean;
  size?: number;
}) {
  const name: IconName =
    tone === "success" || tone === "complete"
      ? "check-md"
      : ["danger", "failed", "blocked"].includes(tone)
      ? "close-medium"
      : active
      ? "spinner"
      : "info-sm";
  return (
    <Icon
      className={active ? "ngs-spin" : undefined}
      name={name}
      size={size ?? (name === "check-md" ? 16 : 20)}
    />
  );
}
