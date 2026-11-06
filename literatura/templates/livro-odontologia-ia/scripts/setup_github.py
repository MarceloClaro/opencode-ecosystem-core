#!/usr/bin/env python3
"""
setup_github.py — Configura o repositório GitHub para o livro OdontoIA

Uso:
    python3 scripts/setup_github.py

    OU, com token:
    export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"
    python3 scripts/setup_github.py

Pré-requisitos:
    pip install requests PyGithub --break-system-packages
"""

import os
import subprocess
import sys

REPO_NAME = "odontoia-book"
REPO_DESC = "🦷 OdontoIA em Python: IA, Deep Learning e Gêmeos Digitais na Odontologia — Livro completo com LaTeX, Python, Colab, SDD/TDD"
REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def check_git():
    """Verifica se git está configurado."""
    result = subprocess.run(["git", "config", "user.name"], capture_output=True, text=True)
    if not result.stdout.strip():
        print("⚠️  git user.name não configurado. Configure com:")
        print("   git config user.name 'Seu Nome'")
        print("   git config user.email 'seu@email.com'")
        return False
    return True

def find_gh():
    """Encontra o caminho para o GitHub CLI (gh) oficial."""
    # Caminhos conhecidos do gh
    candidates = ["/usr/bin/gh", "/usr/local/bin/gh", "/snap/bin/gh"]
    for p in candidates:
        if os.path.exists(p):
            return p
    # Fallback: procurar no PATH (pode ser o browser opener, tentamos mesmo assim)
    which = subprocess.run(["which", "gh"], capture_output=True, text=True)
    if which.returncode == 0:
        p = which.stdout.strip()
        # Verificar se é o gh real (não o browser opener v0.0.4)
        ver = subprocess.run([p, "--version"], capture_output=True, text=True)
        if "cli/cli" in ver.stdout or "github.com" in ver.stderr:
            return p
    return None

def create_with_gh_cli():
    """Tenta criar o repo usando a GitHub CLI oficial."""
    gh_path = find_gh()
    if not gh_path:
        return False
    
    # Verificar autenticação
    auth = subprocess.run([gh_path, "auth", "status"], capture_output=True, text=True)
    if auth.returncode != 0:
        print("ℹ️  GitHub CLI encontrado mas não autenticado.")
        print(f"   Execute: {gh_path} auth login")
        print(f"   Depois execute: {gh_path} repo create {REPO_NAME} --public --push")
        return False
    
    result = subprocess.run(
        [gh_path, "repo", "create", REPO_NAME, "--public", "--description", REPO_DESC, "--source", ".", "--push"],
        capture_output=True, text=True, cwd=REPO_DIR
    )
    print(result.stdout)
    if result.returncode == 0:
        print(f"✅ Repositório criado: https://github.com/{REPO_NAME}")
        return True
    else:
        print(f"❌ Erro gh CLI: {result.stderr}")
        return False

def create_with_api():
    """Cria repo via GitHub API usando requests."""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("❌ GITHUB_TOKEN não definido.")
        print("   Crie um token em: https://github.com/settings/tokens")
        print("   Depois execute: export GITHUB_TOKEN='ghp_...'")
        return False
    
    try:
        import requests
    except ImportError:
        print("❌ requests não instalado. Instale com: pip install requests --break-system-packages")
        return False

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json"
    }
    
    # Criar repo
    data = {
        "name": REPO_NAME,
        "description": REPO_DESC,
        "private": False,
        "has_issues": True,
        "has_wiki": True,
        "has_projects": True,
        "homepage": "https://odontoia.com.br"
    }
    
    r = requests.post("https://api.github.com/user/repos", json=data, headers=headers)
    if r.status_code == 201:
        repo_url = r.json()["html_url"]
        print(f"✅ Repositório criado: {repo_url}")
        
        # Adicionar remote e push
        subprocess.run(["git", "remote", "add", "origin", f"https://github.com/{r.json()['full_name']}.git"], cwd=REPO_DIR)
        subprocess.run(["git", "branch", "-M", "main"], cwd=REPO_DIR)
        subprocess.run(["git", "push", "-u", "origin", "main"], cwd=REPO_DIR)
        return True
    else:
        print(f"❌ Erro API: {r.status_code} {r.text}")
        return False

def manual_instructions():
    """Instruções manuais para criar o repo."""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║  📦 INSTRUÇÕES PARA CRIAR O REPOSITÓRIO GITHUB                ║
╚═══════════════════════════════════════════════════════════════╝

1️⃣  Vá para: https://github.com/new
2️⃣  Nome do repositório: """ + REPO_NAME + """
3️⃣  Descrição: """ + REPO_DESC + """
4️⃣  Visibilidade: Public
5️⃣  NÃO inicialize com README (já existe)
6️⃣  Clique "Create repository"

7️⃣  Execute no terminal:
   cd """ + REPO_DIR + """
   git remote add origin https://github.com/SEU_USUARIO/""" + REPO_NAME + """.git
   git branch -M main
   git push -u origin main

8️⃣  Opcional — crie um release:
   gh release create v1.0.0 --title "v1.0.0 — Lançamento inicial" --notes "Estrutura completa do livro OdontoIA"

╔═══════════════════════════════════════════════════════════════╗
║  🚀 OU: Instale o GitHub CLI para automatizar:               ║
║  sudo apt install gh && gh auth login                        ║
║  Depois execute: gh repo create odontoia-book --public --push ║
╚═══════════════════════════════════════════════════════════════╝
""")

if __name__ == "__main__":
    print("🔧 Configurando repositório GitHub para o livro OdontoIA...")
    print()
    
    if not check_git():
        sys.exit(1)
    
    # Tentar gh CLI primeiro
    if create_with_gh_cli():
        sys.exit(0)
    
    print("ℹ️  GitHub CLI não encontrado. Tentando via API...")
    print()
    
    # Tentar API
    if create_with_api():
        sys.exit(0)
    
    # Instruções manuais
    manual_instructions()
