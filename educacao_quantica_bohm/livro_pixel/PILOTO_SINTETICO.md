# Piloto sintético do protocolo de avaliação {#piloto-sintetico}

> **Status:** simulação sintética concluída; **não** é estudo de eficácia, não
> usou LLM/OASIS e não coletou dados humanos. O resultado serve para ajustar o
> protocolo antes do CEP.

## 1. O que foi executado

O protocolo `AVALIACAO_EFICACIA.md` foi submetido ao motor acadêmico local R920
(`academic.adversarial_research.simulation`), com:

- 7 etapas: projeto, metodologia, qualificação, análise, resultados,
  pré-defesa e defesa;
- 3 cenários: base, banca divergente e fonte indisponível;
- 21 casos, 42 rounds, 84 ações;
- 6 participantes sintéticos por caso;
- seed 42;
- limites: 64 rounds, 512 ações, 30 s.

O motor é **determinístico e baseado em regras**. Não há LLM, OASIS, agentes
reais ou dados de estudantes. O relatório completo está em
`outputs/piloto-avaliacao/RELATORIO_PILOTO.md`; o resumo está em
`outputs/piloto-avaliacao/RESUMO.json`.

## 2. Resultado operacional

| Métrica | Valor |
|---|---:|
| Status | `completed` |
| Revisão | `needs_revision` |
| Casos | 21 |
| Rounds | 42 |
| Ações | 84 |
| Perguntas | 196 |
| Objeções não resolvidas | 8 |
| Trajetória SHA-256 | `0fbaaed5de26ac45de5f828799beef7fbf72502b86442174938c9a9a736a645f` |

`needs_revision` não é fracasso do livro: é o resultado esperado de um ensaio
que encontra perguntas sem resposta pronta. O piloto não aprova e não reprova;
ele lista o que precisa ser explicitado.

## 3. As 8 objeções e o ajuste

| Objeção | O que faltava | Onde foi corrigido |
|---|---|---|
| Perguntas ou interpretações alternativas | rivais explícitos | `AVALIACAO_EFICACIA.md`, seção 9.1 |
| Genealogia e limites dos conceitos | definições operacionais | seção 4.1 |
| Análise de interpretações rivais | critérios de distinção | seção 9.1 |
| Critérios de seleção | seleção de escolas e turmas | seção 3.3 |
| Precedências e prazos | cronograma com dependências | seção 11.1 |
| Disponibilidade de recursos | recursos mínimos | seção 11.2 |
| Contingências | plano de contingência | seção 11.3 |
| Aderência institucional | governança e cartas | seção 11.4 |
| Fonte indisponível | plano de dados e fontes | seção 11.5 |

## 4. O que o piloto não prova

- Não prova que o livro ensina.
- Não produz effect size, retenção ou equidade.
- Não substitui CEP, consentimento ou assentimento.
- Não é peer review.
- Não generaliza para estudantes brasileiros.
- Não valida a interpretação de Bohm.

## 5. O que o piloto prova

- O protocolo é **executável em 21 casos sintéticos**.
- O motor encontrou **8 lacunas de explicitação** antes da coleta.
- O protocolo pode ser **revisado e versionado** antes do CEP.
- O pipeline de perguntas e objeções é **reproduzível** pela seed e pelo hash.

## 6. Como reproduzir

```bash
python3 scripts/run_piloto_avaliacao.py
```

Saídas:

```text
outputs/piloto-avaliacao/plano.json
outputs/piloto-avaliacao/resultado.json
outputs/piloto-avaliacao/RELATORIO_PILOTO.md
outputs/piloto-avaliacao/RESUMO.json
```

## 7. Próximo passo

1. Levar a versão 1.1 ao CEP.
2. Pilotar os instrumentos com 30 estudantes fora da amostra.
3. Corrigir clareza e tempo.
4. Pré-registrar no OSF.
5. Executar a coleta com 440 estudantes.
6. Analisar com equipe independente.
7. Publicar resultados — positivos ou negativos.

> **Regra:** o piloto sintético é um ensaio de palco, não a peça. Ele ensina a
> entrar em cena; não prova que o público vai aplaudir.
