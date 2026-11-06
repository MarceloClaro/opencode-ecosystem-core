#!/usr/bin/env python3
"""
linha_tempo_ia_odontologia.py — Linha do Tempo Interativa da IA na Odontologia
Autor: Edson Laranjeiras — Livro OdontoIA
Uso: Execute no Google Colab para visualizar a evolução histórica da IA odontológica.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# Dados da linha do tempo: (ano, evento, categoria)
eventos = [
    (1943, "McCulloch & Pitts: primeiro modelo matemático de neurônio artificial", "fundacao"),
    (1950, "Turing: 'Computing Machinery and Intelligence' — o Teste de Turing", "fundacao"),
    (1956, "Conferência de Dartmouth: nascimento oficial da IA", "fundacao"),
    (1965, "Primeiro sistema especialista médico (DENDRAL)", "medico"),
    (1972, "MYCIN: sistema especialista para diagnóstico de infecções", "medico"),
    (1986, "Rumelhart, Hinton & Williams: backpropagation popularizada", "fundacao"),
    (1989, "LeCun: LeNet — primeira CNN aplicada (reconhecimento de dígitos)", "fundacao"),
    (1993, "Hammond et al.: sistema especialista para próteses parciais removíveis", "odonto"),
    (1998, "Brickley, Shepherd & Armstrong: primeiras redes neurais em odontologia", "odonto"),
    (2001, "Schleyer & Spallek: informática odontológica como pilar clínico", "odonto"),
    (2006, "Hinton: deep belief networks — renascimento do deep learning", "fundacao"),
    (2012, "AlexNet vence ImageNet: era do deep learning", "fundacao"),
    (2015, "Ronneberger: U-Net para segmentação de imagens biomédicas", "fundacao"),
    (2017, "Detecção de cáries em radiografias panorâmicas com CNN", "odonto"),
    (2018, "Segmentação de lesões periapicais com U-Net", "odonto"),
    (2019, "Classificação de lesões bucais com EfficientNet (Schwendicke et al.)", "odonto"),
    (2020, "Primeira revisão sistemática abrangente de IA em odontologia", "odonto"),
    (2021, "Khanagar et al.: revisão sistemática de 20 anos (2000-2020)", "odonto"),
    (2022, "CariesNet (Zhu et al.): segmentação multi-estágio de cáries", "odonto"),
    (2023, "Gêmeos digitais em planejamento de implantes (Gholamalizadeh)", "odonto"),
    (2024, "LLMs + RAG aplicados à documentação odontológica", "odonto"),
    (2025, "González Herrera: análise bibliométrica das 3 fases históricas", "odonto"),
    (2026, "OdontoIA Book: 500 laudas, 28 capítulos, 93 testes SDD/TDD", "odonto"),
]

cores = {"fundacao": "#2E86C1", "medico": "#E67E22", "odonto": "#27AE60"}
labels = {"fundacao": "Fundação da IA", "medico": "IA Médica", "odonto": "IA Odontológica"}

# Criar a figura
fig, ax = plt.subplots(figsize=(16, 10))

for i, (ano, evento, cat) in enumerate(eventos):
    y = len(eventos) - i
    cor = cores[cat]
    ax.plot(ano, y, 'o', color=cor, markersize=10, zorder=5)
    ax.text(ano + 0.3, y, f"{evento}", fontsize=9, va='center',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=cor, alpha=0.15))

# Linha vertical no ano atual
ax.axvline(x=2026, color='red', linestyle='--', alpha=0.3, label='2026 (presente)')

ax.set_xlabel('Ano', fontsize=12)
ax.set_title('Linha do Tempo: IA na Odontologia (1943–2026)', fontsize=14, fontweight='bold')
ax.set_yticks([])
ax.grid(axis='x', alpha=0.3)

# Legenda
patches = [mpatches.Patch(color=cores[k], label=labels[k]) for k in cores]
ax.legend(handles=patches, loc='lower right', fontsize=10)

plt.tight_layout()
plt.show()

# ============================================================
# SDD — Especificação
# ============================================================
"""
SPEC: visualizar_linha_tempo_ia_odontologia() -> None

Problema: O leitor precisa compreender visualmente a evolução
da IA aplicada à odontologia, desde os fundamentos da computação
(1943) até o estado da arte atual.

Entrada: Dados estruturados (ano, evento, categoria)
Saída: Gráfico com linha do tempo interativa
Critérios de aceitação:
    1. Todos os eventos de 1943–2026 devem estar visíveis
    2. Eventos odontológicos devem ser destacados em verde
    3. O gráfico deve ser gerado sem erros
    4. A legenda deve diferenciar as 3 categorias
"""

# ============================================================
# TDD — Testes
# ============================================================
def test_todos_eventos_presentes():
    """Verifica que todos os 23 eventos estão na lista."""
    assert len(eventos) == 23, f"Esperado 23 eventos, encontrado {len(eventos)}"

def test_categorias_validas():
    """Verifica que todas as categorias são válidas."""
    categorias = {cat for _, _, cat in eventos}
    assert categorias.issubset({"fundacao", "medico", "odonto"}), \
        f"Categorias inválidas: {categorias - {'fundacao', 'medico', 'odonto'}}"

def test_anos_crescentes():
    """Verifica que os anos estão em ordem crescente."""
    anos = [ano for ano, _, _ in eventos]
    for i in range(1, len(anos)):
        assert anos[i] >= anos[i-1], f"Ano {anos[i]} antes de {anos[i-1]}"

def test_primeiro_evento():
    """Verifica que o primeiro evento é de 1943."""
    assert eventos[0][0] == 1943, f"Primeiro ano deveria ser 1943, é {eventos[0][0]}"

def test_ultimo_evento():
    """Verifica que o último evento é de 2026."""
    assert eventos[-1][0] == 2026, f"Último ano deveria ser 2026, é {eventos[-1][0]}"

if __name__ == "__main__":
    test_todos_eventos_presentes()
    test_categorias_validas()
    test_anos_crescentes()
    test_primeiro_evento()
    test_ultimo_evento()
    print("✅ Todos os testes passaram!")
    print(f"📊 {len(eventos)} eventos na linha do tempo")
    print("🟢 1943–2026: Da teoria do neurônio artificial ao OdontoIA Book")
    visualizar_linha_tempo_ia_odontologia()  # Esta função chamaria plt.show()
