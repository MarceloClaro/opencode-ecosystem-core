# Pesquisador Universal v4.1 incorporado ao OpenCode Ecosystem Core

## Decisão arquitetural

O OpenCode Ecosystem Core permanece o kernel geral: MarceloClaroOrchestrator,
MetaBus, Blackboard, AttentionRouter, SDD/TDD, MCPs e catálogo geral de agentes.
O Pesquisador Universal v4.1 é a supercamada científica especializada.

A incorporação usa uma bridge nativa em vez de copiar o runtime inteiro para o
kernel. Isso reduz duplicação e permite atualizar/reverter a camada científica
sem reescrever os componentes centrais.

## Instalação científica descoberta

Por padrão a bridge procura:

```text
~/.local/share/pesquisador-universal/skill
```

Esse é o `PREFIX/skill` utilizado pelo instalador v4.1. Também é possível usar:

```bash
export PESQUISADOR_UNIVERSAL_HOME=/caminho/para/skill
```

## Uso

```bash
python -m marceloclaro.scientific_lab status
python -m marceloclaro.scientific_lab doctor
python -m marceloclaro.scientific_lab research harvest "quantum cellular automata" --workspace .
python -m marceloclaro.scientific_lab review --help
python -m marceloclaro.scientific_lab synthesis --help
python -m marceloclaro.scientific_lab grade --help
python -m marceloclaro.scientific_lab causal --help
```

## Compatibilidade após incorporação

A v4.1 standalone foi auditada contra `a5478054ceb8fc34eb0d254a30a3c451d6d864cd`.
O merge muda o HEAD do Core por definição. A bridge portanto preserva esse SHA
como baseline documental e valida a presença dos componentes essenciais, em vez
de exigir que o repositório permaneça congelado no commit anterior.

## Limites

- CI configurada não equivale a CI executada.
- hash, SBOM e assinatura não constituem validade científica.
- convergência entre laboratórios não constitui verdade científica.
- GRADE, inferência causal, recomendações e promoção de claims continuam sob os
  gates humanos definidos na supercamada.
