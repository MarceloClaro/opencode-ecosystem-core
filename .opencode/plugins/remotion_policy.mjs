/**
 * Política pura do plugin remotion-guard (R1025).
 * Não importa Remotion, não executa comandos e não acessa a rede.
 */

export function validLicenseAck(data) {
  return Boolean(
    data &&
      data.acknowledged === true &&
      data.license === "Remotion License" &&
      Array.isArray(data.scope) &&
      data.scope.includes("install"),
  );
}

const RENDER = /\bremotion\s+(?:render|still|bundle)\b/i;
const STUDIO = /\bremotion\s+studio\b/i;
const UPGRADE = /\bremotion\s+upgrade\b/i;
const INSTALL = /\b(?:npm|pnpm|yarn|bun)\s+(?:install|i|add)\b[^;&|]*\b(?:remotion|@remotion\/)/i;
const REMOTION = /\bremotion\b/i;

function block(code, reason, command) {
  return { decision: "block", code, reason, command, executed: false };
}

function allow(code, reason, command) {
  return { decision: "allow", code, reason, command, executed: false };
}

export function decideCommand(command, options = {}) {
  if (typeof command !== "string" || !command.trim()) {
    return block("invalid_command", "comando vazio ou inválido", command);
  }
  const normalized = command.split(/\s+/).join(" ").trim();
  if (INSTALL.test(normalized)) {
    if (options.licenseAck === true) {
      return allow(
        "install_license_acknowledged",
        "ciência da licença registrada pelo operador",
        normalized,
      );
    }
    return block(
      "license_ack_required",
      "instalação de Remotion exige REMOTION_LICENSE_ACK=1",
      normalized,
    );
  }
  if (RENDER.test(normalized)) {
    if (options.renderApproved === true) {
      return allow(
        "render_approved",
        "render autorizado explicitamente pelo operador",
        normalized,
      );
    }
    return block(
      "render_requires_approval",
      "render/still/bundle exige REMOTION_RENDER_APPROVED=1",
      normalized,
    );
  }
  if (STUDIO.test(normalized)) {
    return allow(
      "preview_allowed",
      "prévia interativa não renderiza o vídeo",
      normalized,
    );
  }
  if (UPGRADE.test(normalized)) {
    return block(
      "upgrade_requires_review",
      "upgrade altera dependências; revise antes",
      normalized,
    );
  }
  if (REMOTION.test(normalized)) {
    return allow(
      "remotion_readonly",
      "comando Remotion sem render nem instalação",
      normalized,
    );
  }
  return allow(
    "unrelated",
    "comando não pertence ao fluxo Remotion",
    normalized,
  );
}
