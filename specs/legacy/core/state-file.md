# Spec: State File (core/state_file.py)

**Versao:** 1.0.0 | **Status:** active | **SWEBOK:** adaptativa | **Revisao:** 2026-05-27

## 1. Comportamento
Persistencia de estado em arquivos JSON. Implementa IStateManager com uma chave = um arquivo .json. Thread-safe com escrita atomica via tempfile + replace. Usado como backend secundario pelo UnifiedStateManager.

## 2. Usuarios
- Usuarios: UnifiedStateManager, componentes que precisam persistir JSON
- Volume: ate 1000 arquivos
- Ambiente: Python 3.11+, pathlib

## 3. Restricoes
- Uma chave = um arquivo .json no diretorio base
- Escrita atomica: escreve em tempfile, depois replace
- Thread-safe: Lock por arquivo
- Chaves com prefixo `file:` sao roteadas para este backend

## 4. Bordas
- Diretorio inexistente: criado automaticamente
- Arquivo corrompido: retorna None, loga warning
- Concorrencia: Lock previne escrita simultanea no mesmo arquivo
- Chave com caracteres invalidos: sanitizada para nome de arquivo valido

## 5. Criterios
- [ ] set/get/delete com chave simples
- [ ] Escrita atomica (sem arquivo parcial em caso de crash)
- [ ] Thread-safe (escritas concorrentes nao corrompem)
- [ ] keys() retorna todas as chaves validas
- [ ] Arquivo corrompido nao quebra o sistema
