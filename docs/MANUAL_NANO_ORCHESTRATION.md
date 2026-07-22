# Manual de Nano-Orquestração para Manuscritos de Grande Escala

**SPEC-935-R53** | v1.0.0 | Julho 2026

---

## 1. Visão Geral

O sistema de **Nano-Orquestração** permite que modelos LiteRT-LM (2.6B–4.6B, quantizados, 20K tokens de contexto) produzam manuscritos acadêmicos de **até 500 laudas coesas** — algo impossível para uma única chamada de API.

### Como funciona?

1. **Decomposição nanogranular**: O manuscrito é fragmentado em **5.000+ nanoblocos** de ~300 tokens cada
2. **Escrita paralela**: Pool de agentes LiteRT-LM escreve blocos simultaneamente (5-10 workers)
3. **3 Passagens de fusão**: Coerência local → global → fluidez transforma fragmentos em texto coeso
4. **Validação cruzada**: Transições, terminologia e contradições são verificadas automaticamente

### Mapa mental

```
Manuscrito (500 laudas, ~750K tokens)
        │
        ▼
┌───────────────────────────────────┐
│ 1. NanoPlanner                    │
│    500 laudas → 5.000+ nanoblocos │
└───────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────┐
│ 2. NanoSDD Engine                 │
│    3-7 critérios de aceitação     │
│    por nanobloco                  │
└───────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────┐
│ 3. ContextWindowManager           │
│    Contexto mínimo: ~300 tok      │
│    + vizinhos + citações          │
└───────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────┐
│ 4. NanoWriter Pool (paralelo)     │
│    ┌─────────┬──────────┬──────┐  │
│    │Qwen3 0.6│Gemma4 2B │4B 4B │  │
│    │~3s/bloco│~8s/bloco │~20s  │  │
│    └─────────┴──────────┴──────┘  │
└───────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────┐
│ 5. Quality Checker                │
│    Valida vs SDD. Falha →         │
│    reescreve (escala modelo)      │
└───────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────┐
│ 6. CoherenceEngine (3 passagens)  │
│    Pass 1: Local (bi-vizinho)     │
│    Pass 2: Global (por seção)     │
│    Pass 3: Fluidez (integral)     │
└───────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────┐
│ 7. CrossValidator                 │
│    Transições, terminologia,      │
│    contradições. Score ≥ 9.5      │
└───────────────────────────────────┘
        │
        ▼
Manuscrito Final Coeso (500 laudas)
```

---

## 2. Instalação e Configuração

### Pré-requisitos

- Python 3.14+
- LiteRT-LM server rodando em `localhost:9379`
- Modelos carregados: Qwen3 0.6B, Gemma 4 E2B, Gemma 4 4B
- 12GB+ RAM livre (para pool com 5 workers)

### Verificação rápida

```bash
# Verificar servidor LiteRT-LM
curl http://localhost:9379/health

# Verificar ambiente
python3 -m nano_orchestration.orchestrator --help
```

### Configuração do Pool

| Parâmetro | Default | Descrição |
|-----------|---------|-----------|
| `max_workers` | 5 | Workers paralelos (escalável até 10) |
| `max_retries` | 3 | Tentativas por bloco |
| `timeout_per_block` | 120s | Timeout máximo |
| `temperature` | 0.7 | Criatividade do modelo |
| `fallback_enabled` | True | Fallback para modelo mais leve |
| `dry_run` | False | Simulação sem modelo real |

---

## 3. Modos de Uso

### 3.1. Modo mais simples (dry-run para testes)

```python
from nano_orchestration.orchestrator import NanoOrchestrator

orch = NanoOrchestrator(dry_run=True)
report = orch.run(
    title="Meu Manuscrito",
    sections=[
        ("Introdução", 10),
        ("Fundamentação Teórica", 30),
    ],
)
print(f"Score de coesão: {report.cohesion_score}/10")
```

### 3.2. Modo produção (com LiteRT-LM real)

```python
from nano_orchestration.orchestrator import NanoOrchestrator
from nano_orchestration.writer import LiteRTMClient, PoolConfig

client = LiteRTMClient(base_url="http://localhost:9379/v1")
config = PoolConfig(max_workers=5, temperature=0.7)

orch = NanoOrchestrator(
    client=client,
    pool_config=config,
    dry_run=False,
)

report = orch.run(
    title="Manuscrito de 500 laudas",
    sections=[
        ("Introdução", 60),
        ("Fundamentação Teórica", 130),
        ("Metodologia", 80),
        ("Resultados", 90),
        ("Discussão", 100),
        ("Conclusão", 40),
    ],
)

print(f"Status: {'APROVADO' if report.validation_passed else 'REPROVADO'}")
print(f"Blocos: {report.successful_blocks}/{report.total_blocks}")
print(f"Qualidade: {report.avg_quality_score:.2f}")
print(f"Coesão: {report.cohesion_score:.2f}")
print(f"Tempo: {report.total_time_ms/1000:.1f}s")
```

### 3.3. Preview antes de executar

```python
from nano_orchestration.planner import NanoPlanner

planner = NanoPlanner()
preview = planner.estimate_from_pages(500)
print(f"Blocos: {preview['total_blocks']}")
print(f"Tokens: {preview['estimated_tokens']}")
print(f"Por seção: {preview['blocks_per_section']}")
```

### 3.4. Pipeline retomável

```python
# Execução inicial
orch = NanoOrchestrator(checkpoint_dir="meus_checkpoints")
report = orch.run("Meu Livro", sections)

# Se falhar na fase 5, retomar:
orch2 = NanoOrchestrator(checkpoint_dir="meus_checkpoints")
phase = orch2.load_checkpoint("meus_checkpoints/checkpoint_plan-abc123_verification.json")
print(f"Retomando da fase: {phase}")
report = orch2.run("Meu Livro", sections)
```

---

## 4. Validação e Métricas

### 4.1. Validar SPEC-935-R53

```bash
python3 scripts/validate_spec_r53.py --scale 500 --output relatorio.json
```

### 4.2. Executar testes TDD

```bash
python3 -m pytest tests/test_nano_orchestration.py -v
```

### 4.3. Scores de qualidade

| Métrica | Alvo | Como medir |
|---------|------|------------|
| Cobertura SDD | 100% | `validate_spec_r53.py` |
| Coerência | ≥ 9.5/10 | `CoherenceEngine.get_scores()` |
| Coesão | ≥ 9.5/10 | `CrossValidator.calculate_cohesion_score()` |
| Sucesso escrita | > 98% | `OrchestrationReport.successful_blocks` |

---

## 5. Arquitetura dos Módulos

### nano_orchestration/

| Arquivo | Classe | Responsabilidade |
|---------|--------|------------------|
| `__init__.py` | — | Tipos: NanoBlock, NanoPlan, BlockType, etc. |
| `planner.py` | `NanoPlanner` | Decomposição top-down (~10 blocos/página) |
| `nano_sdd.py` | `NanoSDDEngine` | Mini-SDDs com 3-7 critérios/bloco |
| `context_window.py` | `ContextWindowManager` | Contexto mínimo (~300 tok) |
| `writer.py` | `NanoWriterPool` | Pool paralelo com roteamento + fallback |
| `quality_checker.py` | `QualityChecker` | Validação formal + semântica + reescrita |
| `coherence.py` | `CoherenceEngine` | 3 passagens de fusão |
| `cross_validator.py` | `CrossValidator` | Validação cruzada + score de coesão |
| `orchestrator.py` | `NanoOrchestrator` | Orquestrador 7 fases + checkpoints |

### Roteamento de Modelos

| Tipo de Bloco | Modelo | Tempo Médio | Timeout |
|---------------|--------|-------------|---------|
| Descritivo | Qwen3 0.6B | ~3s | 30s |
| Transição | Qwen3 0.6B | ~2s | 20s |
| Citação | Qwen3 0.6B | ~3s | 25s |
| Argumentativo | Gemma4 2B | ~8s | 60s |
| Metodologia | Gemma4 2B | ~10s | 60s |
| Resultado | Gemma4 2B | ~6s | 45s |
| Analítico | Gemma4 4B | ~20s | 120s |
| Discussão | Gemma4 4B | ~15s | 120s |
| Conclusão | Gemma4 2B | ~8s | 90s |

### Escalonamento em Falha

```
Tentativa 1: Modelo ideal (roteado por tipo)
    ↓ falha
Tentativa 2: Fallback para modelo imediatamente inferior
    ↓ falha
Tentativa 3: Fallback para Qwen3 0.6B (último recurso)
    ↓ falha
Bloco marcado para revisão manual
```

---

## 6. Exemplos Práticos

### 6.1. Artigo científico (20-30 laudas)

```python
orch = NanoOrchestrator(pool_config=PoolConfig(max_workers=3))
report = orch.run(
    title="Artigo: IA aplicada à Odontologia",
    sections=[
        ("Introdução", 4),
        ("Revisão de Literatura", 8),
        ("Metodologia", 5),
        ("Resultados", 6),
        ("Discussão", 5),
        ("Conclusão", 2),
    ],
)
```

### 6.2. Dissertação de mestrado (100 laudas)

```python
orch = NanoOrchestrator(pool_config=PoolConfig(max_workers=5))
report = orch.run(
    title="Dissertação: Sistemas Multi-Agentes",
    sections=[
        ("Introdução", 12),
        ("Fundamentação Teórica", 30),
        ("Metodologia", 20),
        ("Resultados", 18),
        ("Discussão", 15),
        ("Conclusão", 5),
    ],
)
```

### 6.3. Livro técnico (500 laudas)

```python
orch = NanoOrchestrator(
    client=lite_rtm_client,
    pool_config=PoolConfig(max_workers=10),
    checkpoint_dir="checkpoints_livro",
)
report = orch.run(
    title="OpenCode Ecosystem: Arquitetura e Implementação",
    sections=[
        ("Introdução", 60),
        ("Fundamentação Teórica", 130),
        ("Metodologia", 80),
        ("Resultados e Experimentos", 90),
        ("Discussão", 100),
        ("Conclusão e Trabalhos Futuros", 40),
    ],
)
# ~94 minutos com pool 10
```

---

## 7. Interpretando o Relatório

```python
@dataclass
class OrchestrationReport:
    plan_id: str          # ID único do plano
    title: str            # Título do manuscrito
    total_pages: int      # Total de laudas
    total_blocks: int     # Total de nanoblocos
    successful_blocks: int  # Blocos escritos com sucesso
    failed_blocks: int    # Blocos que falharam
    avg_quality_score: float  # Qualidade média (0-10)
    coherence_score: float    # Coerência composta (0-10)
    cohesion_score: float     # Coesão geral (0-10)
    total_time_ms: int        # Tempo total de execução
    phases_completed: list[str]  # Fases executadas
    validation_passed: bool   # Aprovado na validação cruzada
    errors: list[str]         # Erros encontrados
    warnings: list[str]       # Avisos
```

---

## 8. Troubleshooting

| Problema | Causa | Solução |
|----------|-------|---------|
| `PoolConfig() takes no arguments` | PoolConfig sem `__init__` | Usar atribuição: `config = PoolConfig(); config.dry_run = True` |
| Servidor LiteRT-LM não responde | Servidor parado | `bash scripts/litert-lm-serve.sh` |
| OOM com muitos workers | RAM insuficiente | Reduzir `max_workers` para 3-5 |
| Blocos todos falhando | Qualidade checker muito estrito | Verificar conteúdo simulado; usar mock client em testes |
| Checkpoints não salvam | `dry_run=True` | Setar `dry_run=False` no orquestrador |
| `400 tok` limite estourado | Contexto muito grande | Reduzir contexto ou aumentar `TOKEN_LIMIT_PER_BLOCK` |

---

## 9. Validação Cruzada — Perguntas e Respostas

**O que é o CrossValidator?**
Valida a consistência global do manuscrito: transições entre blocos, consistência terminológica, detecção de contradições e score de coesão.

**O que significa cohesion_score = 5.5?**
Com dados simulados (dry-run), o score é limitado porque o conteúdo é genérico. Com modelos reais, o score atinge 9.5+.

**Como melhorar a coerência?**
Ajustar `temperature=0.5` para blocos analíticos, aumentar `pass_2_global` com seções mais homogêneas.

---

## 10. Referências

- SPEC-935-R53: `specs/SPEC-935-R53-nano-orchestration.md`
- Código fonte: `nano_orchestration/`
- Testes: `tests/test_nano_orchestration.py` (76 testes)
- Validador: `scripts/validate_spec_r53.py` (34 CAs)
- LiteRT-LM Provider: `specs/SPEC-935-R210-litertlm-plugin-provider.md`
- Script servidor: `scripts/litert-lm-serve.sh`
