# SPEC-935-R207 — Revisão, Auditoria e Correções dos Volumes 2–5

**Status:** EM EXECUÇÃO
**Ciclo de evolução:** R207 (correções) → registro R509 (evolution registry)
**Escopo:** `livro-alfabetizacao/Volume2/*.tex`, `Volume3/main.tex`, `Volume4/main.tex`, `Volume5/main.tex`

## Contexto

O Volume 1 (v4.9, 636 pp) passou pelo ciclo completo de auditoria-correção (SPEC-935-R206, R508).
O usuário solicitou: **"auditar/corrigir os Volumes 2-5 com o mesmo protocolo"** (SPEC → script
reproduzível → compile 2x → verificação → registro). Este ciclo R207 executa a auditoria já
realizada (parecer consolidado entregue) e aplica as correções aprovadas.

## Objetivo

Entregar os Volumes 2–5 corrigidos (v1.1) com:
- 0 erros factuais, typos, palavras inventadas ou anglicismos não intencionais;
- 0 erros de compilação (exit 0 nas duas passadas de pdflatex);
- 0 "Missing character";
- consistência metodológica (Pausa/Pista neuroinclusiva; uso honesto da Técnica da Boquinha;
  colunas CAEd/BNCC/SPAECE sem mistura de matrizes);
- exercícios por letra no Volume 2 (L2–L8) e folha 3.2 no Volume 3, seguindo padrões já existentes
  no próprio livro (sem criação de conteúdo novo fora dos padrões).

## Critérios de aceitação (gate SDD)

- [ ] AC1: `\RequirePackage{amssymb}` adicionado aos mains do V2, V3 e V5 (uso de `$\square$`).
- [ ] AC2: V2 parte1: "Reconhecher" x2 → "Reconhecer"; "fogo, fogo" → "fogo, fada".
- [ ] AC3: V2 parte2: `\sil{DENTE}{DO}` → `\sil{DE}{DO}`; "BONÉDIA" → "BONITO";
      "O que o gosta" → "O que o gato gosta"; "feta" → "fada".
- [ ] AC4: V2 parte2: exercício (reconhecimento/produção/leitura) inserido nas lições 2–8,
      com palavras reais e separação silábica correta.
- [ ] AC5: V2 parte2: uma caixa "Pausa Neuroinclusiva + Pista" por unidade (5 unidades).
- [ ] AC6: V2 parte3: folhas renumeradas (2.1, 2.2 B, 2.3 Formação); cabeçalho SPAECE → BNCC;
      descrição CAEd D1–D5 padronizada ("palavras, frases, textos, produção, consciência fonológica").
- [ ] AC7: V2 parte4: "introducing frases" → "introduzir frases".
- [ ] AC8: V2 parte5: "scrapy, magneticos" → "feltro, imantadas"; cronograma alinhado às
      revisões realmente existentes (sem citar Revisão 2/3 inexistentes).
- [ ] AC9: V2 referencias: bibitem SPAECE → SEDUC-CE (não FUNCAP/SAEB).
- [ ] AC10: V3: "TR" duplicado removido; "GH" removido dos dígrafos.
- [ ] AC11: V3: inventadas corrigidas (BRACO→BRAÇO, FRATE→FRACO, GRACO→GRATO, nhanha→pinha,
      dóu→dou, outage→roupa, bou→boi, pedrei→leite/papel, voi→foi, palau→pau, peú,EU→céu,
      loudly removido, mão removido de OU, edia→saia/folia, fire removido, tui→viu/caiu/partiu).
- [ ] AC12: V3: RR/SS/LH/NH ensinados conforme a língua (RR/SS/LH/NH não iniciam palavras;
      exemplos intervocalicos; CH pode iniciar). `\dig{RR}{A}` etc. removidos; "rato" removido
      dos exemplos de RR; boquinha do LH adicionada.
- [ ] AC13: V3: `\dig{LÁ}{I}` removido; linha de palavras do AI corrigida (pai, cai, mãe, mais, pais).
- [ ] AC14: V3: folha 3.2 (grupo 2 de compostas) adicionada; códigos V3-A-V3-C renumerados
      sequencialmente (A-01..A-04, C-05, C-06); títulos 3.4→3.3 e 3.6→3.4.
- [ ] AC15: V3: tabela de dígrafos do apêndice com coluna "Como aparece" e sem LH/RR/SS iniciais;
      tabela de ditongos reescrita com exemplos reais.
- [ ] AC16: V4: "des-animar" → "pré-história"; "caixa d'água, girassol" → "guarda-chuva, segunda-feira".
- [ ] AC17: V4: nível V4-B-01 → "Alfabético".
- [ ] AC18: V4: nota metodológica sobre o uso da Boquinha no volume + caixa Pausa/Pista
      articulatória na Unidade 3.
- [ ] AC19: V5: "MAKE predictions" → "fazer previsões"; "Durante a ler" → "Durante a leitura";
      "(página XX)" → "(ver a Avaliação Final do 5º Ano)".
- [ ] AC20: V5: regra "KC" substituída por C/QU (C antes de A/O/U = /k/; QU antes de E/I = /k/)
      + SS/Ç; "/sh/" → "/ʃ/"; exemplo S/Z explicitado (casa, rosa; exame com X).
- [ ] AC21: V5: nota metodológica Boquinha + caixa Pausa/Pista na Unidade 3.
- [ ] AC22: V3/V4/V5: bibitem SPAECE → SEDUC-CE.
- [ ] AC23: Compilação: `pdflatex -interaction=nonstopmode main.tex` 2x por volume → exit 0,
      0 Missing character (baseline de overfull preservado ou reduzido).
- [ ] AC24: Verificação `pdftotext` confere palavras-chave corrigidas (braço, fraco, grato, céu,
      boi, guarda-chuva, C/QU, pausa neuroinclusiva, etc.).
- [ ] AC25: PDFs v1.1 entregues em `C:\Users\marce\Downloads\Alfabetizar_Bem\`.
- [ ] AC26: Ciclo registrado no EvolutionRegistry (R509) com lições.

## Restrições

- Sem inspeção visual de PDF; verificação por logs + `pdftotext`.
- Sem reestruturação dos mains V3–5 (arquivo único mantido).
- Sem promessas/overclaim: as notas metodológicas explicitam onde a Boquinha é usada (V5, V4)
  sem afirmar aplicação plena.
- IPA: símbolos restritos a rótulos simples (ex.: /ʃ/), fora de `\textipa{}`.
- Backups em `/tmp/opencode/*_r207_backup.tex`; script idempotente.

## Verificação final

Script `r207_correcoes_volumes_2_5.py` aplica todos os patches com verificação de ocorrência
única esperada; falha de ancoragem interrompe o ciclo (fail-closed).