"""
Prática 16.1 — Auditoria de Repositório GitHub Odontológico
Protocolo G1-G3 de confiabilidade com verificação completa
"""
import json

# ============================================================
# PROTOCOLO DE AUDITORIA G1 → G3
# ============================================================

AUDIT_CHECKLIST = {
    "g1_basico": [
        "README.md existe e está em inglês ou português",
        "Arquivo LICENSE presente",
        "requirements.txt ou environment.yml",
        "Código executável sem erros de sintaxe",
        "Estrutura de diretórios organizada",
    ],
    "g2_intermediario": [
        "Citação de artigo/DOI associado",
        "Dataset documentado (fonte, tamanho, licença)",
        "Scripts de treinamento reproduzíveis",
        "Métricas reportadas (accuracy, sensitivity, specificity)",
        "Testes automatizados (pytest/unittest)",
    ],
    "g3_avancado": [
        "Modelo pré-treinado disponível (Hugging Face, Zenodo)",
        "Dockerfile para ambiente containerizado",
        "CI/CD pipeline (GitHub Actions)",
        "Model Card ou Data Sheet",
        "Reprodutibilidade validada por terceiros",
    ],
}


def audit_repository(repo_name: str, repo_url: str, features: dict) -> dict:
    """
    Audita um repositório odontológico conforme níveis G1-G3.
    
    Args:
        repo_name: Nome do repositório
        repo_url: URL do GitHub
        features: Dicionário com features detectadas
    
    Returns:
        Relatório de auditoria com nível e score
    """
    score_g1 = sum(1 for f in AUDIT_CHECKLIST["g1_basico"] if features.get(f, False))
    score_g2 = sum(1 for f in AUDIT_CHECKLIST["g2_intermediario"] if features.get(f, False))
    score_g3 = sum(1 for f in AUDIT_CHECKLIST["g3_avancado"] if features.get(f, False))
    
    total_g1 = len(AUDIT_CHECKLIST["g1_basico"])
    total_g2 = len(AUDIT_CHECKLIST["g2_intermediario"])
    total_g3 = len(AUDIT_CHECKLIST["g3_avancado"])
    
    # Determina nível
    if score_g1 == total_g1 and score_g2 == total_g2 and score_g3 >= 4:
        nivel = "G3 — Avançado (Produção)"
    elif score_g1 == total_g1 and score_g2 >= 4:
        nivel = "G2 — Intermediário (Pesquisa)"
    elif score_g1 >= 4:
        nivel = "G1 — Básico (Exploratório)"
    else:
        nivel = "G0 — Insuficiente"
    
    return {
        "repo_name": repo_name,
        "repo_url": repo_url,
        "nivel": nivel,
        "score": {
            "g1": f"{score_g1}/{total_g1}",
            "g2": f"{score_g2}/{total_g2}",
            "g3": f"{score_g3}/{total_g3}",
        },
        "recomendacao": (
            "Pronto para uso clínico-assistido"
            if "G3" in nivel
            else "Adequado para pesquisa"
            if "G2" in nivel
            else "Requer melhorias antes do uso"
        ),
    }


# ============================================================
# ESTUDOS DE CASO: Repositórios IA-Odontológica
# ============================================================

REPOSITORIES = {
    "OdontoAI": {
        "url": "https://github.com/odontoai/classification",
        "features": {
            "README.md existe e está em inglês ou português": True,
            "Arquivo LICENSE presente": True,
            "requirements.txt ou environment.yml": True,
            "Código executável sem erros de sintaxe": True,
            "Estrutura de diretórios organizada": True,
            "Citação de artigo/DOI associado": True,
            "Dataset documentado (fonte, tamanho, licença)": True,
            "Scripts de treinamento reproduzíveis": True,
            "Métricas reportadas (accuracy, sensitivity, specificity)": True,
            "Testes automatizados (pytest/unittest)": False,
            "Modelo pré-treinado disponível (Hugging Face, Zenodo)": True,
            "Dockerfile para ambiente containerizado": False,
            "CI/CD pipeline (GitHub Actions)": True,
            "Model Card ou Data Sheet": True,
            "Reprodutibilidade validada por terceiros": False,
        },
    },
    "DENTEX": {
        "url": "https://github.com/ibrahimethemhamamci/DENTEX",
        "features": {
            "README.md existe e está em inglês ou português": True,
            "Arquivo LICENSE presente": True,
            "requirements.txt ou environment.yml": True,
            "Código executável sem erros de sintaxe": True,
            "Estrutura de diretórios organizada": True,
            "Citação de artigo/DOI associado": True,
            "Dataset documentado (fonte, tamanho, licença)": True,
            "Scripts de treinamento reproduzíveis": True,
            "Métricas reportadas (accuracy, sensitivity, specificity)": True,
            "Testes automatizados (pytest/unittest)": True,
            "Modelo pré-treinado disponível (Hugging Face, Zenodo)": True,
            "Dockerfile para ambiente containerizado": True,
            "CI/CD pipeline (GitHub Actions)": True,
            "Model Card ou Data Sheet": True,
            "Reprodutibilidade validada por terceiros": True,
        },
    },
    "ToothSeg": {
        "url": "https://github.com/liangjiubujiu/ToothSeg",
        "features": {
            "README.md existe e está em inglês ou português": True,
            "Arquivo LICENSE presente": True,
            "requirements.txt ou environment.yml": True,
            "Código executável sem erros de sintaxe": True,
            "Estrutura de diretórios organizada": True,
            "Citação de artigo/DOI associado": True,
            "Dataset documentado (fonte, tamanho, licença)": False,
            "Scripts de treinamento reproduzíveis": True,
            "Métricas reportadas (accuracy, sensitivity, specificity)": True,
            "Testes automatizados (pytest/unittest)": False,
            "Modelo pré-treinado disponível (Hugging Face, Zenodo)": True,
            "Dockerfile para ambiente containerizado": False,
            "CI/CD pipeline (GitHub Actions)": False,
            "Model Card ou Data Sheet": False,
            "Reprodutibilidade validada por terceiros": False,
        },
    },
}


if __name__ == "__main__":
    print("=" * 70)
    print("AUDITORIA DE REPOSITÓRIOS GITHUB — IA ODONTOLÓGICA")
    print("Protocolo G1-G3 de Confiabilidade")
    print("=" * 70)
    
    results = []
    for name, data in REPOSITORIES.items():
        report = audit_repository(name, data["url"], data["features"])
        results.append(report)
        
        print(f"\n📦 {report['repo_name']}")
        print(f"   URL: {report['repo_url']}")
        print(f"   Nível: {report['nivel']}")
        print(f"   G1: {report['score']['g1']} | G2: {report['score']['g2']} | G3: {report['score']['g3']}")
        print(f"   Recomendação: {report['recomendacao']}")
    
    print("\n" + "=" * 70)
    print("RESUMO DA AUDITORIA")
    print("=" * 70)
    for r in results:
        print(f"  {r['repo_name']:15s} → {r['nivel']}")
    
    print("\n✅ Auditoria concluída!")
