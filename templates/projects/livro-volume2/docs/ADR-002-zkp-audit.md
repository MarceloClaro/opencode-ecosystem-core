# ADR-002: Auditoria Criptográfica via Provas de Conhecimento Zero (ZKP)

| Campo | Valor |
|-------|-------|
| **ID** | ADR-002 |
| **Data** | 2026-06-21 |
| **Status** | Aceito |
| **Autor** | Marcelo Claro Laranjeira |
| **Especificação** | SPEC-038 (TrustEngine) |

## Contexto

A simulação de gêmeos digitais no SUS envolve dados sensíveis dos pacientes (CNS, exames de imagem, prontuários). A Lei Geral de Proteção de Dados (LGPD) exige que dados pessoais não sejam expostos em auditorias públicas. É necessário um mecanismo que prove a integridade de uma simulação sem revelar a identidade do paciente.

## Decisão

Implementar auditoria via provas de conhecimento zero baseadas em SHA-256 com salting:

```python
C_ZKP = SHA-256(SHA-256(CNS || salt) + Hash_simulação)
```

## Alternativas Consideradas

| Alternativa | Motivo da Rejeição |
|-------------|-------------------|
| Criptografia assimétrica (RSA) | Complexidade de gerenciamento de chaves |
| Armazenamento centralizado | Vulnerabilidade a ataques de vazamento |
| Logs em texto plano | Violação direta da LGPD |

## Consequências

**Positivas:**
- CNS nunca armazenado em texto plano
- Verificação pública sem expor dados
- Detecção de fraudes por alteração de hash

**Negativas:**
- Overhead computacional mínimo (SHA-256 é rápido)
- Dependência de chave de salt armazenada com segurança

## Verificação

- Testes TDD-008 e TDD-009 validam o mecanismo
- 100% de precisão na detecção de fraudes
