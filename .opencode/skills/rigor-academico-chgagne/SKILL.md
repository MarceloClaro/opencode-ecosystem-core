---
name: rigor-academico-chgagne
description: Revise fontes acadêmicas com identificador persistente, bibliografia
  invertida, claims com evidência e provas que degradam explicitamente. Use para revisão
  de papers, checagem de citações e derivações; não inventa DOI, não copia texto e
  não substitui revisão humana.
metadata:
  round: R1049
  source: https://github.com/chgagne/claude-skills-research
  license: MIT
  adaptation: Adaptação textual original inspirada em chgagne/claude-skills-research
    (commit 3f50d620d3d5a8d5c97aa1cdd5d5b04ca1c2a92b); sem cópia de scripts.
---

# Rigor acadêmico — adaptação seletiva

## Regra de ouro

Uma citação só existe quando um identificador persistente resolve para um
registro que corresponde ao texto citado. Memória do modelo não é fonte.
Similaridade de título não é verificação.

## Fluxo de revisão

1. **Delimitar** — pergunta, escopo, fontes incluídas/excluídas e data de busca.
2. **Coletar** — DOI, PMID, arXiv, ISBN ou URL estável; registrar acesso.
3. **Inverter a bibliografia** — resolver o identificador e comparar o registro
   de volta contra autor, ano, título, veículo, volume, páginas e DOI.
4. **Ler com claims** — cada afirmação recebe evidência, localização e força.
5. **Buscar contraexemplos** — explicação rival, viés de seleção, resultado
   negativo e limite de generalização.
6. **Verificar prova/derivação** — passo simbólico, unidade, hipótese e o que
   não foi checado.
7. **Entregar** — achados, incerteza, lacunas, referências e o que exige humano.

## Gates

- Sem identificador resolvido → `NÃO VERIFICADO`.
- DOI que não resolve ou aponta para outro título → bloquear.
- Citação literal sem localização → não usar como prova.
- Prova simbólica sem checker → declarar `UNVERIFIED`; não arredondar para
  "provado".
- Revisão por IA não é decisão editorial; diversidade de um único modelo é
  limitada.

## Saída

Tabela de claims com `claim`, `evidence`, `locator`, `status`, `limit`.
Referências em ABNT/APA conforme o destino, sempre a partir do registro
resolvido, nunca de memória.
