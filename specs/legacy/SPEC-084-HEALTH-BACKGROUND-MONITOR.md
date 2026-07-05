# SPEC-084: Health Background Monitor + Webhook Notifications

| Campo | Valor |
|-------|------|
| **SPEC ID** | SPEC-084 |
| **Ciclo** | R41 |
| **Status** | `active` |
| **Prioridade** | Alta |
| **Dependências** | SPEC-083 (Self-Repair), `core/services/health.py`, `plugins/health-reporter.ts` |
| **Suítes TDD** | `tests/test_r41_health_background.py` |
| **Componentes** | `core/services/health_background.py`, `nexus/health_webhook.py` |

---

## 1. Problema

O ecossistema OpenCode possui componentes de health check já implementados, porém **desconectados entre si e sem execução em background**:

| Componente | Localização | Problema |
|:-----------|:------------|:---------|
| `HealthService` | `core/services/health.py` | Apenas registro passivo; sem scheduler |
| `HealthMonitor` | `nexus/ecosystem_capabilities_server.py` | Executado sob demanda via `run_self_repair("heartbeat")` |
| `health-reporter.ts` | `plugins/health-reporter.ts` | Plugin TS com scores hardcoded (96-100), sem dados reais |
| `ecosystem-state.json` | Raiz | Atualizado manualmente, sem periodicidade |

**Consequências:**
- Degradações de saúde não são detectadas em tempo real
- Sem notificação proativa de falhas
- Histórico de saúde não é preservado para análise de tendências
- Alertas exigem ação manual do orquestrador

## 2. Solução

Implementar um **serviço de monitoramento em background** com 3 camadas:

```
┌─────────────────────────────────────────────────────────────┐
│               HealthBackgroundService (scheduler)              │
│  ┌─────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐ │
│  │ Health  │  │ Health   │  │ Webhook  │  │ Health       │ │
│  │ Checker │→│ History  │→│ Notifier │→│ State        │ │
│  │ (5 min) │  │ Logger   │  │ (HTTP)   │  │ Persister    │ │
│  └─────────┘  └──────────┘  └──────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
         │                │                │
         ▼                ▼                ▼
┌─────────────┐  ┌──────────────┐  ┌──────────────────┐
│ HealthMonitor │  │ health_     │  │ ecosystem-state   │
│ (SPEC-083)    │  │ history.json │  │ .json             │
│ Z3, SymPy, …  │  │ (CSV/JSONL) │  │ (versão 6.x)      │
└─────────────┘  └──────────────┘  └──────────────────┘
```

### 2.1 Camada 1 — Health Checker (Scheduler)

- Executa `HealthMonitor.heartbeat()` a cada **5 minutos** (configurável)
- Aciona `SelfRepairOrchestrator.run_pipeline()` se health_pct < 90%
- Thread em background com `threading.Timer` (sem dependência externa)
- Suporta `start()`, `stop()`, `status()`

### 2.2 Camada 2 — Health History Logger

- Registro time-series: `{timestamp, health_pct, avg_response_ms, unhealthy_count, engines[]}`
- Armazenamento em `health_history.jsonl` (JSON Lines, append-only)
- Retenção configurável: keep last N entries (default: 1000)
- Consulta: `get_history(hours=24)`, `get_trend(direction="improving|degrading|stable")`

### 2.3 Camada 3 — Webhook Notifier

- Envia HTTP POST para URLs configuradas quando:
  - **Warning**: health_pct < 90% pela 1ª vez
  - **Alert**: health_pct < 80%
  - **Critical**: health_pct < 70%
  - **Recovery**: health_pct >= 90% após alerta
- Payload JSON: `{event, timestamp, health_pct, unhealthy_engines[], previous_pct, trend}`
- Timeout: 5s por webhook
- Retry: 1 tentativa após 2s se falhar
- Não bloqueia o scheduler em caso de falha de webhook

### 2.4 Camada 4 — Health State Persister

- Atualiza `ecosystem-state.json` seção `health_monitor`:
  ```json
  {
    "health_monitor": {
      "enabled": true,
      "interval_minutes": 5,
      "last_check": "2026-07-04T03:00:00Z",
      "health_pct": 100.0,
      "unhealthy_engines": [],
      "trend": "stable",
      "webhooks": ["https://hooks.example.com/health"],
      "total_checks": 42,
      "alerts_sent": 1
    }
  }
  ```

## 3. Arquitetura de Classes

```python
# core/services/health_background.py

@dataclass
class HealthSnapshot:
    """Snapshot de saúde em um instante."""
    timestamp: str
    health_pct: float
    avg_response_ms: float
    unhealthy_count: int
    unhealthy_engines: list[str]
    engine_details: list[dict]

@dataclass
class WebhookConfig:
    url: str
    events: list[str]  # warning, alert, critical, recovery
    timeout_s: float = 5.0
    retry_count: int = 1
    enabled: bool = True

class HealthHistoryLogger:
    """Registra historico time-series de saude."""
    
    HISTORY_PATH = BASE / "health_history.jsonl"
    MAX_ENTRIES = 1000
    
    def append(self, snapshot: HealthSnapshot) -> None
    def get_history(self, hours: int = 24) -> list[HealthSnapshot]
    def get_trend(self) -> str  # "improving" | "degrading" | "stable"
    def get_summary(self) -> dict
    def trim(self, max_entries: int = 1000) -> int

class WebhookNotifier:
    """Notifica webhooks configurados sobre eventos de saude."""
    
    def __init__(self, configs: list[WebhookConfig])
    def send_event(self, event: str, snapshot: HealthSnapshot, previous: HealthSnapshot | None) -> int  # returns count sent
    def _build_payload(self, event, snapshot, previous) -> dict
    def _post(self, config: WebhookConfig, payload: dict) -> bool
    def health(self) -> dict  # stats about webhook delivery

class HealthBackgroundService:
    """Servico background que orquestra health checks periodicos."""
    
    def __init__(self, interval_minutes: int = 5, webhook_configs: list[WebhookConfig] | None = None)
    def start(self) -> None  # inicia thread background
    def stop(self) -> None   # para thread background
    def status(self) -> dict  # running/stopped, last_check, etc.
    def check_now(self) -> HealthSnapshot  # executa check imediato
    def _run_cycle(self) -> None  # loop interno
    def _evaluate_alert(self, current: HealthSnapshot, previous: HealthSnapshot | None) -> str | None
```

## 4. Fluxo de Execução

```
t=0     start() → scheduler iniciado
t=5min  _run_cycle():
          1. HealthMonitor.heartbeat() → snapshot
          2. HealthHistoryLogger.append(snapshot)
          3. _evaluate_alert(current, previous):
             - Se health < 70% → event="critical"
             - Se health < 80% → event="alert"
             - Se health < 90% → event="warning"
             - Se health >= 90% e previous < 90% → event="recovery"
          4. Se evento → WebhookNotifier.send_event(event, ...)
          5. HealthStatePersister.update(snapshot)
          6. Se health_pct < 90% → aciona SelfRepairOrchestrator
t=10min _run_cycle() novamente
...     (loop até stop())
```

## 5. CTs (20 Testes)

### 5.1 HealthSnapshot (2 CTs)

| CT | Nome | Descrição |
|:--:|:-----|:----------|
| CT-01 | `test_snapshot_creation` | HealthSnapshot cria com todos os campos |
| CT-02 | `test_snapshot_defaults` | Valores default funcionam corretamente |

### 5.2 HealthHistoryLogger (5 CTs)

| CT | Nome | Descrição |
|:--:|:-----|:----------|
| CT-03 | `test_history_append` | append() adiciona entrada ao JSONL |
| CT-04 | `test_history_get_history` | get_history() retorna entradas recentes |
| CT-05 | `test_history_get_trend_improving` | health_pct crescente → "improving" |
| CT-06 | `test_history_get_trend_degrading` | health_pct decrescente → "degrading" |
| CT-07 | `test_history_trim` | trim() remove entradas excedentes |

### 5.3 WebhookNotifier (4 CTs)

| CT | Nome | Descrição |
|:--:|:-----|:----------|
| CT-08 | `test_webhook_send_event_no_config` | Sem config → 0 enviados (sem erro) |
| CT-09 | `test_webhook_send_event` | Com config → tenta enviar (não falha) |
| CT-10 | `test_webhook_build_payload` | Payload contém campos obrigatórios |
| CT-11 | `test_webhook_health` | health() retorna estatísticas |

### 5.4 HealthBackgroundService (7 CTs)

| CT | Nome | Descrição |
|:--:|:-----|:----------|
| CT-12 | `test_service_init_default` | Inicializa com interval=5, sem webhooks |
| CT-13 | `test_service_init_custom` | Inicializa com parâmetros customizados |
| CT-14 | `test_service_start_stop` | start() → running, stop() → stopped |
| CT-15 | `test_service_check_now` | check_now() retorna HealthSnapshot |
| CT-16 | `test_service_status` | status() contém campos esperados |
| CT-17 | `test_service_evaluate_alert_normal` | health=100 → None (sem alerta) |
| CT-18 | `test_service_evaluate_alert_warning` | health=85 → "warning" |

### 5.5 Integração (2 CTs)

| CT | Nome | Descrição |
|:--:|:-----|:----------|
| CT-19 | `test_integration_heartbeat_to_history` | health_check → history → consulta |
| CT-20 | `test_integration_alert_webhook` | health baixo → webhook disparado |

## 6. Critérios de Aceitação

1. Todos os 20 CTs passam (`pytest tests/test_r41_health_background.py -v`)
2. `HealthBackgroundService.start()` executa em background sem bloquear
3. `HealthHistoryLogger` persiste e recupera histórico corretamente
4. `WebhookNotifier` tenta enviar sem lançar exceções em caso de falha
5. Alertas seguem a hierarquia: normal → warning → alert → critical → recovery
6. Nenhuma dependência externa (threading nativo do Python)
7. `ecosystem-state.json` é atualizado com seção `health_monitor`

## 7. Referenciais Teóricos

| Ref | Fonte | Contribuição |
|:----|:------|:-------------|
| IEEE — Standard for System Health Management (STD 1856-2017) | IEEE | Framework para monitoramento de saúde em sistemas |
| AWS — Well-Architected Framework (Reliability Pillar) | AWS 2024 | Práticas de monitoramento e alarmes |
| Google SRE — Monitoring Distributed Systems | Beyer et al., O'Reilly 2016 | Four golden signals: latency, traffic, errors, saturation |
| OpenTelemetry — Cloud Native Computing Foundation | CNCF 2024 | Padrão para coleta de telemetria |

---

*Fim da SPEC-084*
