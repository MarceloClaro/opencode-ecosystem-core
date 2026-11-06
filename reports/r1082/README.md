# R1082 — Capa selecionada, 6 pranchas de prova e perfil local

**Status:** capa selecionada finalizada; 6 pranchas de prova montadas; caderno de
provas e preflight executados. **Arte final, 2× a 300 DPI, CMYK/PDF-X e prova
física continuam pendentes.**
**Não é publicação, não é upload KDP e não é validação externa.**

## 1. Capa selecionada

A composição preta/ouro com diário, coruja, foto, caatinga e arquitetura
institucional foi finalizada em `literatura/molambudos/capas/molambudos_final/`:

| Variante | PDF | SHA-256 | Bytes |
|---|---|---|---|
| 422 pp (print) | `molambudos_capa_completa_422p_print_300dpi.pdf` | `a177899a2054486a…` | 5.428.219 |
| 436 pp (canônica) | `molambudos_capa_completa_436p_canonica_300dpi.pdf` | `1c4c368de78475d7…` | 5.428.229 |

O teste `tests/test_r1082_molambudos_cover_assets.py` passou **7/7** após a
finalização. As capas alternativas em `piranesi_pencz_2026-11-05` e
`edicao_2026-11-05` foram preservadas.

## 2. Seis pranchas de prova

As pranchas usam as artes existentes do pacote R1082 e a prancha `placa_00`.
Não houve geração nova: OpenAI está sem créditos e Gemini está com cota zero
para imagem.

| Prancha | Fonte | Tipo | DPI a 86 mm | DPI a 2× |
|---|---|---|---:|---:|
| Carceri do Colônia | `arte_confinamento.png` | IA | 316,6 | 158,3 |
| Paisagem Erodida | `arte_sertao.png` | IA | 316,6 | 158,3 |
| Arquivo Doente | `arte_arquivo.png` | IA | 316,6 | 158,3 |
| Retrato Emblemático | `placa_00.png` | prancha existente | 345,6 | 172,8 |
| Tabela Alegórica | `arte_frontal_original.png` | IA | 316,6 | 158,3 |
| Anatomia da Contaminação | `placa_00.png` (detalhe) | prancha existente | 316,6 | 158,3 |

**Lacuna 2×:** seriam necessários **2032 px** de largura para 172 mm a 300 DPI;
as fontes têm 1024–1122 px. Não houve upscale artificial. As pranchas estão a
300 DPI **no tamanho final de 86 mm**, não a 2×.

Duotone: papel `#F2E8CF`, tinta `#2B2117`, um acento carmim `#9B1B1B` por
prancha. Cada prancha tem marca de placa e hash no manifesto.

## 3. Revisão visual

Relatório: `plate_review.md`.

- **Rostos e mãos:** majoritariamente plausíveis; revisão de detalhe continua
  necessária.
- **Arquitetura europeia em 3 de 5 artes** (`confinamento`, `sertao`, `arquivo`).
  O autor pediu elementos brasileiros; a adaptação está pendente.
- `arte_frontal_original` é a mais brasileira (casa colonial, caatinga, coruja,
  diário, foto).
- `arte_contracapa_original` é um corredor colonial genérico; bom, mas precisa
  de ancoragem no Colônia.
- **Nenhuma arte tem texto legível**; nenhuma retrata pessoa real identificável.

## 4. Caderno de provas e preflight

`reports/r1082/plate_proof/caderno_provas.pdf` — 8 páginas, 160 × 230 mm,
capa + 6 pranchas + proveniência.

| Verificação | Resultado |
|---|---|
| Página | 453,543 × 651,969 pt = 160 × 230 mm |
| Páginas | 8 |
| Fontes | 7; 0 não embutidas |
| Imagens | 6; mínimo 317 DPI |
| TAC médio | 86,4% |
| TAC máximo | 117,9% |
| 2× a 300 DPI | **não** (fontes insuficientes) |
| PDF | 8.606.045 bytes; `62fdb2185e1f7b1a…` |

O caderno canônico do livro **não foi alterado**. O PDF é RGB, sem CMYK
perfilado, sem PDF/X e sem prova física.

## 5. Perfil local, sem OpenCode Go

O perfil `romance-psicologico-molambudos` foi reconfigurado:

- modelo: `ollama-local/gemma4:e2b-tuned`;
- fallbacks: `ollama-local/gemma4:e4b-tuned` e
  `litert-lm/litert-community/gemma-4-E4B-it-litert-lm`;
- nenhum fallback `opencode-go`;
- teste: `tests/test_r1082_local_provider.py` — 2 testes.

**Limite:** a configuração é válida, mas a inferência local **não foi
comprovada** nesta sessão. O endpoint Ollama listou modelos, porém o chat
retornou “model not found”/não respondeu. O perfil está pronto para quando o
runtime local estiver saudável.

## 6. Tentativas de geração de imagem

| Provider | Resultado |
|---|---|
| OpenAI `gpt-image-2` | `credit_balance_exhausted` |
| Gemini `gemini-3-pro-image` | `429`, cota 0 no free tier |
| Gemini `gemini-3.1-flash-image` | `429`, cota 0 |
| Ollama local | modelos listados; chat não respondeu |

O cliente `reports/r1081/illustration_style/gemini_image.py` está pronto para
quando houver cota. O cliente `skills/imagegen/scripts/image_gen.py` foi
corrigido para omitir `response_format` (gpt-image-2 rejeita o campo).

## 7. Limites

- Não há arte figurativa nova; as 6 pranchas são composições/provas.
- 2× a 300 DPI não é possível com as fontes atuais.
- Arquitetura europeia em 3 artes; adaptação brasileira pendente.
- RGB, sem CMYK/PDF-X, sem prova física.
- Nenhuma publicação, KDP, ISBN ou nota 10/10.
- O perfil local não teve inferência comprovada.

## 8. Arquivos

| Caminho | Conteúdo |
|---|---|
| `plate_review.md` | revisão de rostos, mãos, arquitetura e anacronismos |
| `build_plates.py` | montagem das 6 pranchas |
| `build_proof.py` | caderno e preflight |
| `plate_proof/plates/` | 6 PNGs em duotone |
| `plate_proof/plates_manifest.json` | fontes, hashes e DPI |
| `plate_proof/caderno_provas.pdf` | caderno de 8 páginas |
| `plate_proof/preflight.json` | checks e TAC |
| `../r1081/illustration_style/gemini_image.py` | cliente Gemini image |
| `skills/imagegen/scripts/image_gen.py` | correção de compatibilidade |
