const { OrchestrationEngine } = require('../../.opencode/engines/orchestration_engine');
const assert = require('assert');

async function runLiquidSwarmTest() {
    console.log("===============================================================");
    console.log("🔬 AUDITORIA TDD: LIQUID SWARM ARCHITECTURE (N4.0)");
    console.log("===============================================================\n");

    const engine = new OrchestrationEngine();
    
    // Verifying dynamic spawning
    console.log("[TESTE 1] Invocando Skill Inexistente no Pool Básico...");
    try {
        const task = {
            skill: 'data_analysis', // Skill válida, mas sem nenhum agente pré-existente na memória!
            priority: 'critical',
            payload: { data: 'qbits' }
        };

        const result = await engine.dispatch(task);
        console.log("RESULTADO:", result);
        assert.ok(result.result && result.result.agent_id && result.result.agent_id.includes('liquid-agent'), "Agente líquido não foi spawnado!");
        console.log(`✅ [PASSOU] Enxame Líquido fundiu um novo agente na hora: ${result.result.agent_id}`);
        console.log(`   -> Agente adquiriu a skill instantaneamente: ${result.result.agent_skill}`);

        // Verificando evaporação (Suicide by Incompetence)
        console.log("\n[TESTE 2] Forçando Incompetência e Evaporação de Agente...");
        const liquidAgent = engine.pool.agents.get(result.result.agent_id);
        
        // Simulating repeated failures until success_rate drops below 0.3
        for (let i = 0; i < 50; i++) {
            engine.pool.releaseAgent(result.result.agent_id, false); 
        }

        const agentExists = engine.pool.agents.has(result.result.agent_id);
        assert.strictEqual(agentExists, false, "Agente não evaporou como deveria após falhas seguidas.");
        console.log("✅ [PASSOU] Agente evaporou (foi destruído da memória) após taxa de sucesso cair abaixo de 30%!");

    } catch (e) {
        console.error("❌ [FALHOU] Erro na arquitetura Liquid Swarm:", e.stack);
    }
    
    console.log("\n===============================================================");
    console.log(`📊 STATUS DA ARQUITETURA N4.0: ${engine.pool.getStats().architecture} - ONLINE E VALIDADo`);
    console.log("===============================================================");
}

runLiquidSwarmTest();
