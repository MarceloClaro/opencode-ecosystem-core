#!/usr/bin/env bash
# ============================================================================
# causal_claim_guard.sh — Hook: nega alegação causal sem desenho que a sustente
# ----------------------------------------------------------------------------
# Fail-closed: sai 1 (DENIED) quando módulos de resultados/discussão/conclusão
# contêm verbos causais (PT/EN) e nenhum módulo de método declara desenho
# causal (DID, IV, RDD, experimento, Bayes) ou protocolo de replicação.
# Concretiza o Contrato de Força de Alegação (research/claim_strength).
#
# Uso:
#   causal_claim_guard.sh DIR_DO_ARTIGO
# Registro no engine (core-hooks):
#   HookMatcher("Write", hooks=[causal_claim_guard])  # via hooks.engine
# ============================================================================
set -u
DIR="${1:-}"

[ -n "${DIR}" ] || { echo "causal_claim_guard: DENIED (diretório não informado)" >&2; exit 1; }
[ -d "${DIR}" ] || { echo "causal_claim_guard: DENIED (diretório inexistente: ${DIR})" >&2; exit 1; }

mapfile -t TEXS < <(find "${DIR}" -maxdepth 2 -name '*.tex' 2>/dev/null)
[ "${#TEXS[@]}" -gt 0 ] || { echo "causal_claim_guard: ALLOW (sem .tex no diretório)"; exit 0; }

CAUSAIS='causa(m|ram)? |provoca(m|ram)? |demonstra(m)?( que)?|prova(m)?( que)?|cura(m|ram)?|eficaz|eficácia|efetiv|causes? |proves? |demonstrates? |leads to|causal effect|treatment effect'
DESENHO='diferenças-em-diferenças|diferen..as-em-diferen..as|variável instrumental|variavel instrumental|2SLS|descontinuidade|randomiz|experimento|experiment|Bayes|modelos? mistos?|efeitos? mistos?|mixed[- ]models?|propensity|pareamento'
# Siglas em caixa alta com fronteira Unicode explícita (evita "didáticos", "rdd"-like).
# grep -i NÃO se aplica aqui: DID/RDD só valem em maiúsculas.
DESENHO_SIGLAS='([^A-Za-zÀ-ÿ]|^)(DID|RDD)([^A-Za-zÀ-ÿ]|$)'

ALVOS=()
for f in "${TEXS[@]}"; do
  base="$(basename "${f}")"
  case "${base}" in
    *resultado*|*discuss*|*conclus*|*resumo*|*abstract*) ALVOS+=("${f}") ;;
  esac
done
[ "${#ALVOS[@]}" -gt 0 ] || { echo "causal_claim_guard: ALLOW (sem módulos de resultado/discussão)"; exit 0; }

if ! grep -rhoEi "(${CAUSAIS})" "${ALVOS[@]}" 2>/dev/null | grep -q .; then
  echo "causal_claim_guard: ALLOW (sem verbo causal nos resultados)"
  exit 0
fi

if grep -rhoEi "(${DESENHO})" "${TEXS[@]}" 2>/dev/null | grep -q . \
  || grep -rhoE "(${DESENHO_SIGLAS})" "${TEXS[@]}" 2>/dev/null | grep -q .; then
  echo "causal_claim_guard: ALLOW (verbo causal amparado por desenho declarado)"
  exit 0
fi

echo "causal_claim_guard: DENIED (verbo causal em resultados/discussão sem desenho causal declarado no método — DID, IV, RDD, experimento ou Bayes)" >&2
exit 1
