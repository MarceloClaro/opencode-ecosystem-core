#!/usr/bin/env python3
"""Produção real do podcast Molambudos por capítulo — SPEC-973 (lote 2..26).
Pipeline validado no piloto EP1 (R552): notebook create → source add → audio create
→ download (espera real ~6min) → recibo físico por episódio. NADA prometido:
each episódio só é reportado como concluído quando o m4a físico + sha256 existem.
"""
import io, sys, json, os, pathlib, time, hashlib
sys.path.insert(0, os.getcwd())
from agent_runners.nlm_executor import NlmPodcastExecutor, NlmPodcastReceipt

def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()

exe = NlmPodcastExecutor(bin_path=".venv/bin/nlm")
spec = importlib_util = None
import importlib.util
sm = importlib.util.spec_from_file_location("nlm_phys","agent_runners/nlm_executor.py")
m = importlib.util.module_from_spec(sm); sys.modules["nlm_phys"]=m; sm.loader.exec_module(m)
texto = io.open("projetos/molambudos/molambudos.md", encoding="utf-8").read()
caps = m.segmentar_por_capitulo(texto)
OUT = pathlib.Path("research/producao_real/audio")
LOG = pathlib.Path("research/producao_real/audio/lote_2_26.log")
resumo = []
for idx in range(1, len(caps)):  # 2..26
    cap = caps[idx]
    num = idx + 1
    titulo = cap.splitlines()[0].strip().replace('#','').strip()
    fname = f"podcast_ep{num:02d}_mem{num:02d}.m4a"
    outp = OUT / fname
    try:
        r1 = exe.create_notebook(f"Molambudos EP{num} — {titulo[:40]}")
        nb_id = r1.result_id or ""
        if not nb_id:
            raise RuntimeError(f"sem notebook_id: {r1.reason}")
        r2 = exe.add_source_text(nb_id, cap)
        if not r2.success:
            raise RuntimeError(f"source add falhou: {r2.reason}")
        r3 = exe.create_audio(nb_id, fmt="deep_dive", length="long", language="pt-BR", timeout=900)
        art_id = r3.result_id or ""
        if not art_id:
            raise RuntimeError(f"sem artifact_id: {r3.reason}")
        deadline = time.time() + 12*60
        ok = False
        while time.time() < deadline:
            r4 = exe.download_audio(nb_id, art_id, str(OUT), filename=fname, retries=1, wait=1.0, timeout=60)
            if outp.exists() and outp.stat().st_size > 0 and sha(str(outp)).startswith("d82944b8") is False or (outp.exists() and outp.stat().st_size > 0):
                ok = True
                break
            time.sleep(45)
        if not ok:
            # tenta mais um ciclo de espera pesado (até 12min) — servidor às vezes demora
            deadline = time.time() + 12*60
            while time.time() < deadline:
                r4 = exe.download_audio(nb_id, art_id, str(OUT), filename=fname, retries=1, wait=1.0, timeout=60)
                if outp.exists() and outp.stat().st_size > 0:
                    ok = True
                    break
                time.sleep(45)
        rec = {"ep": num, "titulo": titulo, "notebook_id": nb_id, "artifact_id": art_id,
               "ok": ok, "arquivo": str(outp) if ok else "", "bytes": outp.stat().st_size if ok else 0,
               "sha256": sha(str(outp)) if ok else "", "ts": time.strftime("%Y-%m-%d %H:%M:%S")}
        (OUT / f"receipt_ep{num:02d}.json").write_text(json.dumps(rec, indent=2, ensure_ascii=False))
        resumo.append(rec)
        msg = f"[EP{num:02d}] {'OK' if ok else 'FALHA'} | {titulo} | {'%.1fMB'%(outp.stat().st_size/1e6) if ok else ''}"
        print(msg, flush=True); LOG.open("a").write(time.strftime("%H:%M:%S ") + msg + "\n")
    except Exception as e:
        msg = f"[EP{num:02d}] ERRO {e}"
        print(msg, flush=True); LOG.open("a").write(time.strftime("%H:%M:%S ") + msg + "\n")
print("=== LOTE 2..26 CONCLUÍDO ===")
print("  ok:", sum(1 for r in resumo if r["ok"]), "| falhas:", sum(1 for r in resumo if not r["ok"]))
