#!/usr/bin/env python3
"""R1058: narração e timeline do plano de ação Airam Veras.

Gera um WAV por batida, monta a narração em 48 kHz mono e grava timeline.json
e subtitles.srt. Não clona voz; usa Edge TTS pt-BR-FranciscaNeural.
"""
from __future__ import annotations

import asyncio
import json
import math
from pathlib import Path
import subprocess
import wave

import edge_tts

ROOT = Path(__file__).resolve().parent
AUDIO = ROOT / "audio"
BEATS = AUDIO / "beats"
VOICE = "pt-BR-FranciscaNeural"
SR = 48_000
FPS = 30
PAUSE = 0.34
LEAD = 0.28
TAIL = 0.55

SKILLS = json.loads((ROOT / "skills.json").read_text(encoding="utf-8"))

BASE_SCENES = [
    {
        "id": "01", "title": "Abertura", "kicker": "PLANO DE AÇÃO • SPAECE 2026",
        "beats": [
            {"text": "Escola de Cidadania Airam Veras, Crateús, Ceará.",
             "tts": "Escola de Cidadania Airam Véras, Crateús, Ceará."},
            {"text": "Plano de ação SPAECE, novembro de 2026, 5º ano A e B.",
             "tts": "Plano de ação Espaéce, novembro de dois mil e vinte e seis, quinto ano A e B."},
            {"text": "Língua Portuguesa e Matemática: recompor para aprender.",
             "tts": "Língua Portuguesa e Matemática: recompor para aprender."},
        ],
    },
    {
        "id": "02", "title": "Território", "kicker": "MUNDO → CEARÁ → CRATEÚS → MARATOAN",
        "beats": [
            {"text": "A escola fica no bairro Maratoan, em Crateús, no sertão do Ceará.",
             "tts": "A escola fica no bairro Maratoan, em Crateús, no sertão do Ceará."},
            {"text": "Do mundo ao bairro: 55 estudantes, duas turmas, duas prioridades.",
             "tts": "Do mundo ao bairro: cinquenta e cinco estudantes, duas turmas, duas prioridades."},
        ],
    },
    {
        "id": "03", "title": "Diagnóstico", "kicker": "LINHA DE BASE • AGOSTO DE 2026",
        "beats": [
            {"text": "A linha de base é de agosto de 2026. Não é o resultado de novembro.",
             "tts": "A linha de base é de agosto de dois mil e vinte e seis. Não é o resultado de novembro."},
            {"text": "Em Língua Portuguesa: 70% adequado; 78% no 5º A e 63% no 5º B.",
             "tts": "Em Língua Portuguesa: setenta por cento adequado; setenta e oito por cento no quinto A e sessenta e três por cento no quinto B."},
            {"text": "Em Matemática: 62%; 59% no 5º A e 65% no 5º B.",
             "tts": "Em Matemática: sessenta e dois por cento; cinquenta e nove por cento no quinto A e sessenta e cinco por cento no quinto B."},
            {"text": "Fluência: 43 fluentes, 5 iniciantes e 2 pré-leitores; 5 resultados do 5º B a recuperar.",
             "tts": "Fluência: quarenta e três fluentes, cinco iniciantes e dois pré-leitores; cinco resultados do quinto B a recuperar."},
        ],
    },
    {
        "id": "04", "title": "Cronograma corrigido", "kicker": "PREPARAÇÃO ATÉ 30/11 • PROVA 01/12/2026",
        "beats": [
            {"text": "Correção importante: a avaliação SPAECE de Língua Portuguesa e Matemática será em 1º de dezembro de 2026, terça-feira.",
             "tts": "Correção importante: a avaliação Espaéce de Língua Portuguesa e Matemática será em primeiro de dezembro de dois mil e vinte e seis, terça-feira."},
            {"text": "A preparação vai até 30 de novembro. Semanas 1 e 2: diagnóstico, fundamentos, gêneros, frações e geometria.",
             "tts": "A preparação vai até trinta de novembro. Semanas um e dois: diagnóstico, fundamentos, gêneros, frações e geometria."},
            {"text": "Semanas 3 e 4: textos multimodais, medidas, gráficos, simulado, clínica de erros e contraprova.",
             "tts": "Semanas três e quatro: textos multimodais, medidas, gráficos, simulado, clínica de erros e contraprova."},
            {"text": "30/11: revisão final, logística e acolhimento. 01/12/2026: SPAECE.",
             "tts": "Trinta de novembro: revisão final, logística e acolhimento. Primeiro de dezembro de dois mil e vinte e seis: Espaéce."},
            {"text": "Rotina semanal fixa: segunda e quarta, leitura, interpretação e produção textual; terça, Matemática com operações, problemas e geometria.",
             "tts": "Rotina semanal fixa: segunda e quarta, leitura, interpretação e produção textual; terça, Matemática com operações, situações-problema e geometria."},
            {"text": "Quinta: simulados, correção e revisão das maiores dificuldades. Sexta: vídeos de apoio, Torta na Cara, Tabuada Divertida e Bingo.",
             "tts": "Quinta: simulados, correção e revisão das maiores dificuldades. Sexta: vídeos de apoio, Torta na Cara, Tabuada Divertida e Bingo."},
            {"text": "Objetivo: fortalecer leitura e escrita, ampliar Matemática e melhorar o SPAECE. Juntos pelo avanço da aprendizagem.",
             "tts": "Objetivo: fortalecer leitura e escrita, ampliar Matemática e melhorar o Espaéce. Juntos pelo avanço da aprendizagem."},
        ],
    },
    {
        "id": "05", "title": "Habilidades • Língua Portuguesa", "kicker": "5º A E 5º B • PRIORIDADES POR TURMA",
        "beats": [
            {"text": "Língua Portuguesa. No 5º A, os menores marcadores são H18 e H19, H12, H05 e H11.",
             "tts": "Língua Portuguesa. No quinto A, os menores marcadores são agá dezoito e agá dezenove, agá doze, agá cinco e agá onze."},
            {"text": "No 5º B: H05, H18, H19, H12 e H20. Vamos trabalhar inferência, assunto global, sentido, pontuação, conflito e coesão.",
             "tts": "No quinto B: agá cinco, agá dezoito, agá dezenove, agá doze e agá vinte. Vamos trabalhar inferência, assunto global, sentido, pontuação, conflito e coesão."},
        ],
    },
    {
        "id": "12", "title": "Habilidades • Matemática", "kicker": "5º A E 5º B • PRIORIDADES POR TURMA",
        "beats": [
            {"text": "Matemática. No 5º A: H18, H12, H01 e H14, H08 e H11.",
             "tts": "Matemática. No quinto A: agá dezoito, agá doze, agá um e agá quatorze, agá oito e agá onze."},
            {"text": "No 5º B: H12, H14, H11, H01 e H18. Vamos trabalhar multiplicação e divisão, frações, geometria, área, medidas e gráficos.",
             "tts": "No quinto B: agá doze, agá quatorze, agá onze, agá um e agá dezoito. Vamos trabalhar multiplicação e divisão, frações, geometria, área, medidas e gráficos."},
        ],
    },
    {
        "id": "18", "title": "Intervenções e metas", "kicker": "RESPONSÁVEIS • MONITORAMENTO • METAS",
        "beats": [
            {"text": "Professoras registram erros, apoios e respostas; coordenação revisa grupos; gestão garante tempo e materiais.",
             "tts": "Professoras registram erros, apoios e respostas; coordenação revisa grupos; gestão garante tempo e materiais."},
            {"text": "C1 e C2: atendimento focal; C3 consolida; C4 aprofunda. Metas: 80% em LP e 75% em Matemática, sem ranking.",
             "tts": "C1 e C2: atendimento focal; C3 consolida; C4 aprofunda. Metas: oitenta por cento em Língua Portuguesa e setenta e cinco por cento em Matemática, sem ranking."},
        ],
    },
]


def skill_scene(skill: dict, number: int) -> dict:
    component = "LÍNGUA PORTUGUESA" if skill["component"] == "LP" else "MATEMÁTICA"
    steps = " ".join(skill["steps"])
    question_tts = skill.get("question_tts", skill["question_short"])
    steps_tts = skill.get("steps_tts", skill["steps_short"])
    return {
        "id": f"{number:02d}",
        "title": skill["title"],
        "kicker": f"HABILIDADE • {component} • {skill['classes']}",
        "skill_id": skill["id"],
        "beats": [
            {"text": f"{skill['title']}. Foco: {skill['classes']}. Marcadores: {skill['markers']}.",
             "tts": f"{skill['title']}. Foco: {skill['classes']}. Marcadores: {skill['markers']}."},
            {"text": f"Exemplo: {skill['question_short']}",
             "tts": f"Exemplo: {question_tts}"},
            {"text": f"Como responder: {skill['steps_short']}. Por que: {skill['why_short']}",
             "tts": f"Como responder: {steps_tts} Por que: {skill['why_short']}"},
        ],
    }


SKILLS_LP = [s for s in SKILLS if s["component"] == "LP"]
SKILLS_MAT = [s for s in SKILLS if s["component"] == "MAT"]
SCENES = BASE_SCENES[:5]
SCENES += [skill_scene(s, 6 + i) for i, s in enumerate(SKILLS_LP)]
SCENES += [BASE_SCENES[5]]
SCENES += [skill_scene(s, 13 + i) for i, s in enumerate(SKILLS_MAT)]
SCENES += BASE_SCENES[6:]
SCENES += [{
    "id": "19", "title": "Agradecimento", "kicker": "PROFESSOR MARCELO CLARO",
    "beats": [
        {"text": "Muito obrigado por assistir. Sou Marcelo Claro Laranjeira, professor e pedagogo.",
         "tts": "Muito obrigado por assistir. Sou Marcelo Claro Laranjeira, professor e pedagogo."},
    ],
}]


async def synthesize(text: str, path: Path):
    if path.exists() and path.stat().st_size > 1000:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    await edge_tts.Communicate(text, VOICE, rate="+10%", volume="+0%").save(str(path))


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as w:
        return w.getnframes() / w.getframerate()


def build():
    AUDIO.mkdir(parents=True, exist_ok=True)
    BEATS.mkdir(parents=True, exist_ok=True)
    for scene in SCENES:
        sid = scene["id"]
        for index, beat in enumerate(scene["beats"]):
            mp3 = BEATS / f"{sid}-{index:02d}.mp3"
            wav = BEATS / f"{sid}-{index:02d}.wav"
            asyncio.run(synthesize(beat.get("tts", beat["text"]), mp3))
            if not wav.exists() or wav.stat().st_mtime < mp3.stat().st_mtime:
                subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(mp3),
                                "-ar", str(SR), "-ac", "1", "-c:a", "pcm_s16le", str(wav)], check=True)
    # Monta o WAV e a timeline com as mesmas durações.
    output = wave.open(str(AUDIO / "narration.wav"), "wb")
    output.setnchannels(1); output.setsampwidth(2); output.setframerate(SR)
    silence_lead = b"\x00\x00" * int(SR * LEAD)
    output.writeframes(silence_lead)
    cursor = LEAD
    scenes_out = []
    for scene in SCENES:
        start = cursor
        captions = []
        for index, beat in enumerate(scene["beats"]):
            wav = BEATS / f"{scene['id']}-{index:02d}.wav"
            with wave.open(str(wav), "rb") as w:
                frames = w.readframes(w.getnframes())
            duration = len(frames) / 2 / SR
            captions.append({"text": beat["text"], "start": round(cursor, 3),
                             "end": round(cursor + duration, 3)})
            output.writeframes(frames)
            cursor += duration
            if index < len(scene["beats"]) - 1:
                gap = b"\x00\x00" * int(SR * PAUSE)
                output.writeframes(gap); cursor += PAUSE
        scenes_out.append({"id": scene["id"], "title": scene["title"],
                           "kicker": scene["kicker"], "start": round(start, 3),
                           "end": round(cursor + TAIL, 3), "captions": captions})
        silence = b"\x00\x00" * int(SR * TAIL)
        output.writeframes(silence); cursor += TAIL
    output.close()
    total = cursor
    frames = math.ceil(total * FPS)
    timeline = {"voice": VOICE, "cloned": False, "fps": FPS, "total_duration": round(total, 3),
                "total_frames": frames, "scenes": scenes_out}
    (AUDIO / "timeline.json").write_text(json.dumps(timeline, ensure_ascii=False, indent=2) + "\n")
    # SRT por batida.
    def stamp(seconds):
        h = int(seconds // 3600); m = int(seconds % 3600 // 60); s = seconds % 60
        return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")
    rows = []
    index = 1
    for scene in scenes_out:
        for caption in scene["captions"]:
            rows += [str(index), f"{stamp(caption['start'])} --> {stamp(caption['end'])}", caption["text"], ""]
            index += 1
    (AUDIO / "subtitles.srt").write_text("\n".join(rows))
    print(json.dumps({"total_duration": round(total, 3), "frames": frames,
                      "scenes": len(scenes_out), "captions": index - 1}, ensure_ascii=False))


if __name__ == "__main__":
    build()
