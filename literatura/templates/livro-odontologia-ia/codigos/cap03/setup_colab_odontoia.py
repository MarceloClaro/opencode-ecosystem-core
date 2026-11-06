#!/usr/bin/env python3
"""setup_colab_odontoia.py — Setup inicial no Google Colab para o livro OdontoIA."""
print("🦷 OdontoIA — Ambiente configurado!")
print("✅ Python", __import__('sys').version.split()[0])
# Verificar pacotes essenciais
for pkg in ['numpy', 'pandas', 'matplotlib', 'sklearn']:
    try:
        __import__(pkg)
        print(f"✅ {pkg}")
    except ImportError:
        print(f"⚠️ {pkg} — instale com !pip install {pkg}")
