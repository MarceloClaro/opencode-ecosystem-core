# Spec: Errors (core/errors.py)

**Versao:** 1.0.0 | **Status:** active | **SWEBOK:** adaptativa | **Revisao:** 2026-05-27

## 1. Comportamento
Hierarquia de excecoes do ecossistema. Todas herdam de OpenCodeError, permitindo captura uniforme. Cada excecao tem codigo unico e HTTP status code mapeado. Fornece AgentError, PluginError, NotFoundError e outras especializacoes.

## 2. Usuarios
- Usuarios: todos os modulos core e agentes
- Volume: baixo (excecoes sao raras no fluxo normal)
- Ambiente: Python 3.11+

## 3. Restricoes
- Todas as excecoes herdam de OpenCodeError
- Codigo unico por tipo de erro (ex: AGENT_001)
- HTTP status code mapeado para cada erro
- Mensagens de erro em ingles (logs internos)

## 4. Bordas
- Erro desconhecido: capturado como OpenCodeError generico
- Encadeamento: suporta `raise ... from` para preservar causa

## 5. Criterios
- [ ] OpenCodeError capturavel como base de todas as excecoes
- [ ] AgentError levantado por agent_manager em falhas
- [ ] PluginError levantado por plugin_manager em falhas
- [ ] NotFoundError levantado para recursos inexistentes
- [ ] Cada erro tem codigo unico e HTTP status
