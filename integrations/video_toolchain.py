"""R1043: registro curado de ferramentas/modelos para o editor universal.

Não instala, não baixa e não executa modelos. Apenas descreve papel, licença,
hardware, maturidade de integração e sinais de disponibilidade local.
"""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
from pathlib import Path
import shutil

VERSION = 'R1043-1'
LICENSE_CLASSES = {'permissive', 'copyleft', 'non_commercial', 'custom', 'unknown'}
STATUSES = {'integrated', 'candidate', 'reference_only', 'blocked'}

# Fontes verificadas em 2026-11-02 via GitHub API/Hugging Face API e leitura
# local dos livros/skills. Licença é triagem, não parecer jurídico.
REGISTRY = [
    # Base de execução
    {'id': 'ffmpeg', 'kind': 'tool', 'name': 'FFmpeg', 'url': 'https://ffmpeg.org/',
     'license': 'LGPL-2.1-or-later (partes GPL opcionais)', 'license_class': 'copyleft',
     'roles': ['cut', 'concat', 'mux', 'audio', 'subtitles', 'render'],
     'runtime': 'system', 'hardware': 'cpu', 'status': 'integrated',
     'adapter': 'integrations.video_editor', 'requires': ['ffmpeg'],
     'notes': 'Backend padrão; a configuração local determina codecs disponíveis.'},
    {'id': 'remotion', 'kind': 'tool', 'name': 'Remotion', 'url': 'https://github.com/remotion-dev/remotion',
     'license': 'Remotion License (custom, não OSI)', 'license_class': 'custom',
     'roles': ['animation', 'motion_graphics', 'overlay', 'render'],
     'runtime': 'node', 'hardware': 'cpu', 'status': 'integrated',
     'adapter': 'integrations.video_editor', 'requires': ['node', 'npx', 'license_acceptance', 'render_approval'],
     'notes': 'CLI 4.0.540 instalado; compositions verificado; render exige aprovação. Não é OSI.'},
    {'id': 'ffmpeg-skill', 'kind': 'repo', 'name': 'ffmpeg-skill', 'url': 'https://github.com/kajisho5/ffmpeg-skill',
     'license': 'MIT', 'license_class': 'permissive', 'roles': ['cut', 'audio', 'subtitles', 'mcp'],
     'runtime': 'node', 'hardware': 'cpu', 'status': 'reference_only', 'adapter': None,
     'requires': ['node'], 'notes': '42 ferramentas FFmpeg e contrato MCP; referência para ampliar operações.'},
    {'id': 'opentimelineio', 'kind': 'repo', 'name': 'OpenTimelineIO', 'url': 'https://github.com/AcademySoftwareFoundation/OpenTimelineIO',
     'license': 'Apache-2.0', 'license_class': 'permissive', 'roles': ['timeline_exchange', 'interchange'],
     'runtime': 'python', 'hardware': 'cpu', 'status': 'candidate', 'adapter': None,
     'requires': [], 'notes': 'Formato/API de timeline para interoperar com editores; adapter ainda não implementado.'},
    {'id': 'moviepy', 'kind': 'repo', 'name': 'MoviePy', 'url': 'https://github.com/Zulko/moviepy',
     'license': 'MIT', 'license_class': 'permissive', 'roles': ['compositing', 'python_backend'],
     'runtime': 'python', 'hardware': 'cpu', 'status': 'candidate', 'adapter': None,
     'requires': [], 'notes': 'Composição Python; alternativa ao FFmpeg puro, não necessária para o núcleo.'},
    {'id': 'editly', 'kind': 'repo', 'name': 'Editly', 'url': 'https://github.com/mifi/editly',
     'license': 'MIT', 'license_class': 'permissive', 'roles': ['declarative_edit', 'slideshow', 'render'],
     'runtime': 'node', 'hardware': 'cpu', 'status': 'candidate', 'adapter': None,
     'requires': ['node', 'ffmpeg'], 'notes': 'Edição declarativa em JSON; boa referência para planos reproduzíveis.'},
    {'id': 'motion-canvas', 'kind': 'repo', 'name': 'Motion Canvas', 'url': 'https://github.com/motion-canvas/motion-canvas',
     'license': 'MIT', 'license_class': 'permissive', 'roles': ['animation', 'motion_graphics'],
     'runtime': 'node', 'hardware': 'cpu', 'status': 'candidate', 'adapter': None,
     'requires': ['node'], 'notes': 'Animação por código; alternativa MIT ao Remotion para cenas 2D.'},
    {'id': 'fframes', 'kind': 'repo', 'name': 'fframes', 'url': 'https://github.com/dmtrKovalenko/fframes',
     'license': 'MIT', 'license_class': 'permissive', 'roles': ['programmatic_render', 'animation'],
     'runtime': 'rust', 'hardware': 'cpu', 'status': 'reference_only', 'adapter': None,
     'requires': ['rust'], 'notes': 'Render programático rápido; sem adapter e sem instalação.'},
    {'id': 'opencut', 'kind': 'repo', 'name': 'OpenCut', 'url': 'https://github.com/OpenCut-app/OpenCut',
     'license': 'MIT', 'license_class': 'permissive', 'roles': ['editor_ui', 'timeline', 'reference'],
     'runtime': 'web', 'hardware': 'cpu', 'status': 'reference_only', 'adapter': None,
     'requires': ['node'], 'notes': 'Editor completo tipo CapCut; referência de UX/timeline, não embutido.'},
    {'id': 'openchatcut', 'kind': 'repo', 'name': 'OpenChatCut', 'url': 'https://github.com/0xsline/OpenChatCut',
     'license': 'AGPL-3.0', 'license_class': 'copyleft', 'roles': ['conversational_edit', 'timeline'],
     'runtime': 'web', 'hardware': 'cpu', 'status': 'reference_only', 'adapter': None,
     'requires': ['node', 'license_review'], 'notes': 'AGPL; integração exigiria revisão de arquitetura/licença.'},
    {'id': 'fire-red-openstoryline', 'kind': 'repo', 'name': 'FireRed-OpenStoryline', 'url': 'https://github.com/FireRedTeam/FireRed-OpenStoryline',
     'license': 'Apache-2.0', 'license_class': 'permissive', 'roles': ['intention_edit', 'agent'],
     'runtime': 'python', 'hardware': 'gpu_optional', 'status': 'reference_only', 'adapter': None,
     'requires': [], 'notes': 'Agente de edição por intenção; referência de fluxo, não executado.'},
    {'id': 'baocut', 'kind': 'repo', 'name': 'BaoCut', 'url': 'https://github.com/JimLiu/baocut',
     'license': 'NOASSERTION (verificar)', 'license_class': 'unknown', 'roles': ['agent', 'timeline', 'dubbing'],
     'runtime': 'web', 'hardware': 'cpu', 'status': 'blocked', 'adapter': None,
     'requires': ['license_review'], 'notes': 'Licença não declarada; não integrar nem copiar.'},
    {'id': 'video-shotcraft', 'kind': 'repo', 'name': 'video-shotcraft', 'url': 'https://github.com/Vincentwei1021/video-shotcraft',
     'license': 'Apache-2.0', 'license_class': 'permissive', 'roles': ['remotion_recipes', 'promo', 'animation'],
     'runtime': 'node', 'hardware': 'cpu', 'status': 'reference_only', 'adapter': None,
     'requires': ['node'], 'notes': '124 receitas de planos Remotion; referência editorial, não copiar assets.'},
    {'id': 'videolingo', 'kind': 'repo', 'name': 'VideoLingo', 'url': 'https://github.com/Huanshere/VideoLingo',
     'license': 'Apache-2.0', 'license_class': 'permissive', 'roles': ['dubbing', 'subtitles', 'translation'],
     'runtime': 'python', 'hardware': 'gpu_optional', 'status': 'reference_only', 'adapter': None,
     'requires': ['python'], 'notes': 'Pipeline de localização; referência para alinhamento e legenda.'},
    {'id': 'latentsync', 'kind': 'repo', 'name': 'LatentSync', 'url': 'https://github.com/bytedance/LatentSync',
     'license': 'Apache-2.0 (repo); OpenRAIL++ (pesos)', 'license_class': 'custom',
     'roles': ['lip_sync'], 'runtime': 'python', 'hardware': 'gpu',
     'status': 'candidate', 'adapter': None, 'requires': ['gpu', 'hf_token', 'license_review'],
     'notes': 'Lip sync por difusão; pesos com termos próprios. Não executado.'},
    {'id': 'wav2lip', 'kind': 'repo', 'name': 'Wav2Lip', 'url': 'https://github.com/Rudrabha/Wav2Lip',
     'license': 'não declarada no GitHub (verificar)', 'license_class': 'unknown',
     'roles': ['lip_sync'], 'runtime': 'python', 'hardware': 'gpu',
     'status': 'blocked', 'adapter': None, 'requires': ['license_review'],
     'notes': 'Licença ausente/ambígua; não integrar sem autorização.'},
    {'id': 'hypit', 'kind': 'repo', 'name': 'Hypit', 'url': 'https://github.com/hypit-ai/hypit',
     'license': 'Hypit Open Source License (Apache-2.0 modificada)', 'license_class': 'custom',
     'roles': ['workflow_clone', 'composition', 'render'], 'runtime': 'node', 'hardware': 'cpu',
     'status': 'reference_only', 'adapter': None,
     'requires': ['license_review', 'explicit_install'],
     'notes': 'Licença custom; não instalar sem autorização; documentação local já registra limites.'},
    {'id': 'joyai-video-edit', 'kind': 'repo', 'name': 'JoyAI-Video-Edit', 'url': 'https://github.com/jd-opensource/JoyAI-Video-Edit',
     'license': 'Apache-2.0', 'license_class': 'permissive', 'roles': ['video_edit', 'generative'],
     'runtime': 'python', 'hardware': 'gpu', 'status': 'reference_only', 'adapter': None,
     'requires': ['gpu'], 'notes': 'Pesquisa de edição generativa; não integrado.'},
    {'id': 'scenedetect', 'kind': 'repo', 'name': 'PySceneDetect', 'url': 'https://github.com/Breakthrough/PySceneDetect',
     'license': 'BSD-3-Clause', 'license_class': 'permissive', 'roles': ['scene_detection', 'shot_split'],
     'runtime': 'python', 'hardware': 'cpu', 'status': 'candidate', 'adapter': None,
     'requires': ['python'], 'notes': 'Detecção de cortes; candidato a operação de timeline.'},
    {'id': 'auto-editor', 'kind': 'repo', 'name': 'auto-editor', 'url': 'https://github.com/WyattBlue/auto-editor',
     'license': 'Unlicense', 'license_class': 'permissive', 'roles': ['silence_cut', 'rough_cut'],
     'runtime': 'python', 'hardware': 'cpu', 'status': 'candidate', 'adapter': None,
     'requires': ['ffmpeg'], 'notes': 'Corte por silêncio/movimento; usar como proposta, não como aprovação.'},

    # Modelos de fala/ASR/diarização
    {'id': 'xtts-v2', 'kind': 'model', 'name': 'XTTS v2', 'url': 'https://huggingface.co/coqui/XTTS-v2',
     'license': 'CPML (não comercial)', 'license_class': 'non_commercial',
     'roles': ['tts', 'voice_clone'], 'runtime': 'python', 'hardware': 'cpu',
     'status': 'integrated', 'adapter': 'integrations.dubbing_synth',
     'requires': ['consent', 'reference_audio', 'license_review'],
     'notes': 'Usado no piloto; CPML restringe uso comercial. Não é modelo de emoção certificada.'},
    {'id': 'kokoro-82m', 'kind': 'model', 'name': 'Kokoro-82M', 'url': 'https://huggingface.co/hexgrad/Kokoro-82M',
     'license': 'Apache-2.0', 'license_class': 'permissive', 'roles': ['tts', 'narration'],
     'runtime': 'python', 'hardware': 'cpu', 'status': 'candidate', 'adapter': None,
     'requires': [], 'notes': 'TTS leve e rápido; não clona voz original.'},
    {'id': 'chatterbox', 'kind': 'model', 'name': 'Chatterbox', 'url': 'https://huggingface.co/ResembleAI/chatterbox',
     'license': 'MIT', 'license_class': 'permissive', 'roles': ['tts', 'voice_clone', 'emotion'],
     'runtime': 'python', 'hardware': 'gpu_optional', 'status': 'candidate', 'adapter': None,
     'requires': ['reference_audio'], 'notes': 'Clonagem zero-shot e emoção; verificar idiomas e qualidade em pt-BR.'},
    {'id': 'f5-tts', 'kind': 'model', 'name': 'F5-TTS', 'url': 'https://huggingface.co/SWivid/F5-TTS',
     'license': 'CC-BY-NC-4.0', 'license_class': 'non_commercial', 'roles': ['tts', 'voice_clone'],
     'runtime': 'python', 'hardware': 'gpu_optional', 'status': 'candidate', 'adapter': None,
     'requires': ['reference_audio', 'license_review'], 'notes': 'Clonagem não comercial; não usar em entrega monetizada.'},
    {'id': 'faster-whisper', 'kind': 'model', 'name': 'faster-whisper large-v3', 'url': 'https://huggingface.co/Systran/faster-whisper-large-v3',
     'license': 'MIT', 'license_class': 'permissive', 'roles': ['asr', 'transcription'],
     'runtime': 'python', 'hardware': 'cpu', 'status': 'integrated', 'adapter': 'integrations.video_cpu_pipeline',
     'requires': [], 'notes': 'ASR local já usado; não é aprovação de inteligibilidade.'},
    {'id': 'whisper-turbo', 'kind': 'model', 'name': 'Whisper large-v3-turbo', 'url': 'https://huggingface.co/openai/whisper-large-v3-turbo',
     'license': 'MIT', 'license_class': 'permissive', 'roles': ['asr', 'transcription'],
     'runtime': 'python', 'hardware': 'gpu_optional', 'status': 'candidate', 'adapter': None,
     'requires': [], 'notes': 'Alternativa mais rápida; comparar qualidade no corpus local.'},
    {'id': 'parakeet-v2', 'kind': 'model', 'name': 'Parakeet TDT 0.6B v2', 'url': 'https://huggingface.co/nvidia/parakeet-tdt-0.6b-v2',
     'license': 'CC-BY-4.0', 'license_class': 'permissive', 'roles': ['asr'],
     'runtime': 'python', 'hardware': 'gpu_optional', 'status': 'candidate', 'adapter': None,
     'requires': [], 'notes': 'Forte em inglês; verificar suporte a pt-BR/tr antes de adotar.'},
    {'id': 'nemotron-3-diarization', 'kind': 'model', 'name': 'Nemotron 3 Diarization', 'url': 'https://huggingface.co/nvidia/Nemotron-3-Diarization',
     'license': 'OpenMDW-1.1', 'license_class': 'custom', 'roles': ['diarization', 'speaker_mapping'],
     'runtime': 'python', 'hardware': 'cpu', 'status': 'integrated',
     'adapter': 'integrations.video_diarization_nemotron',
     'requires': ['transformers', 'torch'],
     'notes': 'Não gated; até 8 locutores; instalado no venv r1044; identidade continua hipótese.'},
    {'id': 'speechbrain-ecapa', 'kind': 'model', 'name': 'SpeechBrain ECAPA VoxCeleb', 'url': 'https://huggingface.co/speechbrain/spkrec-ecapa-voxceleb',
     'license': 'Apache-2.0', 'license_class': 'permissive', 'roles': ['speaker_embedding', 'diarization'],
     'runtime': 'python', 'hardware': 'cpu', 'status': 'integrated',
     'adapter': 'integrations.video_diarization',
     'requires': ['speechbrain', 'torch'],
     'notes': 'Fallback instalado; baixa acurácia em falas curtas/sobrepostas; não usar sozinho para nomear.'},
    {'id': 'silero-vad', 'kind': 'model', 'name': 'Silero VAD', 'url': 'https://huggingface.co/snakers4/silero-vad',
     'license': 'MIT', 'license_class': 'permissive', 'roles': ['vad', 'speech_segmentation'],
     'runtime': 'python', 'hardware': 'cpu', 'status': 'integrated',
     'adapter': 'integrations.video_diarization',
     'requires': ['silero-vad'],
     'notes': 'Segmentação de fala local; não identifica locutor.'},
    {'id': 'pyannote-3-1', 'kind': 'model', 'name': 'pyannote speaker-diarization-3.1', 'url': 'https://huggingface.co/pyannote/speaker-diarization-3.1',
     'license': 'MIT', 'license_class': 'permissive', 'roles': ['diarization', 'speaker_mapping'],
     'runtime': 'python', 'hardware': 'cpu', 'status': 'candidate', 'adapter': None,
     'requires': ['hf_token', 'gated_access'], 'notes': 'Peça que falta para mapear as 106 partes; acesso gated exige aceite do operador.'},
    {'id': 'pyannote-community-1', 'kind': 'model', 'name': 'pyannote speaker-diarization-community-1', 'url': 'https://huggingface.co/pyannote/speaker-diarization-community-1',
     'license': 'CC-BY-4.0', 'license_class': 'permissive', 'roles': ['diarization', 'speaker_mapping'],
     'runtime': 'python', 'hardware': 'cpu', 'status': 'candidate', 'adapter': None,
     'requires': ['hf_token', 'gated_access'], 'notes': 'Alternativa com licença CC-BY-4.0; também gated.'},

    # Vídeo generativo/animação
    {'id': 'wan22-t2v', 'kind': 'model', 'name': 'Wan2.2 T2V A14B', 'url': 'https://huggingface.co/Wan-AI/Wan2.2-T2V-A14B',
     'license': 'Apache-2.0', 'license_class': 'permissive', 'roles': ['text_to_video', 'animation'],
     'runtime': 'python', 'hardware': 'gpu_high', 'status': 'candidate', 'adapter': None,
     'requires': ['gpu', 'large_download'], 'notes': 'Geração de vídeo; não é edição do material original.'},
    {'id': 'wan21-vace', 'kind': 'model', 'name': 'Wan2.1 VACE 14B', 'url': 'https://huggingface.co/Wan-AI/Wan2.1-VACE-14B',
     'license': 'Apache-2.0', 'license_class': 'permissive', 'roles': ['video_edit', 'control', 'animation'],
     'runtime': 'python', 'hardware': 'gpu_high', 'status': 'candidate', 'adapter': None,
     'requires': ['gpu', 'large_download'], 'notes': 'Edição/controle por vídeo; candidato para VFX e correção generativa.'},
    {'id': 'hunyuanvideo', 'kind': 'model', 'name': 'HunyuanVideo', 'url': 'https://huggingface.co/tencent/HunyuanVideo',
     'license': 'Tencent Hunyuan Community License (custom)', 'license_class': 'custom',
     'roles': ['text_to_video'], 'runtime': 'python', 'hardware': 'gpu_high', 'status': 'reference_only',
     'adapter': None, 'requires': ['gpu', 'license_review'], 'notes': 'Licença custom; não integrar sem revisão.'},
    {'id': 'ltx-video', 'kind': 'model', 'name': 'LTX-Video', 'url': 'https://huggingface.co/Lightricks/LTX-Video',
     'license': 'LTX-Video Open Weights License (custom)', 'license_class': 'custom',
     'roles': ['text_to_video', 'image_to_video'], 'runtime': 'python', 'hardware': 'gpu',
     'status': 'reference_only', 'adapter': None, 'requires': ['gpu', 'license_review'],
     'notes': 'Rápido; termos próprios, revisar antes de uso comercial.'},
    {'id': 'mochi-1', 'kind': 'model', 'name': 'Mochi 1', 'url': 'https://huggingface.co/genmo/mochi-1-preview',
     'license': 'Apache-2.0', 'license_class': 'permissive', 'roles': ['text_to_video'],
     'runtime': 'python', 'hardware': 'gpu_high', 'status': 'candidate', 'adapter': None,
     'requires': ['gpu', 'large_download'], 'notes': 'Geração aberta; pesada para CPU.'},
    {'id': 'cogvideox', 'kind': 'model', 'name': 'CogVideoX-5b', 'url': 'https://huggingface.co/zai-org/CogVideoX-5b',
     'license': 'Apache-2.0 (verificar redirect)', 'license_class': 'permissive',
     'roles': ['text_to_video', 'image_to_video'], 'runtime': 'python', 'hardware': 'gpu_high',
     'status': 'candidate', 'adapter': None, 'requires': ['gpu', 'large_download'],
     'notes': 'Modelo redirecionado para zai-org; conferir card/licença atual.'},
    {'id': 'animatediff', 'kind': 'model', 'name': 'AnimateDiff', 'url': 'https://huggingface.co/guoyww/animatediff',
     'license': 'Apache-2.0', 'license_class': 'permissive', 'roles': ['animation', 'motion'],
     'runtime': 'python', 'hardware': 'gpu', 'status': 'candidate', 'adapter': None,
     'requires': ['gpu'], 'notes': 'Animação de imagens; útil para motion graphics, não para edição de timeline.'},
    {'id': 'seedvr2', 'kind': 'model', 'name': 'SeedVR2-7B', 'url': 'https://huggingface.co/ByteDance-Seed/SeedVR2-7B',
     'license': 'Apache-2.0', 'license_class': 'permissive', 'roles': ['upscale', 'restore'],
     'runtime': 'python', 'hardware': 'gpu', 'status': 'candidate', 'adapter': None,
     'requires': ['gpu'], 'notes': 'Restauração/upscale de vídeo; não executado.'},

    # Visão/segmentação/matting
    {'id': 'qwen25-vl', 'kind': 'model', 'name': 'Qwen2.5-VL-7B-Instruct', 'url': 'https://huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct',
     'license': 'Apache-2.0', 'license_class': 'permissive', 'roles': ['video_understanding', 'caption', 'ocr'],
     'runtime': 'python', 'hardware': 'gpu', 'status': 'candidate', 'adapter': None,
     'requires': ['gpu'], 'notes': 'Entendimento de vídeo para seleção de trechos; não é editor.'},
    {'id': 'florence-2', 'kind': 'model', 'name': 'Florence-2-large', 'url': 'https://huggingface.co/microsoft/Florence-2-large',
     'license': 'MIT', 'license_class': 'permissive', 'roles': ['ocr', 'detection', 'caption'],
     'runtime': 'python', 'hardware': 'cpu', 'status': 'candidate', 'adapter': None,
     'requires': [], 'notes': 'Visão leve para OCR/detecção; alternativa ao Tesseract em alguns casos.'},
    {'id': 'sam2', 'kind': 'model', 'name': 'SAM 2', 'url': 'https://huggingface.co/facebook/sam2-hiera-large',
     'license': 'Apache-2.0', 'license_class': 'permissive', 'roles': ['segmentation', 'matting', 'tracking'],
     'runtime': 'python', 'hardware': 'gpu', 'status': 'candidate', 'adapter': None,
     'requires': ['gpu'], 'notes': 'Segmentação/tracking para recorte e composição; não substitui revisão de borda.'},
    {'id': 'birefnet', 'kind': 'model', 'name': 'BiRefNet', 'url': 'https://huggingface.co/ZhengPeng7/BiRefNet',
     'license': 'MIT', 'license_class': 'permissive', 'roles': ['matting', 'background_removal'],
     'runtime': 'python', 'hardware': 'gpu_optional', 'status': 'candidate', 'adapter': None,
     'requires': [], 'notes': 'Matting de alta qualidade; candidato ao recorte de apresentador.'},
    {'id': 'rmbg-2', 'kind': 'model', 'name': 'RMBG-2.0', 'url': 'https://huggingface.co/briaai/RMBG-2.0',
     'license': 'BRIA RMBG License (custom, gated)', 'license_class': 'custom',
     'roles': ['background_removal'], 'runtime': 'python', 'hardware': 'gpu_optional',
     'status': 'reference_only', 'adapter': None, 'requires': ['hf_token', 'license_review'],
     'notes': 'Licença custom/gated; não integrar sem aceite.'},
    {'id': 'depth-anything-v2', 'kind': 'model', 'name': 'Depth Anything V2 Large', 'url': 'https://huggingface.co/depth-anything/Depth-Anything-V2-Large',
     'license': 'CC-BY-NC-4.0', 'license_class': 'non_commercial', 'roles': ['depth', '3d_parallax'],
     'runtime': 'python', 'hardware': 'gpu_optional', 'status': 'candidate', 'adapter': None,
     'requires': ['license_review'], 'notes': 'Profundidade não comercial; usar só em projeto sem monetização.'},
]


def validate_registry(entries=None):
    rows = REGISTRY if entries is None else entries
    if not isinstance(rows, list) or len(rows) < 10:
        raise ValueError('registry too small')
    ids = set()
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError('entry object required')
        for key in ('id', 'kind', 'name', 'url', 'license', 'license_class', 'roles',
                    'runtime', 'hardware', 'status'):
            if key not in row:
                raise ValueError(f'{row.get("id", "?")}: missing {key}')
        if row['id'] in ids:
            raise ValueError(f'duplicate id: {row["id"]}')
        ids.add(row['id'])
        if row['license_class'] not in LICENSE_CLASSES:
            raise ValueError(f'{row["id"]}: invalid license_class')
        if row['status'] not in STATUSES:
            raise ValueError(f'{row["id"]}: invalid status')
        if not isinstance(row['roles'], list) or not row['roles']:
            raise ValueError(f'{row["id"]}: roles required')
        if not isinstance(row['url'], str) or not row['url'].startswith('https://'):
            raise ValueError(f'{row["id"]}: https URL required')
        if row['status'] == 'integrated' and not row.get('adapter'):
            raise ValueError(f'{row["id"]}: integrated entry needs adapter')
    return {'schema_version': 1, 'version': VERSION, 'count': len(rows),
            'ids': sorted(ids), 'license_classes': sorted({r['license_class'] for r in rows})}


def recommend(task, *, allow_copyleft=False, allow_noncommercial=False,
              allow_custom=False):
    if not isinstance(task, str) or not task:
        raise ValueError('task required')
    result = []
    for row in REGISTRY:
        if task not in row['roles']:
            continue
        if row['status'] == 'blocked':
            continue
        if row['status'] != 'integrated':
            if row['license_class'] == 'copyleft' and not allow_copyleft:
                continue
            if row['license_class'] == 'non_commercial' and not allow_noncommercial:
                continue
            if row['license_class'] == 'custom' and not allow_custom:
                continue
        result.append(copy.deepcopy(row))
    order = {'integrated': 0, 'candidate': 1, 'reference_only': 2}
    return sorted(result, key=lambda r: (order.get(r['status'], 9), r['id']))


def can_integrate(entry, *, accepted_licenses=()):
    if entry.get('status') == 'blocked':
        return {'allow': False, 'reason': 'blocked_license_or_status'}
    if entry.get('license_class') == 'unknown':
        return {'allow': False, 'reason': 'license_unknown'}
    if entry.get('license_class') == 'copyleft' and entry['id'] not in accepted_licenses:
        return {'allow': False, 'reason': 'copyleft_requires_acceptance'}
    if entry.get('license_class') == 'non_commercial' and entry['id'] not in accepted_licenses:
        return {'allow': False, 'reason': 'noncommercial_requires_acceptance'}
    if entry.get('license_class') == 'custom' and entry['id'] not in accepted_licenses:
        return {'allow': False, 'reason': 'custom_license_requires_acceptance'}
    return {'allow': True, 'reason': 'license_screen_passed'}


def detect():
    system = {name: bool(shutil.which(name)) for name in
              ('ffmpeg', 'ffprobe', 'node', 'npx', 'tesseract', 'python3')}
    modules = {}
    for name in ('moviepy', 'opentimelineio', 'cv2', 'scenedetect', 'demucs',
                 'torch', 'transformers', 'faster_whisper', 'TTS', 'pyannote.audio'):
        try:
            modules[name] = importlib.util.find_spec(name) is not None
        except (ImportError, ValueError, ModuleNotFoundError):
            modules[name] = False
    return {'system': system, 'modules': modules,
            'note': 'detecção não prova versão, licença, modelo baixado ou execução'}


def to_json():
    return json.dumps({'schema_version': 1, 'version': VERSION,
                       'validation': validate_registry(), 'entries': REGISTRY,
                       'detected': detect()}, ensure_ascii=False, indent=2) + '\n'


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['validate', 'recommend', 'detect', 'export'])
    parser.add_argument('--task')
    parser.add_argument('--out')
    args = parser.parse_args(argv)
    if args.operation == 'validate':
        result = validate_registry()
    elif args.operation == 'detect':
        result = detect()
    elif args.operation == 'recommend':
        result = {'task': args.task, 'items': recommend(args.task)}
    else:
        text = to_json()
        if args.out:
            Path(args.out).write_text(text)
            result = {'out': args.out, 'bytes': len(text.encode())}
        else:
            result = json.loads(text)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
