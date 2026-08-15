# evo-49 — R418: Caso brasileiro em perspectiva comparada

## Objetivo

Atender ao pedido do usuário de analisar o Brasil e compará-lo com as
emergentes asiáticas, EUA, Europa e China, dentro do artigo RBEP, sem alterar
a amostra principal de 135 países.

## Mudanças

1. **Achado crítico verificado**: o Brasil está ausente da amostra principal
   por limitação de cobertura do WDI (matrícula terciária `SE.TER.ENRR` só
   reportada a partir de 2012; 11 observações não nulas < limiar de 20) — não
   por decisão analítica. Confirmado por consulta direta à API oficial do
   World Bank (12 não nulos, 2012–2024).
2. **Análise de sensibilidade de limiar** (funções oficiais do
   `analyze_expanded.py`): limiar ≥20 → 135 países (ρ níveis 0,751; ρ 1ª dif
   0,146); ≥15 → 153 (0,738/0,149); ≥10 → 173 (0,733/0,155, inclui BRA, DEU,
   JPN, NLD, CAN, SGP, NZL, AUT). Pipeline completo com ≥10: FE coef 0,112
   (p=0,285; 124 clusters; n=1307); ML AUC 0,695/0,606. **Decisão: manter a
   amostra de 135 e tratar o Brasil como estudo de caso** (janela 2012–2022),
   pois a opção de limiar reduzido mudaria todos os números do artigo e
   quebraria a cadeia R408–R414; o Brasil continuaria com apenas 11 anos.
3. **Divergência de dados entre turnos resolvida**: o painel processado atual
   é a fonte de verdade oficial — reproduz a proveniência do artigo (ρ níveis
   0,751, n=4374) e a suíte R408–R414 estava 120/120 verde. Os valores do
   turno anterior (CHN 2022=60,8; USA 2012=87,1; DEU 2012=60,5) provinham de
   uma versão obsoleta do cache; o cache vigente foi validado contra a API
   oficial (BRA 43,834→61,000; CHN 71,580; USA 79,362; DEU 77,366).
4. **Seção 4.8 "O caso brasileiro em perspectiva comparada"** no MD canônico e
   espelhada no TeX, com Tabela 8: Brasil (43,834→61,000; Δ+17,166 p.p.;
   PIB pc −0,149%/ano), renda média asiática (34,333→47,788; +13,455; 3,579%),
   EUA (88,726→79,362; −9,364; 1,811%; janela 2013–2022), Europa Ocidental
   (65,575→78,773; +13,199; 1,063%), China (29,308→71,580; +42,272; 5,814%).
5. **Cobertura desbalanceada declarada e tratada sem imputação**: EUA/DEU
   iniciam em 2013, PRT em 2015, VNM com lacunas; crescimento médio anual
   calculado sobre o número real de anos (ano_fim − ano_inicio).
6. **Proveniência fechada** `outputs/expanded/provenance_r418.json` + tabela
   `tabela8_brasil_comparado.csv` gerados por
   `scripts/analyze_brasil_comparativo.py` (sha256 dos 3 JSONs crus + meta).
   Inclui resíduo do Brasil na relação global de níveis (+0,318; n=1462) e
   Spearman de primeiras diferenças intra-Brasil (0,418; p=0,229; n=10).
7. **Bug corrigido no pipeline**: indicador `NY.GDP.PCAP.KD.ZG` já vem em
   percentual; o script multiplicava por 100 (gerava crescimentos de 379%);
   removido o fator e os valores passam a bater com os níveis.
8. **Teste R418** (`tests/test_r418_caso_brasil.py`, 26 testes): script +
   proveniência + tabela presentes; valores-chave do Brasil e grupos com
   tolerância 0,005; seção 4.8 no MD e TeX; anti-overclaim (word-boundary);
   números da seção ancorados na proveniência; PDF compilado.
9. **Ajuste do teste de números**: separador de milhar "1.462" (n=1462)
   normalizado no gate de âncoras (ponto seguido de exatamente 3 dígitos = 
   milhar, não decimal).

## Evidências de validação

- Suíte R408–R418: **146/146 passed** (R418: 26; R408/R410/R412/R413 sem
  regressão — 120 pré-existentes).
- PDF recompilado: `latex/ARTIGO_RBEP_SUBMISSAO.pdf` (0 erros, seção 4.8 +
  Tabela 8 com label `tab:brasil`).
- Cache de dados validado contra a API oficial do World Bank em
  2026-08-14 (BRA/CHN/USA/DEU batem exatamente).

## Lições registradas

1. Sempre validar o cache de dados contra a fonte externa antes de
   reutilizar números de turnos anteriores; `data/` é gitignored e pode ser
   regenerado entre sessões.
2. Cobertura desbalanceada de janela não deve ser "resolvida" com imputação;
   declarar a janela real por unidade e calcular crescimento com o número
   efetivo de anos é mais honesto e auditável.
3. Indicadores WDI de crescimento (`*_ZG`) já vêm em percentual; multiplicar
   por 100 gera valores absurdos que passam despercebidos se não comparados
   aos níveis.
4. Gate de âncoras numéricas precisa normalizar separadores de milhar antes
   de comparar (senão "1.462" vira 1,462 e quebra falsamente).

## Pendência humana

- Revisão humana do texto da seção 4.8 e da Tabela 8 antes da submissão à
  RBEP (janela 2012–2022, resíduo e leitura descritiva).
- Submissão à revista permanece ação humana (fora do escopo do ecossistema).
