# SPEC-TOP-001: Agent Node Pipeline (ANP)
Version: 1.0.0 | Domain: agent-framework

## Objective
Framework para construir agentes LLM como pipelines de nos tipados e composaveis. Inclui MiddlewareChain (P17) com 8 hooks e 7 middlewares pre-construidos. Inspirado pelo BettaFish (QueryEngine/MediaEngine/InsightEngine) e DeerFlow 11-layer Middleware Pipeline.

## Acceptance Criteria
- [x] CT-1: PipelineState serialization round-trip (JSON)
- [x] CT-2: BaseNode/TransformNode/FormatNode execute correctly
- [x] CT-3: AgentNodePipeline runs sequential phases
- [x] CT-4: DeerFlow reducers (merge_artifact_list) deduplicate

## Assets
- scripts/pipeline.py
- scripts/pipeline_state.py
- scripts/base_node.py
- scripts/node_types.py
- scripts/middleware_chain.py
- scripts/llm_client.py
- tests/test_agent_node_pipeline.py
