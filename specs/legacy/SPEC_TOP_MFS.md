# SPEC-TOP-MFS: MiroFish Local Server
Version: 1.0.0 | Domain: top-level | Status: active

## Objective
Servidor local MiroFish com backend API HTTP/SSE, simulacao de agentes, chat interativo, injecao de eventos, predicoes Omen (500+ variaveis), e frontend HTML completo. Zero dependencias externas.

## Architecture
```
Browser (HTML/CSS/JS) ←→ HTTP/SSE ←→ Python Server ←→ SimulationEngine ←→ SQLite
                                              ↓
                                    WhatsApp Profiler + Omen Predictions
```

## Core Components
| Component | Class/Function | Description |
|-----------|---------------|-------------|
| Global State | AppState | engine, sse_clients, chat_history, stats, wa_profiles |
| SSE Broadcast | broadcast_sse() | Real-time event streaming to clients |
| Chat | chat_with_agent() | Contextual responses based on agent stance |
| Simulation | run_simulation_async() | Threaded simulation with callbacks |
| Cleanup | cleanup_databases() | WAL checkpoint + vacuum on shutdown |
| Omen | save_omen_prediction() | SQLite logging with traceability metadata |

## Acceptance Criteria
- [x] CT-1: AppState initialization (engine=None, simulation_running=False, sse_clients=[])
- [x] CT-2: HTML_FRONTEND > 5000 chars, valid HTML with MiroFish branding
- [x] CT-3: BRAZIL_TIME callable and returns datetime
- [x] CT-4: chat_with_agent returns error dict when no engine (graceful degradation)
- [x] CT-5: get_agent_list returns empty list when no engine
- [x] CT-6: broadcast_sse sends to registered SSE clients
- [x] CT-7: cleanup_databases and save_omen_prediction callable
- [x] CT-8: Logger configured with TimedRotatingFileHandler

## Endpoints
| Method | Path | Description |
|--------|------|-------------|
| GET | / | HTML Frontend |
| GET | /api/agents | Agent list |
| POST | /api/simulation/start | Start simulation |
| POST | /api/simulation/stop | Stop simulation |
| POST | /api/chat | Chat with agent |
| POST | /api/events/inject | Inject event |
| POST | /api/omen/predict | Run Omen prediction |
| GET | /api/sse | SSE event stream |

## Test Coverage
- Location: `skills/mirofish-server/tests/test_mirofish_server.py`
- Classes: 4 (AppState, Constants, Functions, Available)
- Tests: 12+
