# Codex CLI e edição de imagens — o que é possível

**Status do executor:** `codex` instalado e disponível, modo
`cli-read-only-windows-interop`, última execução com sucesso.
**Limite central:** Codex é um agente de código, **não um modelo de imagem**.

## 1. O que o Codex faz

### Edição determinística (sim)

Codex pode gerar e/ou executar código para:

- recortar, redimensionar, girar, compor e aplicar bleed;
- converter cor (RGB → CMYK), ajustar contraste, saturação e sépia;
- re-renderizar SVG/PDF em 300 DPI sem upscale;
- gerar contact sheets, previews e comparações lado a lado;
- remover fundo com `rembg` (se instalado);
- converter para PDF/X ou PDF/UA via WeasyPrint/Typst/Ghostscript;
- calcular SHA-256, tamanho e manifesto de proveniência;
- rodar QA: `pdfinfo`, `pdffonts`, `pdfimages`, `gs inkcov`.

Nesta ponte, o Codex está em modo **read-only**: ele pode analisar e devolver o
script/comando, mas **não escreve o arquivo final**. O Core executa o script,
verifica o resultado e registra o hash.

### Edição generativa (não sem modelo/API)

Para inpainting, outpainting, troca de estilo, geração de cena nova ou “editar
por prompt”, é preciso um **modelo de imagem**:

- API de imagens (OpenAI Images, etc.) com chave configurada; ou
- modelo local de difusão (ComfyUI/SDXL etc.) com hardware adequado.

O modelo `gemini-nano-banana-2.1` estava indisponível nesta conexão. Codex pode
orquestrar a chamada se a API existir, mas não substitui o modelo.

## 2. Regra de impressão

- **Não fazer upscale artificial** para alegar 300 DPI.
- Preferir **re-render vetorial** (SVG/PDF) ao aumento de raster.
- Se houver upscale generativo, declarar no manifesto e não usar como arte final
  sem aprovação.
- Manter CMYK, TAC e perfil de cor documentados.
- Guardar original, script, saída e hash.

## 3. Fluxo recomendado

```
original (SVG/PNG/PDF)
   ↓
Codex: analisa + gera script (não executa)
   ↓
Core: executa em sandbox, sem shell injection
   ↓
QA: dimensões, DPI, fontes, cor, TAC, hash
   ↓
preview humano
   ↓
release manifest
```

## 4. Prompts úteis para o Codex

**Re-render 300 DPI sem upscale:**

> Analise `Molambudos_Capa_Frente_Corrigida.svg`. Gere um script Python com
> `cairosvg` que renderize a 1890 × 2717 px (300 DPI para 6,299 × 9,055 in),
> preservando proporção, e calcule SHA-256. Não execute; devolva o script e as
> pré-condições.

**Composição de capa:**

> Gere um script que monte a capa completa 13,8389 × 9,3051 in com bleed de
> 0,125 in, frente, lombada de 0,9904 in, contracapa e área de barcode de
> 2 × 1,2 in. Use WeasyPrint; não faça upscale; inclua guias em página separada.

**Auditoria de imagem:**

> Gere um script que leia `pdfimages -list`, verifique DPI mínimo, espaço de cor
> e dimensões, e produza JSON com hashes. Não altere o PDF.

## 5. Limites

- Codex não “vê” a imagem como um editor gráfico; ele lê metadados, pixels e
  código, e pode descrever o que o modelo de visão permitir.
- Codex não garante qualidade estética.
- Codex não substitui designer, prova de cor ou aprovação editorial.
- Toda edição generativa precisa de divulgação e revisão humana.
