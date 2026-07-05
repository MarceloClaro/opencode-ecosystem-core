# Spec: Cache (core/cache.py)

**Versao:** 1.0.0 | **Status:** active | **SWEBOK:** adaptativa | **Revisao:** 2026-05-27

## 1. Comportamento
Camada de cache com TTL (Time-To-Live), eviccao LRU (Least Recently Used) e estatisticas. Thread-safe. Suporta TTL por entrada individual, eviccao automatica quando atinge limite de tamanho e coleta de metricas (hits, misses, hit_ratio).

## 2. Usuarios
- Usuarios: todos os componentes que precisam cache (state_manager, agent_manager, MCPs)
- Volume: N entradas com TTL e tamanho maximo configuraveis
- Ambiente: Python 3.11+, threading.Lock

## 3. Restricoes
- Tamanho maximo configuravel (default: 1000 entradas)
- TTL padrao: 300s (5 minutos)
- Eviccao LRU: remove a entrada menos recentemente usada
- Thread-safe: Lock por operacao de escrita

## 4. Bordas
- Entrada expirada: retorna None, remove do cache
- Cache cheio: eviccao LRU libera espaco
- TTL=0: entrada nunca expira
- Chave inexistente: retorna None (cache miss)

## 5. Criterios
- [ ] set/get com sucesso
- [ ] Entrada expira apos TTL
- [ ] Eviccao LRU quando cache cheio
- [ ] Estatisticas (hits/misses) corretas
- [ ] Thread-safe: escritas concorrentes sem corrupcao
