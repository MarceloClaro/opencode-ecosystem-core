# SPEC-BOHM-PIXEL-001 — Do Bit ao Todo: 3000 laudas de física quântica (edição pixel bilíngue)

**Status:** implementado e verificado localmente
**Versão:** 1.2
**Data:** 2026-11-07
**Orquestrador:** marceloclaro (OpenCode Ecosystem Core)
**Natureza:** especificação local de projeto editorial

---

## 1. Contexto

A obra anterior (Bohm na Escola, edição black, 54 páginas) precisava escalar para
um formato **nanoescalável**: 3000 laudas independentes, cada uma em um arquivo
separado, compiladas em um **PDF navegável**, com **design editorial pixel
pixel**. O corpo do texto deveria ser legível (não pixel); menus, capítulos,
títulos e subtítulos deveriam manter a fonte pixel. As ilustrações científicas
deveriam vir de **scripts práticos quânticos** (PennyLane, Cirq, Qiskit, NumPy) e
de **resultados de backend** (Guoji08/Baihua). A edição 1.1 acrescenta uma
**ponte sonora de mandarim** no meio de cada lauda e circuitos **OpenQASM 2.0**
para o editor da Tiangong.

## 2. Objetivos

- O1. Produzir 3000 laudas, 100 conceitos × 10 lentes × 3 níveis (N0, N1, N2).
- O2. Manter cada lauda em um arquivo Markdown separado.
- O3. Compilar um PDF A5 navegável, com marcadores e mapa de links.
- O4. Aplicar design pixel: corpo legível, títulos/menus em pixel.
- O5. Gerar figuras científicas por scripts executáveis.
- O6. Registrar resultados reais de GHZ e VQC no Guoji08, com limites.
- O7. Integrar CIQuanta, Tiangong, `gjq-client` e servidor MCP.
- O8. Não armazenar API key em arquivos do projeto.
- O9. Verificar por teste automatizado.
- O10. Integrar 100 termos chineses com pinyin, tons e microfrases.
- O11. Gerar circuitos OpenQASM 2.0 para o editor da Tiangong.
- O12. Distinguir o rótulo do console (`Guoji No.8 (simulate)`) da API (`Guoji08`) e verificar `simulator=False` (hardware).
- O13. Dar a cada um dos 100 conceitos um experimento com simulado e backend.

## 3. Requisitos funcionais

| ID | Requisito | Critério de aceitação |
|---|---|---|
| RF01 | 3000 laudas + 100 fichas | 3000 arquivos `secoes/NNNN_*.md` + 100 `fichas/FNNN_*.md` |
| RF02 | Seções separadas | Um arquivo por lauda, editável de forma independente |
| RF03 | PDF A5 | ≥ 3000 páginas; 3000 rodapés `LNNNN/3000` |
| RF04 | Navegação | Marcadores PDF para partes e laudas; mapa com links e páginas |
| RF05 | Design pixel | Títulos/menus em Press Start 2P; corpo em Atkinson Hyperlegible |
| RF06 | Figuras por código | Figuras científicas geradas por `gerar_ilustracoes.py` e `gerar_resultados_reais.py` |
| RF07 | Resultados reais | JSON do GHZ (1024 tiros) e VQC (4 pontos, 1024 tiros) |
| RF08 | Nuvem | Seção com CIQuanta, Tiangong, QASM 2.0, `gjq-client`, MCP |
| RF09 | Segurança | Nenhuma API key literal no repositório |
| RF10 | Verificação | Teste automatizado verde |
| RF11 | Ponte sonora | Cada lauda tem um parágrafo `PONTE SONORA` no meio do corpo |
| RF12 | Bilíngue | Cabeçalho, rótulos, partes e glossário com hanzi/pinyin |
| RF13 | QASM/Tiangong | 10 arquivos QASM 2.0 válidos em `circuitos_qasm/` |
| RF14 | Script de nuvem | `executar_nuvem.py` com GHZ, QASM, VQC e CHSH, task IDs e JSON |
| RF15 | Rótulo honesto | Texto distingue API, console e `simulator=False` (hardware) |
| RF16 | 100 experimentos | 18 circuitos-base cobrem os 100 conceitos, com simulado e backend |
| RF17 | Relatório | `dados_experimentos/RELATORIO_EXPERIMENTOS.md` com 100 linhas |
| RF18 | Anexo Qualis A1 | Parecer crítico do estudo de VQC com ruído benéfico, com validação 2/4 qubits |
| RF19 | Fichas com DOI | 100 fichas com fonte primária, DOI/URL verificado, prática e grau de evidência |
| RF20 | SWAP test | QASM, simulação e backend com P(0) e sobreposição |
| RF21 | Calibração | CSV do operador e figura T1/T2/fidelidade/frequência |
| RF22 | Oficina de scripts | 18 experimentos com código, linha a linha, cálculo e resultado |
| RF23 | Capítulo CE/PB/GJQ | Ceará, Paraíba, CIQuanta e justificativa do GJQ |
| RF24 | Suíte de Bloch | 6 estados × 3 bases, simulação e hardware |

## 4. Não objetivos

- Não são 3000 ensaios independentes: são 100 conceitos × 10 lentes × 3 níveis, gerados a
  partir de uma base curada.
- Não há treino de VQC no hardware; o modelo foi treinado no simulador e apenas
  avaliado no Guoji08.
- Não há replicação estatística do estudo de ruído benéfico.
- Bohm é interpretação, não consenso; a ordem implicada é filosófica.

## 5. Arquitetura

```
educacao_quantica_bohm/
├── livro_pixel/
│   ├── abertura_capa.md, abertura.md, MAPA.md, fecho.md
│   ├── ARQUITETURA_LEITURA.md, SUMARIO.md, HISTORIA_BOHM.md
│   ├── LABORATORIO_LEITOR.md, GABARITO.md, BLOCH_SUITE.md
│   ├── partes/parte_01..10.md (legado do volume 1000)
│   ├── secoes/0001..3000_*.md
│   ├── niveis/nivel_0..2.md
│   ├── base/base_parte1..5.py
│   ├── base/base_chines.py
│   ├── base/base_experimentos.py
│   ├── base/base_notas.py
│   ├── GLOSSARIO_CHINES.md
│   ├── scripts/pixel_art.py
│   ├── gerar_secoes.py
│   ├── build_pixel_fast.py
│   ├── gerar_manual_leitor.py (em scripts/)
│   ├── gerar_figuras_laboratorio.py (em scripts/)
│   ├── gerar_circuitos_leitor.py (em scripts/)
│   ├── estilo_pixel.css
│   ├── fontes/
│   ├── capa_livro.png (CAPA/CAPA.png)
│   ├── sprites/
│   └── LIVRO_3000_LAUDAS.pdf/html
├── scripts/gerar_ilustracoes.py
├── scripts/gerar_figuras_niveis.py
├── scripts/gerar_resultados_reais.py
├── dados_hardware/*.json
├── circuitos_qasm/*.qasm
├── ANEXO_QUALIS_A1.md
├── FICHAS.md
├── fichas/F001..F100_*.md
├── dados_qualis/*.json
├── dados_referencias/*.json
├── dados_experimentos/*.json
├── scripts/gerar_qasm.py
├── scripts/experimentos_100.py
├── scripts/validar_vqc_rapido.py
├── scripts/analise_vqc_ruido.py
├── scripts/gerar_fichas.py
├── scripts/verificar_dois.py
├── scripts/executar_nuvem.py
├── notebooks/AULA_BOHM_LABORATORIO.ipynb
├── livro/LIVRO_BOHM_BLACK.pdf (edição compacta)
└── tests/test_pixel_book.py
```

## 6. Critérios de aceitação globais

- CA01. 3000 seções, 100 conceitos, 10 lentes e 3 níveis.
- CA02. PDF com ≥3000 páginas e 3000 códigos de lauda únicos.
- CA03. Marcadores PDF para partes e laudas.
- CA04. Mapa com 100 links e números de página.
- CA05. Figuras científicas existentes e geradas por scripts.
- CA06. JSON do GHZ e VQC com somas/acuracidade coerentes.
- CA07. Nenhuma API key literal.
- CA08. Teste automatizado verde.
- CA09. 3000 laudas com ponte sonora e 100 termos chineses únicos.
- CA10. Glossário chinês com 100 linhas e links.
- CA11. 10 QASM válidos para o editor da Tiangong.
- CA12. Nenhum texto chama o resultado de “hardware” sem confirmar o rótulo do console.
- CA13. 18 experimentos com simulado e backend; 100 conceitos cobertos.
- CA14. Cada lauda de prática com caixa `RESULTADO · SIMULADO × BACKEND`.
- CA15. Anexo Qualis A1 com crítica estatística e validação 2/4 qubits.
- CA16. 100 fichas com DOI/URL verificado e prática.
- CA17. 44 DOIs verificados em Crossref/DataCite; 5 URLs oficiais sem DOI.
- CA18. SWAP test com P(0) e sobreposição simulada/backend.
- CA19. Calibração do backend documentada com fonte e limites.
- CA20. Oficina de scripts com 18 experimentos e cálculo matemático explícito.
- CA21. Capítulo Ceará/Paraíba/GJQ com fontes e limites.
- CA22. Suíte de Bloch com vetores simulados e de hardware.

## 7. Riscos

| Risco | Mitigação |
|---|---|
| 3000 laudas virarem repetição | 100 conceitos × 10 lentes × 3 níveis; voz e evidência mudam por nível |
| PDF lento para compilar | Montagem direta de HTML (sem Pandoc nas 3000 seções); build em ~3 min |
| Fonte pixel ilegível no corpo | corpo em Atkinson; pixel só em títulos/menus |
| Figura científica virar desenho manual | script obrigatório e página “Figuras e scripts” |
| Resultado de hardware superinterpretado | página “Caderno de resultados” com limites |
| API key vazar | chave só em variável de ambiente; teste de varredura |
| 4 pontos virarem “prova” | texto explícito: 4/4 não é generalização |
| Chinês virar tradução automática | base curada de 100 termos; pinyin e tons revisáveis; limite declarado |
| Console `(simulate)` virar “hardware” | verificação `simulator=False` + caveat de calibração |
| QASM não rodar no editor | validação local com `qiskit.qasm2.loads`; passo a passo e limites |
| 100 experimentos únicos inviáveis | 18 circuitos-base compartilhados; leitura por conceito |
| sobreposição virar “fidelidade” | texto e teste distinguem as métricas |

## 8. Verificação

```bash
.venv-quantum/bin/python -m pytest educacao_quantica_bohm/tests/test_pixel_book.py -v
```

## 9. Definição de pronto

- [x] Base de 100 conceitos.
- [x] 3000 laudas em arquivos separados, em três níveis.
- [x] PDF A5 navegável com 3550 páginas (3000 laudas + 400 notas de cálculo + 100 fichas + arquitetura, sumário, história de Bohm, sobre o autor, manual do leitor, código dos 18 experimentos, trilhas por nível, verificação em Lean 4, pacote de publicação, mapas, glossário, relatório e fecho).
- [x] Design pixel com corpo legível.
- [x] Figuras por scripts e resultados reais.
- [x] Seção CIQuanta/Tiangong/MCP.
- [x] Teste automatizado.
- [x] Ponte sonora em 3000 laudas e glossário de 100 termos.
- [x] QASM 2.0 para Tiangong e script de nuvem.
- [x] Verificação `simulator=False` (hardware) e caveat do rótulo `(simulate)`.
- [x] 18 experimentos com simulado e backend, cobrindo 100 conceitos.
- [x] Relatório de experimentos e caixa de resultado em cada prática.
- [x] Anexo Qualis A1 com validação 2/4 qubits e crítica de phase damping.
- [x] 100 fichas de evidência e 44 DOIs verificados.
- [x] Nenhuma chave literal.