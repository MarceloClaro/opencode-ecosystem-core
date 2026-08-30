# Recibo local de validação — SPEC-935-R456

## Escopo

Este recibo registra a produção do **manual técnico** da arquitetura RAG do
ecossistema, em formato de banca de doutorado, compilado em PDF. O manual
documenta (i) o **estado atual** da arquitetura RAG (implementada e observável
no checkout) e (ii) a **arquitetura-alvo proposta** pós-Recamán (não
implementada), com mapas, diagramas com legendas, cálculos, especificações
técnicas e referências reais validadas.

## Ambiente registrado

| Campo | Valor observado |
|---|---|
| Base Git (`git rev-parse HEAD`) | `27c018c` |
| Estado do checkout | diretório `docs/r456_manual_tecnico_rag/` com fontes, script e PDF; `specs/`, `tests/` e `VALIDATION_R456.md` novos (ainda não commitados). |
| Runtime | Python 3.14.4 |
| Plataforma | Linux OpenCode (WSL2 kernel 6.18.33.2) |
| Toolchain LaTeX | `pdflatex`, `bibtex`, `makeindex`, `latexmk`, `pdftotext`, `pdfinfo`, `mutool` disponíveis. Classe `abntex2` local usada via `publishing/templates/abntex2`. |

## Evidência observada

```text
12 passed in 0.40s          # tests/test_r456_manual_tecnico_rag.py
[test] paginas=15 chars=22820   # make test (pdfinfo + pdftotext)
```

O PDF gerado (`docs/r456_manual_tecnico_rag/manual_rag_recaman.pdf`) tem
**15 páginas** e **≈22.800 caracteres** de texto extraído. A bibliografia renderiza
**14 referências reais** verificadas (DOIs de TACL/ACL/NAACL/EACL/SIGIR e preprints
arXiv), todas citadas no corpo em formato ABNT (autor-ano) e listadas
alfabeticamente.

## Evidência observada (detalhe)

```text
# pdfinfo
Pages: 15
Page size: 595.276 x 841.89 pts (A4)

# pyflatex + bibtex + makeindex (via ./build.sh)
[build] OK -> .../docs/r456_manual_tecnico_rag/manual_rag_recaman.pdf

# ausência de referências indefinidas no log LaTeX
(0 mensagens "There were undefined references")

# lista de ilustrações e tabelas (formato banca)
Lista de ilustrações — Figura 1 (diagrama atual), Figura 2 (proposta pós-Recamán)
Lista de tabelas     — Tabela 1 (offsets de Recamán), Tabela 2 (especificações técnicas)
```

## Distinção atual x proposta (anti-overclaim)

O manual contém um **aviso metodológico explícito** na seção 4:

> "a arquitetura descrita nesta seção é uma **proposta**, ainda **não
> implementada** no código-fonte."

A única menção a "certificação" no documento é justamente para **negar** que
qualquer certificação externa ou segurança absoluta seja alegada. Não há cadeias
de validação externa, DOIs fabricados nem URLs inventadas.

## Comandos executados

```bash
# Compilação reproduzível do manual (script e Makefile)
cd docs/r456_manual_tecnico_rag
./build.sh
make test   # valida pdfinfo (pages >= 5) e pdftotext (chars > 5000)

# Testes documentais da rodada
cd /home/marceloclaro/opencode-ecosystem-core
python3 -m pytest tests/test_r456_manual_tecnico_rag.py -q \
  tests/test_r455_readme_historico_operacional.py
```

## Limites conhecidos

- A arquitetura "pós-Recamán" é **proposta** (desenho), não uma implementação;
  o manual a rotula explicitamente e não a apresenta como estado atual.
- O arquivo `manual_rag_recaman.pdf` é um **artefato gerado** (ignorado pelo
  `.gitignore` global `*.pdf`); os fontes LaTeX, `.bib`, scripts e Makefile são
  versionados.
- A compilação exige a toolchain TeX Live instalada localmente; a classe
  `abntex2` usada é a copiada no repositório (`publishing/templates/abntex2`).
