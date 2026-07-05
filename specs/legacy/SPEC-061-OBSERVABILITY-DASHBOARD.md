# SPEC-061: Observability Dashboard (Fase C)

## Status: PROPOSED
## Autor: Marcelo Claro (Orquestrador Supremo) & Antigravity pair programmer
## Data: 2026-06-29
## Ciclo: R30

---

## 1. Visão Geral

Esta especificação define o design e a implementação da **Fase C (Observability Dashboard)** para o **OpenCode Ecosystem**.

O painel de observabilidade em tempo real é uma interface web auto-contida que expõe o status operacional e cognitivo do ecossistema. Ele consolida os outputs dos 5 scanners principais (Noológico, Teleológico, Evolutivo, Potencialidade v2 e Impacto Social), rastreia a evolução da **Energia Livre Variacional (VFE)** calculada pelo Active Inference Controller e visualiza a topologia epistemológica do ecossistema.

---

## 2. Objetivos e Requisitos

* **O1**: Atualizar o servidor HTTP [dashboard_server.py](file:///C:/Users/marce/Documents/OpenCode_Ecosystem/nexus/dashboard_server.py) para expor as novas métricas dos 5 scanners e da inferência ativa.
* **O2**: Desenvolver a visualização da **Curva de Convergência da Energia Livre (VFE)** ao longo do tempo utilizando Chart.js.
* **O3**: Exibir o status de saúde do ecossistema baseado nos priors cognitivos (system_health, noological_coverage, etc.).
* **O4**: Criar uma suíte de testes TDD com 12+ CTs (`specs/test_dashboard.py`) validando as rotas da API REST do painel.
* **O5**: Disponibilizar ferramenta MCP/CLI para iniciar e parar o dashboard de forma assíncrona.

---

## 3. Arquitetura de Dados da API

O endpoint `/api/dados` será enriquecido para retornar a seguinte estrutura JSON consolidada:

```json
{
  "scanners": {
    "noological": { "coverage_pct": 32.0, "gaps_count": 8 },
    "teleological": { "score": 80.0, "gaps_count": 1 },
    "evolutionary": { "maturity_level": "N2", "bottlenecks_count": 2 },
    "potentiality_v2": { "total_opportunities": 65, "viable_count": 21 },
    "social_impact": { "sroi_ratio": 2.55, "consolidated_score": 62.9 }
  },
  "active_inference": {
    "current_vfe": 1.25,
    "priors_status": {
      "system_health": { "target": 1.0, "observed": 0.98 },
      "noological_coverage": { "target": 0.85, "observed": 0.32 }
    },
    "history": [
      { "timestamp": "2026-06-29T12:00:00Z", "free_energy": 2.45 },
      { "timestamp": "2026-06-29T13:00:00Z", "free_energy": 1.25 }
    ]
  },
  "system_totals": {
    "skills": 227,
    "agents": 128,
    "mcps": 46
  }
}
```

---

## 4. UI e Estética Visual

Seguindo o design de **Ricas Estéticas Premium** do Antigravity:
* **Tema Escuro Profundo (Deep Dark Mode)**: Fundo `#0B0F19`, cartões translúcidos com glassmorphism (`backdrop-filter: blur(12px)`).
* **Cores de Destaque Vibrantes**:
  * Gradientes roxo-azulados para tecnologia e potencial (`linear-gradient(135deg, #6366F1, #3B82F6)`).
  * Esmeralda neon para sucesso e saúde do sistema (`#10B981`).
  * Amber/Laranja neon para erros, câmara de eco e aviso de alta energia livre (`#F59E0B`).
* **Tipografia Elegante**: Inter / Outfit da Google Fonts.
* **Componentes Interativos**: Hover de micro-animações em cards de métricas e gráficos interativos Chart.js.

---

## 5. Ferramentas MCP Associadas

Novas ferramentas expostas nocapabilities server:
* `eco_dashboard_start`: Inicializa o servidor HTTP na porta 8081 em background.
* `eco_dashboard_stop`: Para o processo do servidor HTTP ativo.
* `eco_dashboard_status`: Retorna se o servidor web está ativo e respondendo na porta configurada.
