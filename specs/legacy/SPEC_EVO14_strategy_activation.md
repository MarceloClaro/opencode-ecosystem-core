# SPEC_EVO14_strategy_activation — Agent Activation Prompts
## Domain: strategy | Agent: agent-activation | Version: 1.0.0

### CT1: Prompt template resolution
- **Given** agent role "Frontend Developer" and phase "Build"
- **When** `resolve_prompt` is called
- **Then** returns a non-empty prompt string containing agent name and phase
- **Given** unknown agent role "UnknownBot"
- **When** `resolve_prompt` is called
- **Then** returns fallback generic prompt

### CT2: Pipeline mode template selection
- **Given** mode "NEXUS-Full"
- **When** `get_orchestrator_prompt` is called
- **Then** returns prompt containing "7-phase pipeline"
- **Given** mode "NEXUS-Micro"
- **When** `get_orchestrator_prompt` is called
- **Then** returns prompt containing "Micro" and max 5-10 agents

### CT3: Placeholder interpolation
- **Given** template with placeholders [PROJECT NAME], [PHASE], [TASK ID]
- **When** `interpolate` is called with values dict
- **Then** all placeholders replaced with actual values
- **Given** template with unused placeholders
- **When** `interpolate` is called with partial values
- **Then** unused placeholders remain as-is

### CT4: Supported agent enumeration
- **When** `list_supported_agents` is called
- **Then** returns dict with divisions as keys and agent lists as values
- **Assert** Engineering division contains "Frontend Developer", "Backend Architect"
- **Assert** Product division contains "Sprint Prioritizer", "Trend Researcher"
