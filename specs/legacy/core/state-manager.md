# Spec: State Manager (core/state_manager.py)

**Versao:** 1.0.0
**Status:** active
**Manutencao SWEBOK:** adaptativa (frequencia: baixa)
**Ultima revisao:** 2026-05-27
**Spec baseada em:** codigo-fonte `ecosystem_backup/core/state_manager.py`

---

## 1. Comportamento Esperado

Proxy unificado que combina dois backends de armazenamento:
- **SQLiteStateManager** (primario): dados estruturados, consultas, chaves regulares
- **FileStateManager** (secundario): dados semi-estruturados, arquivos JSON, chaves com prefixo `file:`

Interface unificada: get(key), set(key, data), delete(key), keys(), exists(key).
Roteamento transparente baseado em prefixo de chave.

## 2. Usuarios e Contexto

- **Usuarios:** Todos os componentes que precisam persistir estado (agentes, plugins, evolucao, health)
- **Volume:** 100+ entidades de estado, acesso frequente (escrita a cada ciclo de evolucao)
- **Ambiente:** Python 3.11+, SQLite via sqlite3 built-in, JSON via Pathlib
- **Dependencias:** core.config.settings, core.interfaces.IStateManager, core.state.SQLiteStateManager, core.state_file.FileStateManager

## 3. Restricoes

- Chaves com prefixo `file:` sao roteadas para FileStateManager
- Demais chaves usam SQLiteStateManager
- Nao ha fallback entre backends (se um falha, o erro e propagado)
- Thread-safe para leitura, nao para escrita concorrente
- Compatibilidade reversa com `from core import state_manager`

## 4. Casos de Borda

- Chave inexistente: retorna default (None)
- Conflito de escrita: ultimo write vence (sem lock)
- DB corrompido: SQLiteStateManager levanta excecao, FileStateManager continua operacional
- Prefixo `file:` no meio da chave: nao e tratado como roteamento (so no inicio)

## 5. Criterios de Aceitacao

- [ ] set/get/delete com chave regular → SQLite backend
- [ ] set/get/delete com prefixo `file:` → File backend
- [ ] keys() retorna chaves de ambos os backends
- [ ] exists() consulta ambos os backends
- [ ] Chave inexistente retorna None (nao levanta excecao)
- [ ] Compatibilidade reversa mantida (import existente nao quebra)

## 6. Testes

- `tests/core/test_state_manager.py` (existente)
- `tests/core/test_unified_state_manager.py` (existente)
- Cenario: CRUD em ambos os backends
- Cenario: roteamento por prefixo
- Cenario: compatibilidade reversa
