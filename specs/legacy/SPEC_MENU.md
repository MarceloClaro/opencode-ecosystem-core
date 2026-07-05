# SPEC-MENU-001: Menu Flexivel com Submenus Hierarquicos
Version: 1.0.0 | Status: verified | TDD: verified | Engine: MenuEngine

## Objective
Sistema de navegacao adaptativo para o ecossistema OpenCode com descoberta
automatica de skills, agentes, MCPs e motores de raciocinio.

## Acceptance Criteria
- [x] CT-1: MenuNode com suporte a submenus recursivos e navegacao hierarquica
- [x] CT-2: MenuEngine descobre dinamicamente 8 categorias principais
- [x] CT-3: 4 reasoning engines acessiveis via submenu dedicado
- [x] CT-4: Busca textual retorna resultados filtrados em toda a arvore
- [x] CT-5: Navegacao por caminho ("reasoning/z3") retorna no correto
- [x] CT-6: Plugins externos carregados via .menu_registry.json
- [x] CT-7: MenuRenderer gera saida formatada com/sem cores
- [x] CT-8: InteractiveMenu suporta loop de eventos (n°, b, q, /busca, h)
- [x] CT-9: 27/27 testes TDD aprovados

## Engine
menu.py -> MenuEngine, MenuNode, MenuItem, MenuRenderer, InteractiveMenu

## Architecture
```
menu.py
├── MenuItem       — Item de menu com callback/submenu
├── MenuNode       — No hierarquico recursivo
├── SessionState   — Estado da sessao (historico, breadcrumbs)
├── MenuEngine     — Descoberta automatica + navegacao + busca
├── MenuRenderer   — Renderizacao terminal (cores, formatacao)
└── InteractiveMenu — Loop de eventos (input, display, navegacao)

.menu_registry.json — Plugins externos (adicionar itens sem editar codigo)
```

## Features
- 8 categorias principais com auto-descoberta
- Submenus hierarquicos com profundidade ilimitada
- Busca textual recursiva em toda a arvore
- Navegacao por teclado (numeros, b, q, /busca, h)
- Breadcrumbs de navegacao
- Plugins externos via JSON (hot-reload sem editar menu.py)
- Estatisticas da sessao (skills, TDD, tempo)
- Compatibilidade Windows/Linux (cores com fallback)
