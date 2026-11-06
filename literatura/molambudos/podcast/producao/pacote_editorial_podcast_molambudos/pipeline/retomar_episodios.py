#!/usr/bin/env python3
"""Retomada EP16..26 do podcast Molambudos — SPEC-973 (com backoff anti-rate-limit).
Lição física do primeiro lote (R553): o servidor NotebookLM recusa RPC com
RESOURCE_EXHAUSTED quando muitas operações são disparadas em sequência curta.
Estratégia: pausa REAL entre episódios, retry com espera longa em
RESOURCE_EXHAUSTED (máx 5 tentativas, backoff 60→600s), recibo por episódio,
nome do arquivo com o capítulo REAL (MEM-XX do header físico), nunca epXX_memXX
por índice (bug corrigido).
"""
import io, sys, json, os, pathlib, time, hashlib, re, importlib.util
sys.path.insert(0, os.getcwd())
from agent_runners.nlm_executor import NlmPodcastExecutor

def sha(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()

exe = NlmPodcastExecutor(bin_path=".venv/bin/nlm")
sm = importlib.util.spec_from_file_location("nlm_phys", "agent_runners/nlm_executor.py")
m = importlib.util.module_from_spec(sm); sys.modules["nlm_phys"]=m; sm.loader.exec_module(m)
texto = io.open("projetos/molambudos/molambudos.md", encoding="utf-8").read()
caps = m.segmentar_por_capitulo(texto)
OUT = pathlib.Path("research/producao_real/audio")
LOG = OUT / "retomada_16_26.log"

def op_com_backoff(fn, *a, nome="op", **k):
    """Executa fn com retry anti-RESOURCE_EXHAUSTED: espera real + backoff."""
    for tentativa in range(5):
        r = fn(*a, **k)
        if r.success and (r.result_id or r.artifact_path or "concluida" in (r.reason or "")):
            return r
        err = (r.reason or "").lower()
        if "resource_exhausted" in err or "rate limit" in err:
            espera = 60 * (2 ** tentativa)  # 60, 120, 240, 480, 600
            LOG.open("a").write(time.strftime("%H:%M:%S") + f"  …{nome} rate-limit, espera {espera}s (tent {tentativa+1})\n")
            time.sleep(min(espera, 600))
            continue
        return r  # erro não-rate-limit: reporta e segue
    return r

for idx in range(15, len(caps)):  # trechos 16..26
    cap = caps[idx]; num = idx + 1
    titulo = cap.splitlines()[0].strip().replace('#', '').strip()
    mm = re.match(r"MEM[- ]?(\d+)", titulo)
    fname = f"podcast_ep{num:02d}_mem{int(mm.group(1)):02d}.m4a" if mm else f"podcast_ep{num:02d}_memXX.m4a"
    outp = OUT / fname
    try:
        LOG.open("a").write(time.strftime("%H:%M:%S") + f" [EP{num:02d}] {titulo} iniciando…\n")
        r1 = op_com_backoff(exe.create_notebook, f"Molambudos EP{num} — {titulo[:40]}", nome=f"create_notebook EP{num}")
        nb_id = r1.result_id or ""
        if not nb_id:
            raise RuntimeError(f"sem notebook_id: {r1.reason}")
        r2 = op_com_backoff(exe.add_source_text, nb_id, cap, nome=f"source EP{num}")
        if not r2.success:
            raise RuntimeError(f"source add falhou: {r2.reason}")
        r3 = op_com_backoff(exe.create_audio, nb_id, fmt="deep_dive", length="long", language="pt-BR", timeout=900, nome=f"audio EP{num}")
        art_id = r3.result_id or ""
        if not art_id:
            raise RuntimeError(f"sem artifact_id: {r3.reason}")
        # download com janela real (o servidor leva ~5-10min para completar)
        deadline = time.time() + 15*60; ok=False
        while time.time() < deadline:
            r4 = exe.download_audio(nb_id, art_id, str(OUT), filename=fname, retries=1, wait=1.0, timeout=60)
            if outp.exists() and outp.stat().st_size > 0:
                ok = True; break
            time.sleep(60)
        rec = {"ep": num, "titulo": titulo, "notebook_id": nb_id, "artifact_id": art_id,
               "ok": ok, "arquivo": str(outp) if ok else "", "bytes": outp.stat().st_size if ok else 0,
               "sha256": sha(str(outp)) if ok else "", "ts": time.strftime("%Y-%m-%d %H:%M:%S")}
        (OUT / f"receipt_ep{num:02d}.json").write_text(json.dumps(rec, indent=2, ensure_ascii=False))
        msg = f"[EP{num:02d}] {'OK' if ok else 'FALHA'} | {titulo} | {'%.1fMB'%(outp.stat().st_size/1e6) if ok else '—'}"
        print(msg, flush=True); LOG.open("a").write(time.strftime("%H:%M:%S") + " " + msg + "\n")
    except Exception as e:
        msg = f"[EP{num:02d}] ERRO {e}"
        print(msg, flush=True); LOG.open("a").write(time.strftime("%H:%M:%S") + " " + msg + "\n")
    # pausa real entre episódios para não re-triggar rate limit
    if num < len(caps):
        LOG.open("a").write(time.strftime("%H:%M:%S") + f"  …pausa anti-rate-limit 90s antes do EP{num+1:02d}\n")
        time.sleep(90)
print("=== RETOMADA 16..26 CONCLUÍDA ===")
