import { Tooltip } from "@base-ui/react/tooltip";
import { useState } from "react";
import { Icon, type IconName } from "./Icon";
import ui from "../styles/ui.module.css";
import styles from "./TooltipIconButton.module.css";

export function TooltipIconButton({
  label,
  icon,
  busy = false,
  onClick,
}: {
  label: string;
  icon: IconName;
  busy?: boolean;
  onClick: () => void;
}) {
  const [trigger, setTrigger] = useState<HTMLElement | null>(null);
  const [open, setOpen] = useState(false);
  // Keep host tokens and native modal top-layer membership while escaping the
  // scrolling attempt panel. A body portal would lose both in embedded views.
  const container = trigger?.closest<HTMLElement>("dialog, .ngs-theme");

  return (
    <Tooltip.Root open={open} onOpenChange={setOpen} disabled={busy}>
      <Tooltip.Trigger
        ref={setTrigger}
        render={<button type="button" disabled={busy} />}
        className={`${ui.button} ${ui.buttonQuiet} ${ui.iconButton}`}
        aria-label={label}
        aria-busy={busy}
        onClick={onClick}
        onKeyDown={(event) => {
          if (event.key === "Escape" && open) {
            event.preventDefault();
            event.stopPropagation();
            setOpen(false);
          }
        }}
      >
        <Icon
          name={busy ? "spinner" : icon}
          className={busy ? "ngs-spin" : undefined}
          size={20}
        />
      </Tooltip.Trigger>
      <Tooltip.Portal container={container}>
        <Tooltip.Positioner
          className={styles.positioner}
          side="bottom"
          align="end"
          sideOffset={8}
          collisionPadding={8}
        >
          <Tooltip.Popup className={styles.popup} role="tooltip">
            {label}
          </Tooltip.Popup>
        </Tooltip.Positioner>
      </Tooltip.Portal>
    </Tooltip.Root>
  );
}
