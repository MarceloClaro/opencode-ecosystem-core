---
spec_id: SPEC-935-R351
title: Pipeline de busca/geração de imagens com filtro sépia para o Molambudos
component: scripts/literary_sepia_pipeline.py + agents/catalog/literary-image-sepia.md
status: verified
test_file: tests/test_r351_molambudos_sepia_pipeline.py
---

# SPEC-935-R351 — Pipeline de imagens sépia para o Molambudos

## Objetivo

Criar um pipeline que, a partir de menções a fotografias no texto do romance
**Molambudos — O Diário do Paciente 1.260**, busque ou gere imagens
correspondentes e aplique filtro sépia + vinheta para envelhecimento,
produzindo arquivos prontos para inclusão no LaTeX do projeto.

## Justificativa literária

O Molambudos contém **21 menções a fotografias** que são centrais à narrativa:
a foto do Paciente 1.260 (1917, "amarelada"), do Dr. Heitor Oliveira (1979),
do homem com livro (s/d), e da Dra. Lúcia (2026). O texto descreve as fotos
como **"antigas"** e **"amareladas"** — efeito que o filtro sépia reproduz
diretamente. Ilustrar essas passagens com imagens sépia traduz visualmente
o que o narrador descreve, aumentando a imersão do leitor.

## Arquitetura

```
Texto do Molambudos
    │
    ▼
Detector de menções a fotografia (regex + LLM opcional)
    │
    ▼
Busca de imagem (Antigravity web search → URL)
  OU
Geração de imagem (Antigravity generate)
    │
    ▼
Download da imagem → PIL.Image
    │
    ▼
Pipeline de processamento:
  1. Matriz sépia 3×3 (R=0.393R+0.769G+0.189B, …)
  2. Vinheta radial (bordas escuras)
  3. Grão/textura de papel envelhecido
  4. Ajuste de contraste e brightness
    │
    ▼
Salvar em projetos/molambudos/figures/foto_N_sepia.png
    │
    ▼
Inserir \includegraphics no LaTeX do capítulo correspondente
```

## Componentes

### 1. Agente `literary-image-sepia` (agents/catalog/literary-image-sepia.md)

Agente especializado no pipeline de imagem sépia. Responsabilidades:
- Receber descrição textual de uma fotografia citada no romance
- Buscar imagem correspondente (web search ou geração)
- Aplicar pipeline de processamento (sépia + vinheta + grão)
- Salvar no diretório apropriado do projeto Molambudos
- Retornar metadata da imagem processada

### 2. Script `scripts/literary_sepia_pipeline.py`

Implementação do pipeline programático com funções:
- `detect_photo_references(text: str) → List[Dict]` — encontra menções
- `fetch_image(url: str) → Image` — download
- `generate_image(description: str) → Image` — via Antigravity
- `apply_sepia(img: Image, intensity: float) → Image` — filtro principal
- `apply_vignette(img: Image, strength: float) → Image` — vinheta
- `apply_grain(img: Image, amount: float) → Image` — textura
- `save_for_latex(img: Image, output_path: str, caption: str) → str` — salva + gera \includegraphics

### 3. Testes (tests/test_r351_molambudos_sepia_pipeline.py)

Testes unitários e de integração conforme especificação abaixo.

## Critérios de aceitação

1. **Pipeline de sépia**: dada uma imagem de entrada, o pipeline deve produzir
   uma imagem de saída com tom sépia visível (matriz 3×3 ou equivalente),
   vinheta nas bordas e grão sutil.

2. **Busca de imagem**: o pipeline deve ser capaz de buscar uma imagem
   na web (via Antigravity search) a partir de uma descrição textual
   e baixá-la para processamento.

3. **Geração de imagem**: o pipeline deve ser capaz de gerar uma imagem
   via Antigravity a partir de uma descrição textual.

4. **Detecção de menções**: o detector deve encontrar ao menos 15 das
   21 menções a fotografias no texto completo do Molambudos.

5. **LaTeX output**: o pipeline deve gerar código LaTeX `\includegraphics`
   válido com path correto e caption opcional.

6. **Integridade**: as imagens processadas devem ser salvos no diretório
   `projetos/molambudos/figures/` com nome padronizado `foto_N_sepia.png`.

7. **CLI**: o script deve expor uma interface de linha de comando:
   ```bash
   python3 scripts/literary_sepia_pipeline.py --text "..." --output foto_teste.png
   python3 scripts/literary_sepia_pipeline.py --detect --corpus projetos/molambudos/original/html_livro.html
   python3 scripts/literary_sepia_pipeline.py --generate "descrição" --output foto_gerada.png
   ```

8. **Sem quebras**: o pipeline não deve corromper imagens existentes,
   nem quebrar a compilação LaTeX do projeto.

## Não escopo

- Não substituir o julgamento do autor na seleção de imagens.
- Não fazer busca em acervos protegidos por copyright sem verificação de licença.
- Não aplicar o pipeline automaticamente sem revisão humana (modo assistido).
- Não afirmar que as imagens geradas são "históricas" ou "documentais reais".
- Não modificar o texto do Molambudos — apenas gerar assets complementares.

## Riscos

- Imagens geradas por IA podem conter artefatos (mãos deformadas, textos ilegíveis).
- Busca web pode retornar imagens protegidas por copyright.
- O filtro sépia pode reduzir contraste e legibilidade em impressão KDP.
- O pipeline adiciona ~5–15 MB ao projeto por foto processada.

## Versionamento

- v1.0 — Pipeline básico: detecção, busca/generação, sépia, vinheta, LaTeX output
- v1.1 — (futuro) Detecção automática de contexto narrativo
- v1.2 — (futuro) Modo batch para múltiplas fotos
- v1.3 — (futuro) Estilos alternativos (P&B, envelhecimento extremo, colorizado)
