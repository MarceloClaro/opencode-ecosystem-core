#!/usr/bin/env python3
"""Recuperação de downloads dos artifacts pendentes (SPEC-973): ler receipts ok=False
com artifact_id e baixar com janela longa real (até 30min por áudio)."""
import json, sys, os, pathlib, time, hashlib
sys.path.insert(0, os.getcwd())
from agent_runners.nlm_executor import NlmPodcastExecutor

def sha(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
exe = NlmPodcastExecutor(bin_path=".venv/bin/nlm")
OUT = pathlib.Path("research/producao_real/audio")
LOG = OUT / "recuperacao.log"

pendentes = []
for rp in sorted(OUT.glob("receipt_ep[0-9][0-9].json")):
    r = json.loads(rp.read_text())
    arq = r.get("arquivo") or ""
    arquivo_inexistente = (not arq) or (not (OUT / arq).exists())
    if not r.get("ok") and r.get("artifact_id") and arquivo_inexistente:
        pendentes.append(r)
LOG.open("a").write(time.strftime("%H:%M:%S") + f" pendentes: {[p['ep'] for p in pendentes]}\n")
print(f"pendentes: {[p['ep'] for p in pendentes]}", flush=True)

for r in pendentes:
    ep = r["ep"]; nb = r["notebook_id"]; art = r["artifact_id"]
    # nome real do capitulo vem do titulo do receipt
    import re
    mm = re.match(r"MEM[- ]?(\d+)", r.get("titulo",""))
    fname = f"podcast_ep{ep:02d}_mem{int(mm.group(1)):02d}.m4a" if mm else f"podcast_ep{ep:02d}_memXX.m4a"
    outp = OUT / fname
    ok = False
    t0 = time.time()
    while time.time() - t0 < 30*60:
        try:
            exe.download_audio(nb, art, str(OUT), filename=fname, retries=2, wait=20.0, timeout=120)
        except Exception:
            pass
        if outp.exists() and outp.stat().st_size > 0:
            ok = True; break
        time.sleep(45)
    r["ok"] = ok
    if ok:
        r["arquivo"] = str(outp); r["bytes"] = outp.stat().st_size; r["sha256"] = sha(str(outp))
    r["ts_recuperacao"] = time.strftime("%Y-%m-%d %H:%M:%S")
    (OUT / f"receipt_ep{ep:02d}.json").write_text(json.dumps(r, indent=2, ensure_ascii=False))
    msg = f"[EP{ep:02d}] recup={'OK' if ok else 'FALHA'} | {r.get('titulo','')[:24]} | {'%.1fMB'%(outp.stat().st_size/1e6) if ok else '—'}"
    print(msg, flush=True); LOG.open("a").write(time.strftime("%H:%M:%S") + " " + msg + "\n")
print("=== RECUPERACAO CONCLUIDA ===", flush=True)
