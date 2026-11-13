# Skill: rag-mitigation

## Descrição

Skill de mitigação de riscos para pipelines Retrieval-Augmented Generation (RAG), alinhado ao protocolo SDD/TDD do ecossistema OpenCode Core. Fornece estratégias operacionais para detectar e mitigar os principais riscos behaviorais em sistemas RAG, sem promover overclaim sobre "qualidade" ou "compreensão" do sistema.

## Contexto

Esta skill opera sob as seguintes especs fundamentais:
- SPEC-935-R1005: Framework de auditoria evolutiva de pipeline RAG
- SPEC-935-R112: Goal Drift Detection no Trust Engine
- SPEC-935-R886: Ciclo metacognitivo integrado
- SPEC-935-R999: Pesquisa sobre consciência em sistema agênico orchestrado (postura anti-overclaim)

## Quando Acionar

Esta skill deve ser acionada quando:
- O pipeline RAG apresentar sinais de goal drift (mudança arbitrária na estratégia de recuperação)
- As observações do MetaBus indicarem padrões de queries variáveis sem justativa
- Métricas de coerência comportamental (M4) demonstrarem baixa consistência
- Houver necessidade de mitigação de riscos identificada durante auditoria (SPEC-935-R1005)
- O sistema RAG necessitar de monitoramento comportamental contínuo

## Contrato Mínimo

### 1. input
- `query`: A query de busca original (string)
- `retrieved_chunks`: Lista de chunks recuperados (lista de dicts com 'conteudo', 'similaridade', 'metadados')
- `generated_response`: A resposta gerada (string)
- `context_meta`: Metadados de contexto do sistema (dict)
  - `system_id`: Identificador do sistema RAG
  - `timestamp`: Timestamp da execução
  - `model_name`: Nome do modelo de linguagem usado
  - `embedding_model`: Modelo de embedding utilizado

### 2. output
- `mitigation_report`: Relatório de mitigação (dict) contendo:
  - `risk_level`: Nível de risco identificado ('low', 'medium', 'high')
  - `drift_score`: Goal Drift Score calculado (float 0-1)
  - `coherence_index`: Índice de coerência comportamental (float 0-1)
  - `observations`: Lista de observações do MetaBus relevantes
  - `recommendations`: Lista de recomendações de mitigação
  - `qualifications`: Qualificações adequadas sobre o que NÃO foi detectado

### 3. bloqueadores fail-closed
- **Sem compilador Lean 4/embeddings validator**: Apenas `syntax_verified` no máximo; relatório indica "sem validação semântica concreta"
- **Ausência de MetaBus**: Relatório registrado como "isolado", sem persistência de observações para comparação across ciclos
- **Goal Drift detectado**: Risco level automatically elevado para 'high', recomendações incluem "revisar strategy de recuperação"
- **Sem qualificações automáticas**: Nenhuma afirmação de "melhoria", "compreensão" ou "qualidade profissional" é promovida

## Habilidades Relacionadas

- `rag-audit`: Auditoria evolutiva completa do pipeline RAG (SPEC-935-R1005)
- `goal-drift-detection`: Detecção de goal drift via Trust Engine (SPEC-935-R112)
- `metacognitive-loop`: Integração com o ciclo metacognitivo do Core (SPEC-935-R886)

## Comandos Disponíveis

### `mitigar_rag`

```bash
# Exemplo de uso
rag-mitigation mitigate_rag \
  --query "historico brasileiro independencia" \
  --retrieved_chunks '[{"conteudo": "...", "similaridade": 0.85, "metadados": {...}}]' \
  --generated_response "..." \
  --context_meta '{"system_id": "rag-system-01", "timestamp": "2026-11-13T03:00:00", "model_name": "claude-3", "embedding_model": "text-embedding-ada-002"}'
```

## Pósura Anti-Overclaim

Esta skill **não**:
- ✅ Declarar "melhoria de qualidade" do pipeline RAG
- ✅ Afirmar "compreensão" do sistema sobre o tema
- ✅ Promover "consciência" ou "inteligência" do sistema
- ✅ Garantir "resultados precisos" sem validação externa
- ✅ Afirmar "fontes confiáveis" sem hash e provenance verificados

Esta skill ****:
- ✅ Detectar propriedades comportamentais mensuráveis (drift, coerência, correlação)
- ✅ Fornecer recomendações qualificadas ("correlação observada", "padrão detectado", "sem evidência")
- ✅ Registrar observações no MetaBus sem promover confiança automática
- ✅ Manter todas as alegações restritas ao escopo local
- ✅ Avisar quando o sistema ultrapassa limites de detecção (risco high, necessidade de intervenção humana)

## Exemplos de Uso

### Exemplo 1: Detecção de Goal Drift

```python
from skills.rag_mitigation import mitigate_rag

result = mitigate_rag(
    query="analisar contexto historico do brasil",
    retrieved_chunks=[...],
    generated_response="...",
    context_meta={"system_id": "minha_rag", "timestamp": "...", ...}
)

# result.risk_level pode ser 'low', 'medium' ou 'high'
# result.drift_score indica grau de desvio da strategy original
# result.qualifications contém as devidas restrições
```

### Exemplo 2: Relatório de Conformidade

```python
report = mitigate_rag(...)
print(f"Risk Level: {report['risk_level']}")
print(f"Drift Score: {report['drift_score']:.2f}")
print(f"Qualifications: {report['qualifications']}")
# Saída esperada (exemplo):
# Risk Level: medium
# Drift Score: 0.45
# Qualifications: "Goal drift detectado via sobreposição lexical Jaccard; paráfrases da query podem gerar falso-positivo. Nenhuma afirmação de compreensão feita."
```

## Integração com o Ecossistema

Esta skill se integra aos seguintes componentes do Core:

1. **Trust Engine**: Goal Drift Detection via `check_drift()`
2. **MetaBus**: Persistência de observações via `orchestrator.meta_bus.register()`
3. **Orchestrator**: Percepção e execução de ciclo SDD via `orchestrator.perceive()`
4. **SPEC-935-R1005**: Framework de auditoria evolutiva de pipeline RAG
5. **SPEC-935-R886**: Ciclo metacognitivo integrado - reflections e lessons learned
6. **SPEC-935-R666**: Orquestração evidenciada da evolução do conhecimento - separação de hipótese, execução local, reprodução computacional, validação externa

## Limites e Responsabilidades

### L1: Skill behavior
Esta skill **não** demonstra "melhoria" do pipeline RAG. Apenas detecta e relata propriedades comportamentais observáveis. Todas as recomendações são qualificadas.

### L2: Overclaim prevention
O provedor desta skill (Core OpenCode) **não** controla a configuração do pipeline RAG externo, provedores de embedding/modelo de linguagem, ou resultados de inferência. A skill apenas observa e reporta comportamento.

### L3: Dados de entrada
A qualidade do relatório depende da qualidade dos dados de entrada (retrieved_chunks, generated_response). Entradas incompletas ou inválidas resultam em relatório com "dados insuficientes" e qualificações adequadas.

### L4: Contexto de execução
O contexto de execução (modelo de linguagem, modelo de embedding, dataset de documentos) afeta diretamente as métricas calculadas. O relatório sempre qualifica suas conclusões considerando esses fatores.

### L5: Responsabilidade humana
Mitigações propostas por esta skill **não** substituem decisão humana. Recomendações de "revisar strategy", "aumentar top-k", etc. exigem validação humana e conhecimento do domínio específico.

## Versionamento

- **Versão atual**: 0.1.0
- **Data**: 2026-11-13
- **Status**: experimental (operacional sob protocolo SDD/TDD)
- **Maintainer**: marceloclaro/orchestrator

## Licença

MIT License - sem restrições de uso dentro do ecossistema OpenCode Core, com atribuição apropriada.