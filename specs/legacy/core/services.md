# Specs: Core Services (core/services/)

**Versao:** 1.0.0 | **Status:** active | **SWEBOK:** evolutiva | **Revisao:** 2026-05-27

---

## Service Registry (services/__init__.py)

### 1. Comportamento
Registro centralizado de servicos via Container DI. Cataloga todos os servicos do ecossistema com resolucao por nome. Singleton via get_service_registry().

### 2. Criterios
- [ ] register(nome, factory) adiciona servico
- [ ] resolve(nome) instancia servico sob demanda
- [ ] is_registered(nome) verifica existencia
- [ ] list_services() retorna todos os nomes

---

## Health Service (services/health.py)

### 1. Comportamento
Monitora saude dos componentes do ecossistema com thresholds. Verifica: agentes respondem, MCPs conectam, DB acessivel, plugins carregados. Gera health.json no diretorio .evolve/.

### 2. Criterios
- [ ] Health check de todos os componentes
- [ ] Thresholds configuraveis (ex: 80% agentes OK = healthy)
- [ ] Gera health.json com timestamp
- [ ] Detecta MCP offline vs erro de codigo

---

## Evolution Service (services/evolution.py)

### 1. Comportamento
Gerencia pipeline evolutivo PLAN→ACT→CORRECT→REFLECT→EVOLVE. Orquestra o AutoEvolve para descobrir, instalar e validar novas skills. Registra aprendizados em learnings.json.

### 2. Criterios
- [ ] Pipeline PLAN→ACT→CORRECT→REFLECT→EVOLVE completo
- [ ] Descoberta de novas skills funciona
- [ ] Instalacao atomica (rollback se falhar)
- [ ] Aprendizados registrados com confianca
