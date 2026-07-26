import os
import sys
import time
from huggingface_hub import snapshot_download

MODEL_REPO = "mateogrgic/GLM-5.2-colibri-int4-with-int8-mtp"
TARGET_DIR = "/home/marceloclaro/models/glm52_i4"

os.makedirs(TARGET_DIR, exist_ok=True)

print(f"Iniciando download do modelo {MODEL_REPO} (~357.4 GB) para {TARGET_DIR}...")
start_time = time.time()

try:
    snapshot_download(
        repo_id=MODEL_REPO,
        local_dir=TARGET_DIR,
        max_workers=8,
        resume_download=True
    )
    elapsed = time.time() - start_time
    print(f"Download concluído com sucesso em {elapsed/3600:.2f} horas!")
except Exception as e:
    print(f"Erro durante o download do modelo: {e}", file=sys.stderr)
    sys.exit(1)
