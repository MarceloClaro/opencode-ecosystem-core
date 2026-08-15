# evo-60 — R429: Conformidade editorial RBEP — resumo/abstract ≤ 1.000 chars e corpo ≥ 40.000

## Objetivo

Tornar o artigo Crateús-IDEB conforme às instruções editoriais da RBEP
(educa.fcc.org.br/revistas/rbedu/pinstruc.htm) nos dois itens autorizados pelo
usuário: (1) encurtar resumo (PT) e abstract (EN) para ≤ 1.000 caracteres cada
(antes: 2.172 e 2.092); (2) expandir o corpo para ≥ 40.000 caracteres
(antes: ~30.900), detalhando método (bootstrap por cluster, correção de pequena
amostra, t(G−1), wild sob H0, MDES/TOST, deflator IPCA), expandindo a revisão de
literatura e criando subseção de limitações — **sem alterar nenhum número aprovado
no R428** e sem termos proibidos.

## Mudanças

1. `docs/ARTIGO_CRATEUS_RBEP.md`:
   - Resumo novo: 914 caracteres (≤ 1.000) preservando r=−0,24 [−0,77; 0,50],
     β=2,61 p=0,20/p wild 0,23, MDES ≈ 6,0, 107/108=99,1%, ganho 5,93, r=−0,14;
   - Abstract novo: 881 caracteres (≤ 1.000), espelhando o resumo em EN;
   - Introdução: +2 parágrafos (lacuna da escala municipal; pergunta de pesquisa
     e implicações de política);
   - §2.1: +formulação do IDEB (fluxo+proficiência, metas, diagnóstico e
     responsabilização, estreitamento de currículo);
   - §2.2: +arquitetura do PAIC (convênios, formação, material, avaliação),
     avanços concentrados em anos iniciais, hipótese de fatores institucionais;
   - §2.3: +justificativa de G pequeno e triangulação entre escalas + ressalva
     observacional/associativa;
   - §3.2: variáveis detalhadas (IDEB, log PIB real, deflator IPCA com fator de
     conversão, renda do responsável, painel, missingness);
   - §3.4: +3 parágrafos de procedimentos inferenciais (bootstrap por cluster
     passo a passo, CRVE + t(G−1), wild sob H0, MDES/TOST);
   - §4.1: +parágrafo substantivo (efeito de composição ecológica);
   - §4.5: +parágrafo substantivo (metas como projeções de convergência, ganho
     > 1/3 da escala IDEB);
   - §5: +parágrafo "leitura em duas dimensões" (r nacional como artefato de
     comparação entre contextos heterogêneos) e nova subseção
     **"5.3 Limitações e agenda de pesquisa"** (poder, G=9, proxies, causalidade,
     metas, generalização, agenda);
   - §6: +parágrafo de implicações práticas para gestores.
2. `latex/ARTIGO_CRATEUS_RBEP.tex` — espelhamento 1:1 de todas as mudanças do MD
   (resumo 974 / abstract 909 caracteres; mesmos parágrafos e subseção), com
   escapes LaTeX e sem renumeração de seções.
3. `latex/ARTIGO_CRATEUS_RBEP.pdf` — recompilado (2 passadas, sem erros).
4. `outputs/docx/` — DOCX ABNT regenerado + MANIFEST.

## Resultados (resumo)

- MD sem markdown: **41.574 caracteres** (≥ 40.000 ✓); TeX sem comandos:
  **40.315 caracteres** (≥ 40.000 ✓).
- Resumo: **914** chars (≤ 1.000 ✓); Abstract: **881** chars (≤ 1.000 ✓).
- Termos proibidos (R426/R428): 0 ocorrências em MD e TeX.
- Números R428 intocados: verificação `verificar_consistencia_manuscrito_r428.py`
  → CONSISTÊNCIA OK; suíte R42: **125 passed**.

## Verificação

- `verificar_consistencia_manuscrito_r428.py`: CONSISTÊNCIA OK.
- `pytest tests/ -k "r42 or r428"`: 125 passed.
- `pdflatex` 2 passadas: exit 0; PDF 1.029 KB.
- Contagem de caracteres por script dedicado (MD sem markdown; TeX sem comandos).

## Lições

- **Contagem de caracteres RBEP é sobre o corpo total:** o limite de 1.000
  caracteres para resumo/abstract é apertado — o rascunho precisa priorizar os
  números-chave (r entre, β FE, MDES, H3, ganho) e renunciar a detalhes
  (IC95 completo, p exato de cada teste, n de cada análise).
- **Espelhamento MD↔TeX exige âncoras por início de linha no TeX:** linhas longas
  (> 2.000 chars, truncadas pelo read) e comandos `\textbf` no começo da linha
  quebram âncoras de substituição; validar com buscas de trechos-chave nos dois
  arquivos.
- **O TeX conta menos caracteres "limpos" que o MD** (40.315 vs 41.574) por
  comandos de controle — a margem de segurança (~1,3 mil) é suficiente, mas
  expansões futuras devem ser medidas nos dois formatos.
- **Pendências de submissão RBEP ainda em aberto** (não autorizadas nesta rodada):
  versão anonimizada `_BLINDED`, dados do autor ao final, declaração de
  financiamento/conflito, carta de submissão, formatação final (Times 12,
  entrelinha simples) — registrar no próximo ciclo.
