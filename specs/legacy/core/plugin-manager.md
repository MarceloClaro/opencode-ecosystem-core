# Spec: Plugin Manager (core/plugin_manager.py)

**Versao:** 1.0.0
**Status:** active
**Manutencao SWEBOK:** evolutiva (frequencia: media)
**Ultima revisao:** 2026-05-27
**Spec baseada em:** codigo-fonte `ecosystem_backup/core/plugin_manager.py`

---

## 1. Comportamento Esperado

Gerencia o ciclo de vida de plugins no ecossistema:
- Descoberta automatica de plugins em diretorios configurados
- Carregamento (load) com configuracao
- Execucao de hooks (execute_hook)
- Descarregamento limpo (unload)
- Suporte a plugins Python (.py) e TypeScript (.ts)
- Integracao com DI Container

## 2. Usuarios e Contexto

- **Usuarios:** Agentes, Skills, sistema de evolucao
- **Volume:** 23 plugins registrados, carregamento sob demanda
- **Ambiente:** Python 3.11+, importlib para descoberta
- **Dependencias:** core.errors (PluginError, NotFoundError), Container (DI)

## 3. Restricoes

- Plugins devem implementar Protocol `Plugin` (name, on_load, on_unload, execute_hook)
- Plugins Python sao descobertos via importlib (nao execucao arbitraria)
- Plugins TypeScript sao gerenciados via subprocesso
- Cada plugin tem nome unico
- Hooks sao strings arbitrarias (o plugin decide quais suporta)

## 4. Casos de Borda

- Plugin nao encontrado: NotFoundError
- Plugin falha ao carregar: PluginError, nao carregado, log de falha
- Hook nao suportado: retorna None (nao levanta excecao)
- Plugin com dependencia circular: detectar e rejeitar no carregamento
- Diretorio de plugins vazio: descobrir retorna lista vazia (nao erro)
- Conflito de nomes: ultimo registrado vence (warning no log)

## 5. Criterios de Aceitacao

- [ ] Descobrir plugins em diretorio e retornar metadados
- [ ] Carregar plugin Python com sucesso
- [ ] Executar hook e receber resultado
- [ ] Descarregar plugin e liberar recursos
- [ ] Plugin que falha no carregamento nao quebra o manager
- [ ] Hook nao suportado retorna None sem erro
- [ ] Modo legado (sem DI) funciona

## 6. Testes

- `tests/core/test_plugin_manager.py` (a verificar existencia)
- `plugins/lib/plugin.test.ts` (existente - testes TS)
- Cenario: discover → load → execute_hook → unload
- Cenario: plugin inexistente → NotFoundError
- Cenario: falha de carregamento → PluginError
