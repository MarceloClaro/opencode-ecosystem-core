/**
 * Roteador didático da apresentação R781.
 * Os pesos representam normalização de utilidades; não são probabilidades
 * calibradas nem resultados de uma nova execução da dissertação.
 */

/** Softmax a temperatura 1, com deslocamento pelo máximo para evitar overflow. */
export function stableSoftmax(scores) {
  if (!Array.isArray(scores) || !scores.every(Number.isFinite)) {
    throw new TypeError("O softmax exige uma lista de números finitos.");
  }
  if (scores.length === 0) return [];

  const maximum = scores.reduce((current, score) => Math.max(current, score), -Infinity);
  const exponentials = scores.map((score) => Math.exp(score - maximum));
  const denominator = exponentials.reduce((total, value) => total + value, 0);
  return exponentials.map((value) => value / denominator);
}

function bounded(value) {
  return Number.isFinite(value) ? Math.min(1, Math.max(0, value)) : 0.5;
}

function validId(id) {
  return typeof id === "string" && id.trim().length > 0;
}

/**
 * Exclui IDs inválidos/duplicados e candidatos indisponíveis ou incompletos.
 * Só então normaliza as utilidades dos candidatos elegíveis.
 * Não modifica os cadastros recebidos.
 */
export function rankCandidates(candidates, requiredCapabilities = []) {
  if (!Array.isArray(candidates) || !Array.isArray(requiredCapabilities)) {
    throw new TypeError("Candidatos e capacidades exigidas devem ser listas.");
  }

  const counts = new Map();
  for (const candidate of candidates) {
    if (candidate && validId(candidate.id)) {
      counts.set(candidate.id, (counts.get(candidate.id) || 0) + 1);
    }
  }

  const eligible = [];
  const excluded = [];
  for (const candidate of candidates) {
    let reason;
    if (!candidate || typeof candidate !== "object" || Array.isArray(candidate)) {
      reason = "Cadastro de candidato inválido.";
    } else if (!validId(candidate.id)) {
      reason = "ID inválido: informe um texto não vazio.";
    } else if (counts.get(candidate.id) > 1) {
      reason = "ID duplicado: todas as ocorrências foram excluídas.";
    } else if (candidate.status !== "available") {
      reason = "Candidato indisponível.";
    } else if (
      !Array.isArray(candidate.capabilities) ||
      !requiredCapabilities.every((capability) => candidate.capabilities.includes(capability))
    ) {
      reason = "O candidato não oferece todas as capacidades exigidas.";
    }

    if (reason) {
      excluded.push({ ...candidate, reason });
      continue;
    }

    const semantic = bounded(candidate.semantic);
    const coverage = 1;
    const trust = bounded(candidate.trust);
    const load = bounded(candidate.load);
    const utility = 0.30 * semantic + 0.35 * coverage + 0.25 * trust + 0.10 * (1 - load);
    eligible.push({ ...candidate, semantic, coverage, trust, load, utility });
  }

  const weights = stableSoftmax(eligible.map((candidate) => candidate.utility));
  const ranked = eligible.map((candidate, index) => ({ ...candidate, weight: weights[index] }));
  ranked.sort((left, right) => {
    if (left.weight !== right.weight) return right.weight - left.weight;
    return left.id < right.id ? -1 : left.id > right.id ? 1 : 0;
  });
  return { ranked, excluded };
}
