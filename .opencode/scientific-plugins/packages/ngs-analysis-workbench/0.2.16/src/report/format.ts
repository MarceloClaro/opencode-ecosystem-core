export type CopyStatus = "idle" | "copied" | "failed";

export async function copyToClipboard(
  value: string,
  setStatus: (status: CopyStatus) => void,
) {
  let copied = false;

  try {
    if (!navigator.clipboard?.writeText) {
      throw new Error("The Clipboard API is unavailable.");
    }
    await navigator.clipboard.writeText(value);
    copied = true;
  } catch {
    copied = copyWithSelection(value);
  }

  setStatus(copied ? "copied" : "failed");
  window.setTimeout(() => setStatus("idle"), 1_800);
}

function copyWithSelection(value: string) {
  const input = document.createElement("textarea");
  input.value = value;
  input.setAttribute("readonly", "");
  input.style.position = "fixed";
  input.style.opacity = "0";
  input.style.pointerEvents = "none";
  document.body.append(input);
  input.select();

  try {
    return document.execCommand("copy");
  } catch {
    return false;
  } finally {
    input.remove();
  }
}

export function joinRunPath(runDirectory: string, path: string) {
  return `${runDirectory.replace(/\/$/, "")}/${path.replace(/^\//, "")}`;
}

export function humanize(value: string) {
  if (value === "html_report") return "HTML report";
  if (value === "json") return "JSON";
  return value
    .replaceAll("_", " ")
    .replace(/^\w/, (character) => character.toUpperCase());
}
