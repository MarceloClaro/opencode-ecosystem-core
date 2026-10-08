import nbformat, time
from nbclient import NotebookClient
nb=nbformat.read("OdontoCA_v1_4_0_CLINICAL_PREDICTION.ipynb",as_version=4)
t=time.time(); err=None
try:
    NotebookClient(nb,timeout=1800,kernel_name="python3",
                   resources={"metadata":{"path":"/tmp/OdontoCA_v1_3_5"}}).execute()
except Exception as e:
    err=f"{type(e).__name__}: {str(e)[:400]}"
el=time.time()-t
code=[c for c in nb.cells if c.cell_type=="code"]
bad=[i for i,c in enumerate(nb.cells) if c.cell_type=="code"
     and any(o.get("output_type")=="error" for o in c.get("outputs",[]))]
print(f"execucao: {'OK' if not err else 'FALHOU'}  tempo={el:.1f}s  codigo={len(code)}  erros={len(bad)}")
if err: print("EXC:",err)
for i in bad[-3:]:
    print(f"\n--- erro celula nb {i} ---")
    for o in nb.cells[i].outputs:
        if o.get("output_type")=="error":
            print(o.get("ename"),"|",o.get("evalue"))
            print("\n".join((o.get("traceback") or [])[-8:]))
if not bad:
    nbformat.write(nb,"OdontoCA_v1_4_0_CLINICAL_PREDICTION.ipynb")
    print("SALVO COM SAIDAS REAIS")
