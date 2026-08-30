# Recibo local de validação — SPEC-935-R456

## Escopo

Este recibo registra a produção do **manual técnico** da arquitetura RAG do
ecossistema, em formato de banca de doutorado, compilado em PDF. O manual é
**modular**: cada seção vive em um arquivo `sec_XX_*.tex` separado, incluída pelo
documento-mestre `main.tex` via `\input`, o que permite aprofundar uma seção
isoladamente e recompilar o PDF único (`main.pdf`).

O manual passou por um **aprofundamento didático de rigor progressivo** (níveis
N0=intuição, N1=aplicação, N2=pós-graduação), enriquecido com *insights* de
engenharia extraídos do código-fonte real, e ganhou uma **nova Seção 2
"Problema de Pesquisa e Impactos"** com formulação formal (PP, 4 RQs, hipótese
H1) e impactos na ciência e no ecossistema.

## Autoria

| Campo | Valor |
|---|---|
| Autor | Marcelo Claro Laranjeira |
| ORCID | `0000-0001-8996-2887` |
| E-mail | `marceloclaro@gmail.com` |

A autoria aparece na capa e na folha de rosto do PDF.

## Ambiente registrado

| Campo | Valor observado |
|---|---|
| Base Git (`git rev-parse HEAD`) | `dd33f4f` (antes do novo aprendizado) |
| Estado do checkout | arquivos modulares do manual, spec, testes e validação atualizados (ainda não commitados). |
| Runtime | Python 3.14.4 |
| Plataforma | Linux OpenCode (WSL2 kernel 6.18.33.2) |
| Toolchain LaTeX | `pdflatex`, `bibtex`, `makeindex`, `latexmk`, `pdftotext`, `pdfinfo`, `mutool` disponíveis. Classe `abntex2` local via `publishing/templates/abntex2`. |

## Estrutura modular do manual

```
docs/r456_manual_tecnico_rag/
├── main.tex                       (documento-mestre: preâmbulo + \input das seções)
├── sec_00_capa_rosto.tex          (capa, folha de rosto, resumo, sumário, listas)
├── sec_01_introducao.tex          (introdução + como ler, trilha N0–N2)
├── sec_02_problema_pesquisa.tex   (problema de pesquisa e impactos)  ← NOVA
├── sec_03_fundamentacao.tex       (fundamentação teórica)
├── sec_04_estado_atual.tex        (estado atual)
├── sec_05_proposta_recaman.tex    (proposta pós-Recamán)
├── sec_06_calculos_specs.tex      (cálculos e especificações)
├── sec_07_implementacoes.tex      (implementações reproduzíveis)
├── sec_08_mapas_dados.tex         (mapas de dados e diagrama operacional)
├── sec_09_consideracoes.tex       (considerações finais e roadmap)
├── referencias.bib
├── build.sh / Makefile            (compilam main.pdf)
└── main.pdf                       (artefato gerado, ignorado por git)
```

## Evidência observada

```text
16 passed in 0.63s          # tests/test_r456_manual_tecnico_rag.py (16 contratos)
23 passed in 0.53s          # R455 + R456 juntos
[test] paginas=31 chars=63831   # make test (pdfinfo + pdftotext)
```

O PDF gerado (`docs/r456_manual_tecnico_rag/main.pdf`) tem **31 páginas** e
**≈63.800 caracteres** de texto extraído (aprofundamento vs. 15 páginas/22.800
chars da versão inicial). A bibliografia renderiza **14 referências reais
validadas**, todas citadas no corpo em formato ABNT (autor-ano) e listadas
alfabeticamente. **Nenhum warning de citação ou referência indefinida** no log.

## Conteúdo novo validado

- **Seção 2 — Problema de Pesquisa e Impactos:** formulação formal (PP), 4
  perguntas de pesquisa (RQ1–RQ4) e hipótese central (H1), com impactos na
  ciência (metodológicos, sem overclaim) e no ecossistema (multiárea, rotulados
  como hipotéticos).
- **Insights de engenharia** extraídos do código real:
  - Roteamento adaptativo como heurística linear ponderada
    (Eq. da complexidade).
  - Determinismo deliberado (ano de referência fixo, clamp temporal, expansão de
    consulta mínima).
  - **Lacuna de métrica de diversidade** no painel `EnhancedRAG.metrics()`.
  - Conexão com o efeito "lost in the middle" e relevância funcional do
    empacotamento canônico.

## Distinção atual x proposta (anti-overclaim)

O manual contém **aviso metodológico explícito** na Seção 5: a arquitetura
pós-Recamán é **proposta**, ainda **não implementada** no código-fonte. A única
menção a "certificação" é para **negar** qualquer certificação externa ou
segurança absoluta. Não há DOIs fabricados, URLs inventadas nem alegação de
validação empírica consumada (os impactos são rotulados como hipóteses a medir).

## Comandos executados

```bash
# Compilação reproduzível do manual modular
cd docs/r456_manual_tecnico_rag
./build.sh          # documenta main.pdf (pdflatex + bibtex + makeindex)
make test           # valida pdfinfo (pages >= 15) e pdftotext (chars > 20000)

# Testes documentais
cd /home/marceloclaro/opencode-ecosystem-core
python3 -m pytest tests/test_r456_manual_tecnico_rag.py -q \
  tests/test_r455_readme_historico_operacional.py
```

## Limites conhecidos

- A arquitetura "pós-Recamán" é **proposta** (desenho), não uma implementação;
  o manual a rotula explicitamente.
- O arquivo `main.pdf` é um **artefato gerado** (ignorado pelo `.gitignore`);
  os fontes LaTeX modulares, `.bib`, scripts e Makefile são versionados.
- A compilação exige a toolchain TeX Live local; a classe `abntex2` usada é a
  copiada no repositório (`publishing/templates/abntex2`), localizada via
  `TEXINPUTS`/`BSTINPUTS`/`BIBINPUTS`.
