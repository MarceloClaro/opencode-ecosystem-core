#!/usr/bin/env python3
"""Gerar EP26 (MEM-26 — A Última Página) isolado, com retries longos no source add
(a falha da retomada foi no source add). SPEC-973."""
import io, json, sys, os, pathlib, time, hashlib, re, importlib.util
sys.path.insert(0, os.getcwd())
from agent_runners.nlm_executor import NlmPodcastExecutor

def sha(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
exe = NlmPodcastExecutor(bin_path=".venv/bin/nlm")
sm = importlib.util.spec_from_file_location("nlm_phys", "agent_runners/nlm_executor.py")
m = importlib.util.module_from_spec(sm); sys.modules["nlm_phys"]=m; sm.loader.exec_module(m)
texto = io.open("projetos/molambudos/molambudos.md", encoding="utf-8").read()
caps = m.segmentar_por_capitulo(texto)
cap = caps[25]
titulo = cap.splitlines()[0].strip().replace('#', '').strip()
mm = re.match(r"MEM[- ]?(\d+)", titulo)
fname = f"podcast_ep26_mem{int(mm.group(1)):02d}.m4a"
OUT = pathlib.Path("research/producao_real/audio")
LOG = OUT / "ep26.log"
def L(s): LOG.open("a").write(time.strftime("%H:%M:%S") + " " + s + "\n"); print(s, flush=True)

L(f"EP26 alvo: {titulo} | trecho {len(cap)} chars")
nb_id = ""
for t in range(4):
    r1 = exe.create_notebook(f"Molambudos EP26 — {titulo[:40]}")
    if r1.success and r1.result_id:
        nb_id = r1.result_id; break
    L(f"  create retry {t+1}: {r1.reason}"); time.sleep(30)
if not nb_id:
    L("FALHA: sem notebook_id"); sys.exit(1)
L(f"  notebook: {nb_id}")

ok2 = False
for t in range(5):
    r2 = exe.add_source_text(nb_id, cap)
    if r2.success:
        ok2 = True; break
    L(f"  source retry {t+1}: {r2.reason}"); time.sleep(45)
if not ok2:
    L("FALHA: source add não passou após retries"); sys.exit(1)
L("  ✓ source adicionada")

r3 = exe.create_audio(nb_id, fmt="deep_dive", length="long", language="pt-BR", timeout=900)
art = r3.result_id or ""
L(f"  artifact: {art}")
if not art:
    L(f"FALHA: sem artifact ({r3.reason})"); sys.exit(1)

outp = OUT / fname
ok = False; t0 = time.time()
while time.time() - t0 < 35*60:
    try:
        exe.download_audio(nb_id, art, str(OUT), filename=fname, retries=2, wait=20.0, timeout=120)
    except Exception as e:
        L(f"  dl exception: {e}")
    if outp.exists() and outp.stat().st_size > 0:
        ok = True; break
    time.sleep(45)
    L(f"  dl aguardando... ({int(time.time()-t0)}s)")
rec = {"ep":26, "titulo":titulo, "notebook_id":nb_id, "artifact_id":art, "ok":ok,
       "arquivo":str(outp) if ok else "", "bytes":outp.stat().st_size if ok else 0,
       "sha256":sha(str(outp)) if ok else "", "ts":time.strftime("%Y-%m-%d %H:%M:%S")}
(OUT/"receipt_ep26.json").write_text(json.dumps(rec, indent=2, ensure_ascii=False))
msg = f"EP26 {'OK' if ok else 'FALHA'} | {titulo} | {'%.1fMB'%(outp.stat().st_size/1e6) if ok else '—'}"
L(msg)
