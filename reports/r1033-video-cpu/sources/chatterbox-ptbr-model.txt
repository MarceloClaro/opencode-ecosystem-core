---
license: mit
language:
- pt
tags:
- chatterbox
- text-to-speech
- tts
- multilingual
- single-language-tts
- voice-cloning
- chatterbox-v3
pipeline_tag: text-to-speech
base_model: ResembleAI/chatterbox
base_model_relation: finetune
---

<!-- chatterbox-space-link -->
> 🎙️ **Live demo:** Try this model in the [`ResembleAI/Chatterbox-Multilingual-TTS-pt-br`](https://huggingface.co/spaces/ResembleAI/Chatterbox-Multilingual-TTS-pt-br) Space.
<!-- chatterbox-space-link -->

# Chatterbox Multilingual: Brazilian Portuguese

Chatterbox Multilingual: Brazilian Portuguese is a dedicated single-language finetune in the **Chatterbox Multilingual V3 Single Language Pack**. It is optimized for Portuguese as spoken in Brazil, with language- and region-specific behavior for expressive text-to-speech and voice cloning.

Use this model when you want tighter Brazilian Portuguese quality control than the broad multilingual checkpoint. For a single model that covers all supported languages, use [`ResembleAI/chatterbox`](https://huggingface.co/ResembleAI/chatterbox).

## Demo

Try the hosted demo Space: [`ResembleAI/Chatterbox-Multilingual-TTS-pt-br`](https://huggingface.co/spaces/ResembleAI/Chatterbox-Multilingual-TTS-pt-br).

## Files

- `t3_pt_br.safetensors`: T3 state dict in safetensors format.
- `s3gen_v3.pt` / `s3gen_v3.safetensors`: V3 S3Gen speech decoder checkpoint.
- `grapheme_mtl_merged_expanded_v1.json`: multilingual tokenizer config.

## Language

- Locale: `pt-BR`
- Chatterbox language ID: `pt`

## Checkpoint Metadata

- Source step: `137400`
- Source checkpoint: `t3_137400.pth.tar`
- Tensor count: `292`
- Dtype: `float32`
- Text embedding shape: `(2454, 1024)`
- Speech embedding shape: `(8194, 1024)`
- Size: `2143990296` bytes
- SHA256: `074aaf65255eb9cb960288f7cc72e09d3b5008f6e0b14868c0d4e5b0bd7cbb6c`

## Loader Notes

This repository contains Chatterbox Multilingual V3 single-language assets used by the linked demo Space. The T3 checkpoint is loaded with multilingual vocabulary shape `2454` and S3 speech vocabulary shape `8194`.

The demo combines these model-specific assets with the shared Chatterbox inference code and companion assets needed for end-to-end speech generation.
