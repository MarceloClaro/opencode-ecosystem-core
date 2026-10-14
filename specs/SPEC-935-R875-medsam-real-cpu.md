---
spec_id: SPEC-935-R875
title: RX reprodução — MedSAM real (Opção 3) com carregamento mapeado para CPU
component: outputs/core-r853-rx
status: implemented
round_id: R875
test_file: tests/test_r875_medsam_cpu.py
---

# SPEC-935-R875 — Integrar o MedSAM real e corrigir o carregamento em CPU

## Contexto e decisão

O operador pediu (**"medsam"**) para tentar o checkpoint **real** do MedSAM e
ligá-lo ao motor `open_base` (Opção 3) da reprodução (SPEC-935-R853/R874). O alvo
usa `medsam_vit_b` (`/health`: `sam.model=medsam_vit_b`); a reprodução até então só
havia verificado o **SAM ViT-B base** (`sam_vit_b.pth`, domínio natural).

Decisão: baixar o `medsam_vit_b.pth` de espelho público, verificar tamanho/hash,
carregar sob `segment_anything` e corrigir o caminho de carregamento para host
**CPU-only**.

## Artefato obtido (proveniência honesta)

- Arquivo: `~/.cache/rx-weights/medsam_vit_b.pth`
- Tamanho: **375.049.145 bytes**
- `sha256`: `34b34b78c1d18cb8c6bf84cf9c00e135d6d6c965699f3c0e31ef1bc9dcb5be74`
- Fonte: espelho no Hugging Face (`kooshakooshadv/medsam-vit-b`). **Cinco** repositórios
  independentes (`kooshakooshadv`, `maregu2023`, `Pankaj0403`, `raju-ai/CG-MedSAM`,
  `meowmeowai/dual-explain-medsam-vit-b`) servem **o mesmo blob** (`xet` content hash
  `56122fe2…`, idêntico `content-length`), o que converge para o mesmo arquivo
  canônico. **Não** é possível atestar criptograficamente a autoria `wanglab` a partir
  do espelho — a verificação é **funcional** (arquitetura + inferência), não de origem.
- Estrutura: `torch.save` zip, `state_dict` com **314 chaves**, prefixos
  `image_encoder` / `prompt_encoder` / `mask_decoder` → compatível com
  `sam_model_registry["vit_b"]`.

## Defeito encontrado e corrigido

`segment_anything.build_sam._build_sam` faz `torch.load(f)` **sem** `map_location`.
O checkpoint do MedSAM **guarda as storages ancoradas em CUDA** (`cuda:0`); em host
CPU-only, carregar por `sam_model_registry["vit_b"](checkpoint=path)` falha com
`RuntimeError: Attempting to deserialize object on a CUDA device but
torch.cuda.is_available() is False`. (O `sam_vit_b.pth` base não expõe o defeito
porque suas storages são CPU.)

Correção em `outputs/core-r853-rx/repro/backend/app.py`:

- novo `_load_sam(ckpt, registry)`: `torch.load(path, map_location="cpu")` →
  `registry["vit_b"](checkpoint=None)` → `sam.load_state_dict(state_dict, strict=True)`
  → `sam.eval()`, com cache por caminho absoluto (`_SAM_CACHE`);
- `_medsam_segment` passa a usar `_load_sam`.

`strict=True` garante **correspondência exata** de arquitetura (nenhuma chave
faltante ou extra), o que também serve de verificação da integridade do checkpoint.

## Contratos de aceite

1. `_load_sam` lê o checkpoint com `map_location="cpu"` (regressão do defeito CUDA).
2. `_load_sam` constrói o modelo com `checkpoint=None` e injeta via
   `load_state_dict(..., strict=True)`.
3. `_load_sam` **cacheia** por caminho (segunda chamada não relê o arquivo).
4. Com o MedSAM real presente e `segment_anything` disponível, `POST /segment/sam`
   sob `RX_ENGINE=open_base` responde **200** com contorno real (≥ 3 pontos) —
   **pulado** quando o ambiente não tem o checkpoint (nunca simulado).
5. `_medsam_segment` / `_load_sam` não alteram o contrato de `/segment/sam`.

## Verificação

- `_load_sam` com o MedSAM real: `load_state_dict(strict=True)` →
  *"All keys matched successfully"*; `img_size=1024`.
- Inferência real (CPU): máscara produzida (área > 0) sobre "lesão" sintética.
- HTTP ao vivo: `POST /segment/sam` (`open_base`) → **200**, contorno com 261 pontos
  circundando a estrutura-alvo dentro da caixa informada (~25 s na 1ª chamada,
  incluindo carga do modelo; ~17 s em cache).
- Testes: `tests/test_r875_medsam_cpu.py` (regressão unitária, sem GPU) +
  `tests/test_r853_rx_repro.py::test_option3_real_sam_when_available` (ponta a ponta,
  agora exercendo MedSAM) — **37 passed** com os dois checkpoints presentes.

## Limites

O MedSAM é um **segmentador de prompt** (não substitui os modelos odontológicos
fdi/teeth/finding/age do alvo, que **não** foram obtidos). Os pesos usados
(MedSAM / SAM base) **não** são os pesos clínicos do alvo. `externally_validated=false`,
`confidence_promoted=false`. Sem GPU, o carregamento é forçado a CPU (mais lento).
A proveniência do espelho é **funcional**, não criptográfica.
