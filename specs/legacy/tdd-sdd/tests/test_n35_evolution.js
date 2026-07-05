const { OrchestrationEngine } = require('../../.opencode/engines/orchestration_engine');
const assert = require('assert');

// Test Suite: N3.5+ Evolutionary Architecture (Lexical Gate & MCP Synergy)
async function runEvolutionTests() {
    console.log("===============================================================");
    console.log("🔬 INICIANDO BATERIA DE TESTES TDD (Evolução N3.5+)");
    console.log("===============================================================\n");

    const engine = new OrchestrationEngine();
    engine.activateN3_5Safety();

    let passed = 0;
    let failed = 0;

    // TDD CASE 1: Lexical Complexity Gate
    try {
        console.log("[TESTE 1] Estresse Lexical - Simulando Prompt Hipercomplexo/Malicioso...");
        // Generating a prompt with high complexity ratio (long strings, few spaces)
        const evilPrompt = "A".repeat(80000) + " " + "B".repeat(80000); 
        
        const task = {
            skill: 'scientific_writing',
            priority: 'high',
            payload: { query: evilPrompt }
        };

        const result = await engine.dispatch(task);
        
        assert.strictEqual(result.status, 'error', "A task deveria ter sido bloqueada");
        assert.strictEqual(result.error, 'BLOCKED_BY_N3_5_PREVENTIVE_BARRIER', "Erro incorreto");
        console.log("✅ [PASSOU] Barreira de Complexidade Lexical interceptou a ameaça com sucesso!");
        passed++;
    } catch (e) {
        console.error("❌ [FALHOU] Teste 1: ", e.message);
        failed++;
    }

    // TDD CASE 2: MCP Synergy Pre-warm
    try {
        console.log("\n[TESTE 2] Sinergia Financeira - Simulando Chamada MCP Financeiro...");
        const task = {
            skill: 'data_analysis',
            priority: 'normal',
            payload: { domain: 'finance', mcp: 'finance_mcp' }
        };

        // Injecting spy on pool.findAgent
        let preWarmCalled = false;
        const originalFindAgent = engine.pool.findAgent.bind(engine.pool);
        engine.pool.findAgent = (skill, mode) => {
            if (skill === 'scientific_writing') preWarmCalled = true;
            return originalFindAgent(skill, mode);
        };

        const result = await engine.dispatch(task);
        assert.ok(preWarmCalled, "O agente de escrita científica não foi pré-aquecido no cache.");
        console.log("✅ [PASSOU] Cache Neural pré-aquecido automaticamente pelo MCP Finance_MCP!");
        passed++;
    } catch (e) {
        console.error("❌ [FALHOU] Teste 2: ", e.message);
        failed++;
    }

    console.log("\n===============================================================");
    console.log(`📊 RESULTADO DA AUDITORIA: ${passed} PASSOU | ${failed} FALHOU`);
    console.log("===============================================================");
}

runEvolutionTests();
