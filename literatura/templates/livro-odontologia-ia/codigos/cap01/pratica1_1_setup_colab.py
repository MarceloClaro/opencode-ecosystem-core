"""Setup do ambiente Google Colab para Odontologia & IA.
Capítulo 1 — Prática 1.1.
"""

import sys
import importlib

# Lista de bibliotecas obrigatórias
BIBLIOTECAS = [
    "numpy",
    "pandas",
    "matplotlib",
    "cv2",
    "PIL",
    "tensorflow",
    "torch",
    "torchvision",
    "sklearn",
    "seaborn",
    "tqdm",
]

# Mapeamento de nome de import para nome de exibição
NOMES_AMIGAVEIS = {
    "cv2": "OpenCV",
    "PIL": "Pillow",
    "torch": "PyTorch",
    "torchvision": "TorchVision",
    "sklearn": "Scikit-learn",
    "tqdm": "TQDM",
}

# Versões esperadas (apenas major.minor)
VERSAO_MINIMA = {
    "numpy": "1.21",
    "pandas": "1.3",
    "tensorflow": "2.10",
    "torch": "1.13",
    "sklearn": "1.0",
}


def verificar_biblioteca(nome_modulo):
    """Verifica se uma biblioteca está instalada e sua versão."""
    try:
        modulo = importlib.import_module(nome_modulo)
        versao = getattr(modulo, "__version__", "desconhecida")
        if nome_modulo in VERSAO_MINIMA:
            minimo = tuple(int(x) for x in VERSAO_MINIMA[nome_modulo].split("."))
            atual = tuple(int(x) for x in versao.split(".")[:2])
            if atual < minimo:
                return False, versao, VERSAO_MINIMA[nome_modulo]
        return True, versao, None
    except ImportError:
        return False, None, None


def main():
    """Função principal de verificação."""
    print("=" * 50)
    print("VERIFICAÇÃO DO AMBIENTE — Odontologia & IA")
    print("=" * 50)
    print(f"Python: {sys.version.split()[0]}")
    print("-" * 50)

    status_geral = True

    for lib in BIBLIOTECAS:
        nome_exib = NOMES_AMIGAVEIS.get(lib, lib)
        ok, versao, minimo = verificar_biblioteca(lib)

        if ok:
            print(f"  ✅ {nome_exib:20s} {versao}")
        else:
            if versao:
                print(f"  ❌ {nome_exib:20s} {versao} (mínimo: {minimo})")
                status_geral = False
            else:
                print(f"  ❌ {nome_exib:20s} não instalada")
                status_geral = False

    print("-" * 50)
    if status_geral:
        print("✅ RESULTADO: Todas as bibliotecas estão OK.")
        print("   Ambiente pronto para o Capítulo 1!")
    else:
        print("❌ RESULTADO: Algumas bibliotecas precisam ser instaladas.")
        sys.exit(1)

    print("=" * 50)


if __name__ == "__main__":
    main()