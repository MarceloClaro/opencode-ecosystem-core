# SPEC-043: Potentiality Scanner — Camada de Potenciais Latentes

## 1. Visão Geral
O `PotentialityScanner` é uma nova camada analítica projetada para mover o OpenCode Ecosystem de um sistema puramente focado em identificar gaps (descritivo/prescritivo) para um sistema focado em descobrir **capacidades emergentes** ("O que está prestes a nascer?"). 

Este documento descreve o **Módulo 1: Structural DNA Extractor**, cuja responsabilidade é extrair o mapa de capacidades do ecossistema a partir de sua estrutura atual de componentes e habilidades, identificando redundâncias, núcleos centrais e lacunas (ausências).

## 2. Metas e Objetivos
* **Extração Baseada em Capacidades:** Mapear o DNA do ecossistema com base em suas capacidades declaradas e inferidas (não sobre código-fonte bruto).
* **Identificação de Núcleo (Core):** Detectar quais capacidades representam o núcleo de processamento do sistema.
* **Detecção de Redundâncias:** Sinalizar áreas onde múltiplos componentes implementam a mesma capacidade, sugerindo potencial de convergência.
* **Mapeamento de Ausências:** Listar capacidades necessárias para a evolução do sistema que ainda não possuem representação concreta.

## 3. Arquitetura do Módulo 1 (Structural DNA Extractor)
* **Classe Principal:** `PotentialityScanner` em `skills/system/academic-audit/potentiality_scanner.py`
* **Fontes de Dados:**
  1. `skills_registry.json`: Registro dinâmico de todas as skills ativas.
  2. Mapeamento Estático de Componentes Core (scanners, engines e pontes).
* **Regras de Inferência (Heurísticas):**
  - Associação de palavras-chave da descrição e nomes de arquivos SKILL.md a capacidades atômicas (ex: "quantum" -> `quantum_computing`, "legal" -> `legal_processing`, "test" -> `tdd_validation`).
* **Saídas:**
  - `capability_map`: Mapa chave-valor associando componentes a capacidades.
  - `core_capabilities`: Capacidades dominantes e essenciais.
  - `redundant_capabilities`: Capacidades duplicadas ou sobrepostas em múltiplos componentes.
  - `missing_capabilities`: Capacidades necessárias ainda não implementadas.

## 4. Casos de Teste (TDD - `specs/test_potentiality_scanner.py`)
* **CT-4301 (Extração de DNA):** Garante que o scanner processe o registro de componentes e extraia as capacidades esperadas de forma consistente.
* **CT-4302 (Detecção de Core):** Valida se o algoritmo identifica corretamente as capacidades centrais do ecossistema (ex: `gap_detection`, `self_evolution`).
* **CT-4303 (Análise de Redundâncias):** Testa se capacidades que aparecem em múltiplos componentes são corretamente categorizadas como redundantes.
* **CT-4304 (Identificação de Ausências):** Verifica se o módulo lista as capacidades latentes ou ausentes com base em dependências não resolvidas ou metas futuras.
