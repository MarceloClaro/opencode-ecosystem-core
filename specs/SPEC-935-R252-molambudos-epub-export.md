# SPEC-935-R252 — Exportação ePub do livro Molambudos

## Objetivo

Gerar uma versão ePub funcional de `Molambudos — O Diário do Paciente 1.260` a partir do projeto LaTeX em:

`projetos/molambudos/Molambudos_VictoriaRegia/`

## Escopo

- Resolver `\input` e `\include` do `main.tex`.
- Converter LaTeX narrativo para Markdown ePub-safe.
- Remover comandos decorativos ou tipográficos não suportados em ePub.
- Preservar texto narrativo, títulos, passaporte, rotas textuais e imagens convertíveis pelo pandoc.
- Gerar:
  - `main.epub`
  - `Molambudos_O-Diario-do-Paciente-1260_v1.5_2026-07-26.epub`

## Critérios de aceitação

1. O pré-processador gera `main.epub.md` sem comandos LaTeX desconhecidos.
2. O pandoc compila o ePub sem erro.
3. O arquivo ePub é um ZIP válido (`zip_test: OK`).
4. O ePub contém `mimetype` e `META-INF/container.xml`.
5. O conteúdo interno não contém comandos LaTeX residuais (`raw_latex_commands: 0`).
6. Trechos críticos aparecem no ePub:
   - `Passaporte de Leitura`
   - `MEM-07`
   - `A Mãe Levada`
   - `O Curral do Governo`
   - `Depois da noite na vala`
7. `main.epub` e a versão nomeada têm o mesmo conteúdo final.

## Implementação

Arquivo principal:

- `projetos/molambudos/Molambudos_VictoriaRegia/misc/preprocess_for_pandoc.py`

Pipeline executado:

```bash
python3 misc/preprocess_for_pandoc.py
pandoc main.epub.md -f markdown -t epub \
  --metadata title="Molambudos — O Diário do Paciente 1.260" \
  --metadata author="Marcelo Dias de Carvalho Filho" \
  --metadata lang="pt-BR" \
  --metadata date="2026" \
  --metadata publisher="Selo Molambudos" \
  --metadata description="Um livro-arquivo sobre trauma, memória e contaminação narrativa" \
  --metadata subject="Ficção brasileira; Literatura experimental; Memória" \
  --metadata rights="CC BY-NC-SA 4.0" \
  -o Molambudos_O-Diario-do-Paciente-1260_v1.5_2026-07-26.epub
cp Molambudos_O-Diario-do-Paciente-1260_v1.5_2026-07-26.epub main.epub
```

## Resultado verificado

- `Molambudos_O-Diario-do-Paciente-1260_v1.5_2026-07-26.epub`
- `main.epub`
- Tamanho: `8.984.954` bytes
- Entradas internas: `20`
- XHTML/HTML: `8`
- Imagens: `6`
- `zip_test: OK`
- `raw_latex_commands: 0`

## Limitações conhecidas

- A conversão prioriza fluxo reflowable de leitura, não fidelidade visual pixel-perfect ao PDF.
- Elementos TikZ/ornamentos decorativos são simplificados ou removidos.
- Rotas permanecem como texto, não como navegação hiperlinkada completa.
