# Log público sanitizado — R522 v49

Este extrato público contém apenas elementos necessários à rastreabilidade de busca e seleção, sem dados pessoais, documentos assinados ou metadados de autoria.

## Bases e strings efetivamente registradas

### DOAJ — 17/09/2026

- D1: `"legal education" AND "artificial intelligence" AND Brazil` — 2 registros.
- D2: `"ensino juridico" AND "inteligencia artificial"` — 1 registro.
- D3: `"generative AI" AND "legal education"` — 10 registros.
- D4: `"legal education" AND "generative artificial intelligence"` — 7 registros.
- D5: `"law school" AND ChatGPT AND assessment` — 2 registros.
- D6: `"educacao juridica" AND "inteligencia artificial"` — 0 registro.
- D7: `"legal education" AND "AI Act"` — 1 registro.
- D8: `"IA generativa" AND "ensino juridico"` — 0 registro.
- D9: `"ChatGPT" AND "law school" AND ethics` — 4 registros.
- D10: `"generative AI" AND "higher education" AND ethics AND law` — 5 registros.
- D11: `"legal education" AND equity AND AI` — 1 registro.

Total bruto DOAJ: 33 registros. Consolidação por título: ver `consolidacao_doaj.md` no pacote-fonte.

### OpenAlex — 17/09/2026

- O1: `search=legal education generative AI (2020-2025)` — 42.671 registros na API; amostra top-25 exportada.
- O2: `title_and_abstract:"legal education" AND "generative AI" (2020-2025, artigo)` — 25 registros.
- O3: `title_and_abstract:"ensino juridico" OR "educacao juridica" (2020-2025, artigo)` — 25 registros.

### Atualização 2026 — 18/09/2026

Arquivo de atualização OpenAlex identificou Lorteau & Sarro (2026), Schrepel (2026) e Fruehwald (2026). Dois primeiros foram tratados como literatura contextual por acesso fechado; Fruehwald ficou fora por tipo documental.

## Razões de exclusão finais

- A01: E2 — foco educacional insuficientemente central.
- B02, N03, N12: E4 — método próprio/compatível insuficiente.
- C07, N06, N09, N10, N16: E6 — texto completo não recuperado por rota legítima durante a execução.

## Concordância

Duas séries humanas independentes, anonimizadas como RH1 e RH2, produziram I/I=21, E/E=9, Po=1,000, Pe=0,580, κ=1,000. Ver errata pública anonimizada.
