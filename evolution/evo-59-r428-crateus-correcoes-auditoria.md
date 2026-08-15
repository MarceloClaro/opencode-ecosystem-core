# evo-59 — R428: Correções completas da auditoria Qualis A1 do artigo Crateús-IDEB

## Objetivo

Aplicar todas as correções P0/P1/P2 apontadas pela auditoria Qualis A1 (QA 6,5/10;
consistência 7,5/10; honestidade 8,0/10; blind peer review: MAJOR REVISION com
risco de REJECT) ao artigo "Desenvolvimento educacional em microrregião do
Semiárido cearense", mantendo auditabilidade e anti-overclaim; re-auditar e fechar
com veredito de aprovação.

## Mudanças

1. `specs/SPEC-935-R428-crateus-correcoes-auditoria.md` — 7 critérios de aceitação,
   tabela com 20 achados → implementação, entregáveis e decisões registradas.
2. `scripts/analise_crateus_r428.py` — reanálise completa: between com IC95%
   bootstrap por cluster; níveis pooled com bootstrap por cluster; primeiras
   diferenças; FE município×etapa+ano com erros clusterizados, t(G−1) e **wild
   cluster bootstrap sob H0** (resíduos restritos; p=0,2302 consistente com
   p_cluster_t=0,2033); lags 0–4; H3 por ano (mesmo ano de referência);
   TOST SESOI ±0,5; MDES traduzido por +10% do PIB real; missingness; LOOCV
   **interno**; jackknife; deflação IPCA (IPEA Data PRECOS12_IPCA12).
3. `data/processed/ipca_medias_anuais.json` — deflator (1680 registros; médias
   anuais 1979–2022; fator 2021/ano). Deflação mudou materialmente: pooled r micro
   0,487 (nominal R426) → **0,159** (real); between negativo (−0,2374).
4. `outputs/expanded/resultados_r428.json` + `provenance_r428.json` — números
   oficiais do ciclo (n=108; 9 clusters; FE β=2,61 IC[−1,73;6,95] p_cl=0,20,
   p_wild=0,23; MDES 6,01/0,57; TOST ±0,5 p=0,85; H3 107/108=99,1%; LOOCV 9/9
   média 0,44; missingness 0,5/1,3/26,2%).
5. `docs/ARTIGO_CRATEUS_RBEP.md` + `latex/ARTIGO_CRATEUS_RBEP.tex` — manuscrito
   reescrito por completo (grafia Crateús; resumo/abstract novos; between como
   dimensão transversal; LOOCV interno; H3 ano a ano; PIB real; TOST/MDES; lags;
   missingness; referências com paginação real verificada; PAIC "Aprendizagem"
   como variação do título de Cruz et al. com nota; "agreed target").
6. `latex/ARTIGO_CRATEUS_RBEP.pdf` (compilado, 2 passadas) + `outputs/docx/`
   (DOCX ABNT regenerado + MANIFEST).
7. `scripts/verificar_consistencia_manuscrito_r428.py` — assert de que 100% dos
   números-chave do manuscrito reproduzem o JSON, incluindo a **Tabela 4 inteira**
   contra `ai_2021_detalhe`.
8. `tests/test_r428_crateus_correcoes.py` — 20 testes (between, pooled, FE,
   wild, MDES/TOST, H3, LOOCV interno, lags, IPCA, proveniência, Tabela 4,
   anti-overclaim, missingness).
9. `requirements.txt` — dependências do paper.

## Resultados (resumo)

- **Micro (n=108, 9 clusters, lag 2, PIB real):** between r=−0,24 (IC[−0,77;0,50],
  p=0,52); pooled r=0,16 (IC[−0,06;0,42], p_cl=0,14); 1ª dif r=−0,07 (p=0,50);
  FE β=2,61 (SE_cl 1,88; IC[−1,73;6,95]; p_cl_t=0,20; p_wild=0,23); MDES 6,01
  (0,57 por +10% PIB); TOST ±0,5 p=0,85; H3 107/108=99,1% (desvio: Ipaporanga
  2013); LOOCV interno 9/9, média 0,44; lags 0–4 pooled 0,16–0,26.
- **Ceará/Brasil:** CE pooled r=0,10 (p_cl=0,01); BR pooled r=0,42 (p<0,001);
  BR FE β=0,11 (p<0,001).
- **Referências:** 17/17 validadas externamente (paginação real; Lacruz et al.
  corrigido para Revista Brasileira de Educação; Carnoy et al. CER 61(4) 726–759;
  Cito & Marôco LSAE 14 art. 30).
- **Re-auditoria delta:** APROVADO COM RESSALVAS → APROVADO (9,5/10 honestidade;
  3 P3 de redação aplicados; nenhum P0/P1 remanescente).

## Verificação

- Suíte R428: 20 passed; subset R42 (R423+R425+R426+R427+R428): **125 passed**.
- `verificar_consistencia_manuscrito_r428.py`: CONSISTÊNCIA OK.
- PDF compilado sem erros; DOCX regenerado com 10 tabelas com bordas.
- Scanners MCP: heurísticos calibrados para RCT — não reconhecem estudo
  observacional robusto; registrado como limitação da ferramenta (merkle OK).

## Lições

- **Wild cluster bootstrap com G=9 exige reamostragem sob H0** (resíduos
  restritos): a versão sob alternativa produzia t_wild até −704 (p=0,0 espúrio);
  sob H0, p=0,23 consistente com t(G−1).
- **Deflação importa:** PIB nominal vs real mudou o pooled micro de 0,487 para
  0,159 — corrigir antes de publicar; FE com efeito de ano absorve fatores
  nacionais (IPCA não altera β do FE).
- **Auditores em loop precisam de fontes verificáveis:** "ano final, 2013" e
  "0,1 ponto" sem etapa/gap no JSON geraram flag P2; manter JSON completo.
- **Erro de cópia de linha em tabela:** 7,2/6,7 (valores de Nova Russas/
  Independência trocados por linha) só foi pego por validação célula a célula
  contra o JSON — testes de paridade tabela↔JSON são obrigatórios.
- **Título de obra é fiel à fonte:** "Aprendizagem na Idade Certa" no título de
  Cruz et al. (2022) vs nome legal "Alfabetização" (Lei 14.026/2007) — nota
  explícita evita flag de inconsistência.
- **"Atingiu" ≠ "superou":** Quiterianópolis empatou meta 2021 (5,9=5,9);
  "superaram" excedia o dado.
