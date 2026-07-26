# -*- coding: utf-8 -*-
"""
Interactive / One-Shot Runner para o modelo OLMoE no Colibri
============================================================
Converte o prompt de texto em token_ids, executa o motor C compilado do OLMoE
e decodifica os token_ids de saída de volta para texto em Português BR.
"""

import sys
import os
import json
import subprocess
import tempfile
from pathlib import Path

MODEL_DIR = Path("/home/marceloclaro/models/olmoe_merged")
ENGINE_BIN = Path("/home/marceloclaro/opencode-ecosystem-core/colibri/c/olmoe")

def run_prompt(prompt_text: str, max_new_tokens: int = 16) -> str:
    from tokenizers import Tokenizer
    tokenizer_path = MODEL_DIR / "tokenizer.json"
    if not tokenizer_path.exists():
        return f"Erro: {tokenizer_path} não encontrado."
    
    tokenizer = Tokenizer.from_file(str(tokenizer_path))
    encoded = tokenizer.encode(prompt_text)
    prompt_ids = encoded.ids
    
    ref_data = {
        "prompt_ids": prompt_ids,
        "full_ids": prompt_ids + [0] * max_new_tokens
    }
    
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(ref_data, f)
        temp_json_path = f.name
        
    try:
        env = dict(os.environ, SNAP=str(MODEL_DIR))
        cmd = [str(ENGINE_BIN), "32", "4", temp_json_path]
        res = subprocess.run(cmd, env=env, capture_output=True, text=True)
        stdout = res.stdout
        
        # Parse stdout for C engine generated tokens
        lines = stdout.splitlines()
        for line in lines:
            if line.startswith("C engine :"):
                tokens_str = line.replace("C engine :", "").strip()
                token_ids = [int(t) for t in tokens_str.split() if t.isdigit()]
                # Decode generated tokens
                generated_text = tokenizer.decode(token_ids)
                return generated_text
        return stdout
    finally:
        if os.path.exists(temp_json_path):
            os.remove(temp_json_path)

if __name__ == "__main__":
    prompt = sys.argv[1] if len(sys.argv) > 1 else "Explique o que e inteligencia artificial em poucas palavras:"
    print(f"Prompt: {prompt}\n")
    print("Executando Colibri (OLMoE C Engine)...")
    output = run_prompt(prompt)
    print("\nResposta Gerada:")
    print(output)
