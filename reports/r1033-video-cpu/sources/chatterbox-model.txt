---
license: mit
language:
- ar
- da
- de
- el
- en
- es
- fi
- fr
- he
- hi
- it
- ja
- ko
- ms
- nl
- no
- pl
- pt
- ru
- sv
- sw
- tr
- zh
pipeline_tag: text-to-speech
tags:
- text-to-speech
- speech
- speech-generation
- voice-cloning
- multilingual-tts
library_name: chatterbox
---

<img width="800" alt="cb-big2" src="https://github.com/user-attachments/assets/bd8c5f03-e91d-4ee5-b680-57355da204d1" />

<h1 style="font-size: 32px">Chatterbox TTS</h1>

<div style="display: flex; align-items: center; gap: 12px">
  <a href="https://resemble-ai.github.io/chatterbox_demopage/">
    <img src="https://img.shields.io/badge/listen-demo_samples-blue" alt="Listen to Demo Samples" />
  </a>
  <a href="https://huggingface.co/spaces/ResembleAI/Chatterbox">
    <img src="https://huggingface.co/datasets/huggingface/badges/resolve/main/open-in-hf-spaces-sm.svg" alt="Open in HF Spaces" />
  </a>
  <a href="https://podonos.com/resembleai/chatterbox">
    <img src="https://static-public.podonos.com/badges/insight-on-pdns-sm-dark.svg" alt="Insight on Podos" />
  </a>
</div>

<div style="display: flex; align-items: center; gap: 8px;">
  <span style="font-style: italic;white-space: pre-wrap">Made with  ❤️  by</span>
  <img width="100" alt="resemble-logo-horizontal" src="https://github.com/user-attachments/assets/35cf756b-3506-4943-9c72-c05ddfa4e525" />
</div>

## Latest Release: Chatterbox Multilingual V3

**Chatterbox Multilingual V3** is the latest general-purpose multilingual TTS model in the Chatterbox family. It keeps the same 0.5B model size while improving speaker similarity, reducing hallucinations, and producing more natural, conversational speech across languages.

V3 is designed for broad language coverage like V2, but with stronger stability and more expressive generation. It is the recommended multilingual model for users who want one voice cloning model that works across many languages. Try it in the [Chatterbox Multilingual TTS V3 Space](https://huggingface.co/spaces/ResembleAI/Chatterbox-Multilingual-TTS-V3).

Alongside V3, we are releasing the **Single Language Pack**: dedicated finetunes for priority languages where tighter quality control, stronger language-specific behavior, and more specialized speech generation are valuable.

- **Broad Multilingual Coverage:** Designed as the main general-purpose multilingual Chatterbox model, supporting wide language coverage similar to V2.
- **Single Language Pack:** Dedicated single-language models provide stronger specialization and quality control where language- and regional-dialect-specific performance matters most.
- **More Consistent Speaker Similarity:** Improves voice identity and accent preservation across languages, making cross-language voice cloning more stable and reliable.
- **Reduced Hallucination:** V3 is optimized to reduce unwanted continuation, repetition, and off-prompt speech, especially in cases where earlier multilingual models were less stable.

## Model Zoo

Choose the right Chatterbox model for your application.

| Model | Size | Languages | Key Features | Best For | Demo |
| --- | --- | --- | --- | --- | --- |
| **Chatterbox Multilingual V3** | **500M** | **23+** | Improved speaker similarity, reduced hallucinations, more natural multilingual speech | Global applications, localization, cross-language voice cloning | [Demo](https://huggingface.co/spaces/ResembleAI/Chatterbox-Multilingual-TTS-V3) |
| **Single Language Pack** | 500M each | 6 dedicated finetunes | Language- and region-specific quality control | Priority languages and dialect-sensitive applications | [Demos](#single-language-pack) |
| Chatterbox | 500M | English | CFG and exaggeration tuning | General zero-shot TTS with creative controls | [Demo](https://huggingface.co/spaces/ResembleAI/Chatterbox) |

**09/04 🔥 Introducing Chatterbox Multilingual in 23 Languages!**

We're excited to introduce **Chatterbox** and **Chatterbox Multilingual**, [Resemble AI's](https://resemble.ai) production-grade open source TTS models. Chatterbox Multilingual supports **Arabic, Danish, German, Greek, English, Spanish, Finnish, French, Hebrew, Hindi, Italian, Japanese, Korean, Malay, Dutch, Norwegian, Polish, Portuguese, Russian, Swedish, Swahili, Turkish, Chinese** out of the box. Licensed under MIT, Chatterbox has been benchmarked against leading closed-source systems like ElevenLabs, and is consistently preferred in side-by-side evaluations.

Whether you're working on memes, videos, games, or AI agents, Chatterbox brings your content to life. It's also the first open source TTS model to support **emotion exaggeration control**, a powerful feature that makes your voices stand out. Try it now on our [Hugging Face Gradio app.](https://huggingface.co/spaces/ResembleAI/Chatterbox)

If you like the model but need to scale or tune it for higher accuracy, check out our competitively priced TTS service (<a href="https://resemble.ai">link</a>). It delivers reliable performance with ultra-low latency of sub 200ms—ideal for production use in agents, applications, or interactive media.

# Key Details
- Chatterbox Multilingual V3, a 0.5B general-purpose multilingual TTS model supporting 23 languages
- Dedicated single-language finetunes for Chinese, LatAm Spanish, Brazilian Portuguese, Spain Spanish, Portugal Portuguese, and Hindi
- SoTA zeroshot English TTS
- 0.5B Llama backbone
- Unique exaggeration/intensity control
- Ultra-stable with alignment-informed inference
- Trained on 0.5M hours of cleaned data
- Watermarked outputs
- Easy voice conversion script
- [Outperforms ElevenLabs](https://podonos.com/resembleai/chatterbox)

# Tips
- **General Use (TTS and Voice Agents):**
  - The default settings (`exaggeration=0.5`, `cfg=0.5`) work well for most prompts.
  - If the reference speaker has a fast speaking style, lowering `cfg` to around `0.3` can improve pacing.

- **Expressive or Dramatic Speech:**
  - Try lower `cfg` values (e.g. `~0.3`) and increase `exaggeration` to around `0.7` or higher.
  - Higher `exaggeration` tends to speed up speech; reducing `cfg` helps compensate with slower, more deliberate pacing.

  
***Note:*** Ensure that the reference clip matches the specified language tag. Otherwise, language transfer outputs may inherit the accent of the reference clip’s language.  
***To mitigate this, set the CFG weight to 0.***


# Installation
```
pip install chatterbox-tts
```


# Usage
```python
import torchaudio as ta
from chatterbox.tts import ChatterboxTTS

model = ChatterboxTTS.from_pretrained(device="cuda")

text = "Ezreal and Jinx teamed up with Ahri, Yasuo, and Teemo to take down the enemy's Nexus in an epic late-game pentakill."
wav = model.generate(text)
ta.save("test-1.wav", wav, model.sr)

# If you want to synthesize with a different voice, specify the audio prompt
AUDIO_PROMPT_PATH="YOUR_FILE.wav"
wav = model.generate(text, audio_prompt_path=AUDIO_PROMPT_PATH)
ta.save("test-2.wav", wav, model.sr)
```

# Multilingual Quickstart
```python
import torchaudio as ta
from chatterbox.mtl_tts import ChatterboxMultilingualTTS

multilingual_model = ChatterboxMultilingualTTS.from_pretrained(
    device="cuda",
    t3_model="v3",
)
# To use the legacy V2 multilingual checkpoint, omit t3_model or pass t3_model="v2".

french_text = "Bonjour, comment ça va? Ceci est le modèle de synthèse vocale multilingue Chatterbox, il prend en charge 23 langues."
wav_french = multilingual_model.generate(french_text, language_id="fr")
ta.save("test-french.wav", wav_french, multilingual_model.sr)

chinese_text = "你好，今天天气真不错，希望你有一个愉快的周末。"
wav_chinese = multilingual_model.generate(chinese_text, language_id="zh")
ta.save("test-chinese.wav", wav_chinese, multilingual_model.sr)
```
See `example_tts.py` for more examples.

## Single Language Pack

The Single Language Pack provides dedicated finetunes for priority languages and regional variants. Use these when you want stronger language-specific behavior, tighter quality control, or dialect-aware generation beyond the general multilingual model.

| Language | Model Card | Demo Space |
| --- | --- | --- |
| Chinese | [ResembleAI/Chatterbox-Multilingual-zh-cmn](https://huggingface.co/ResembleAI/Chatterbox-Multilingual-zh-cmn) | [Demo](https://huggingface.co/spaces/ResembleAI/Chatterbox-Multilingual-TTS-zh-cmn) |
| LatAm Spanish | [ResembleAI/Chatterbox-Multilingual-es-mx-latam](https://huggingface.co/ResembleAI/Chatterbox-Multilingual-es-mx-latam) | [Demo](https://huggingface.co/spaces/ResembleAI/Chatterbox-Multilingual-TTS-es-mx-latam) |
| Brazilian Portuguese | [ResembleAI/Chatterbox-Multilingual-pt-br](https://huggingface.co/ResembleAI/Chatterbox-Multilingual-pt-br) | [Demo](https://huggingface.co/spaces/ResembleAI/Chatterbox-Multilingual-TTS-pt-br) |
| Spain Spanish | [ResembleAI/Chatterbox-Multilingual-es-es](https://huggingface.co/ResembleAI/Chatterbox-Multilingual-es-es) | [Demo](https://huggingface.co/spaces/ResembleAI/Chatterbox-Multilingual-TTS-es-es) |
| Portugal Portuguese | [ResembleAI/Chatterbox-Multilingual-pt-pt](https://huggingface.co/ResembleAI/Chatterbox-Multilingual-pt-pt) | [Demo](https://huggingface.co/spaces/ResembleAI/Chatterbox-Multilingual-TTS-pt-pt) |
| Hindi | [ResembleAI/Chatterbox-Multilingual-hi](https://huggingface.co/ResembleAI/Chatterbox-Multilingual-hi) | [Demo](https://huggingface.co/spaces/ResembleAI/Chatterbox-Multilingual-TTS-hi) |


# Acknowledgements
- [Cosyvoice](https://github.com/FunAudioLLM/CosyVoice)
- [HiFT-GAN](https://github.com/yl4579/HiFTNet)
- [Llama 3](https://github.com/meta-llama/llama3)

# Built-in PerTh Watermarking for Responsible AI

Every audio file generated by Chatterbox includes [Resemble AI's Perth (Perceptual Threshold) Watermarker](https://github.com/resemble-ai/perth) - imperceptible neural watermarks that survive MP3 compression, audio editing, and common manipulations while maintaining nearly 100% detection accuracy.

# Disclaimer
Don't use this model to do bad things. Prompts are sourced from freely available data on the internet.
