/**
 * ============================================================================
 * test_opentwins_adapter.js — TDD Test Suite for OpenTwins Integration Adapter
 * OpenCode Ecosystem v1.1.0 (OpenTwins Module)
 * ============================================================================
 *
 * TEST STRATEGY: Red → Green → Refactor
 * - Validates:
 *   1. Compositional twin registration & active tracking
 *   2. Edge-to-Cloud synchronization with 500ms latency enforcement (OTW-I1)
 *   3. Compositional schema checking (OTW-I2)
 *   4. Role mapping and execution delegation to OpenTwins-compatible agents
 * - Pure JavaScript, zero external dependencies
 * - Built-in test runner with PASS/FAIL reporting
 * - 12 test cases verifying the adapter specifications
 *
 * RUN WITH: node test_opentwins_adapter.js
 * ============================================================================
 */

"use strict";

// ─── Tiny Built-in Test Runner ───────────────────────────────────────────────

const TEST_RESULTS = { passed: 0, failed: 0, errors: [] };

function test(name, fn) {
  try {
    fn();
    TEST_RESULTS.passed++;
    console.log(`  ✓ PASS  ${name}`);
  } catch (err) {
    TEST_RESULTS.failed++;
    TEST_RESULTS.errors.push({ name, message: err.message });
    console.log(`  ✗ FAIL  ${name}`);
    console.log(`          ${err.message}`);
  }
}

function describe(suiteName, fn) {
  console.log(`\n┌─ ${suiteName}`);
  fn();
  console.log(`└${"─".repeat(suiteName.length + 2)}`);
}

function assert(condition, message) {
  if (!condition) throw new Error(message || "Assertion failed");
}

function assertEqual(actual, expected, message) {
  if (actual !== expected)
    throw new Error(message || `Expected ${JSON.stringify(expected)}, got ${JSON.stringify(actual)}`);
}

function assertThrows(fn, expectedCode, message) {
  try {
    fn();
    throw new Error(`Expected error '${expectedCode}' but no error was thrown`);
  } catch (err) {
    if (err.message.startsWith("Expected error")) throw err;
    if (expectedCode && !err.message.includes(expectedCode))
      throw new Error(message || `Expected error containing '${expectedCode}', got '${err.message}'`);
  }
}

// ─── OpenTwinsAdapter Implementation (Under Test) ─────────────────────────────

class OpenTwinsAdapter {
  constructor(centralSkillRegistry = ["intraoral_scan", "lpd_solver", "samd_audit"]) {
    this.active_twins = new Map();
    this.edge_state = new Map();
    this.cloud_state = new Map();
    this.last_sync_timestamp = new Map();
    this.registered_agents = new Map();
    this.central_skill_registry = new Set(centralSkillRegistry);
    this.telemetryEvents = [];
  }

  registerTwin(twinId, components) {
    if (!twinId || typeof twinId !== "string") {
      throw new Error("INVALID_TWIN_ID");
    }
    if (this.active_twins.has(twinId)) {
      throw new Error("DUPLICATE_TWIN");
    }
    if (!components || !Array.isArray(components) || components.length === 0) {
      throw new Error("INVALID_COMPONENTS");
    }

    const twinRecord = {
      twin_id: twinId,
      components: [...components],
      registered_at: new Date().toISOString()
    };

    this.active_twins.set(twinId, twinRecord);
    this.edge_state.set(twinId, {});
    this.cloud_state.set(twinId, {});
    this.last_sync_timestamp.set(twinId, new Date().toISOString());

    return twinRecord;
  }

  // OTW-I2 Check: validation of OpenTwins compositional structure
  validateCompositionalSchema(stateData) {
    if (!stateData || typeof stateData !== "object") return false;
    // An OpenTwins state payload must contain 'version', 'twin_type', and a 'components_state' map
    if (!stateData.version || !stateData.twin_type || !stateData.components_state) {
      return false;
    }
    return typeof stateData.components_state === "object";
  }

  syncTwinState(twinId, stateData, simulatedLatencyMs = 0) {
    if (!this.active_twins.has(twinId)) {
      throw new Error("TWIN_NOT_FOUND");
    }

    // Invariant OTW-I2 Check
    if (!this.validateCompositionalSchema(stateData)) {
      throw new Error("INVALID_COMPOSITION_SCHEMA");
    }

    // Invariant OTW-I1 Check (latency limit 500ms)
    if (simulatedLatencyMs > 500) {
      throw new Error("SYNC_TIMEOUT");
    }

    // Update edge state
    this.edge_state.set(twinId, { ...stateData.components_state });

    // Sync to cloud
    this.cloud_state.set(twinId, { ...stateData.components_state });
    this.last_sync_timestamp.set(twinId, new Date().toISOString());

    return { status: "SYNCHRONIZED", latency_ms: simulatedLatencyMs };
  }

  registerAgent(agentId, role, skillId) {
    // Invariant OTW-I3 Check
    if (!this.central_skill_registry.has(skillId)) {
      throw new Error("SKILL_NOT_IN_REGISTRY");
    }

    this.registered_agents.set(agentId, { role, skillId });
  }

  dispatchToTwinsAgent(twinId, task, role) {
    if (!this.active_twins.has(twinId)) {
      throw new Error("TWIN_NOT_FOUND");
    }

    // Find agent mapping the role
    let mappedAgent = null;
    for (const [agentId, info] of this.registered_agents.entries()) {
      if (info.role === role) {
        mappedAgent = { agent_id: agentId, ...info };
        break;
      }
    }

    if (!mappedAgent) {
      throw new Error("UNMAPPED_AGENT_ROLE");
    }

    // Simulate agent task execution
    const executionResult = {
      status: "EXECUTED",
      agent_id: mappedAgent.agent_id,
      role: mappedAgent.role,
      skill_used: mappedAgent.skillId,
      timestamp: new Date().toISOString()
    };

    this.telemetryEvents.push({
      event: "agent_dispatched_via_opentwins",
      twin_id: twinId,
      agent_id: mappedAgent.agent_id,
      task_payload: task
    });

    return executionResult;
  }
}

// ─── Tests ───────────────────────────────────────────────────────────────────

const adapter = new OpenTwinsAdapter();

describe("Suite 1 — OpenTwins Twin Registration & Invariants", () => {

  test("TC01: Verify active_twins registry initialization", () => {
    assertEqual(adapter.active_twins.size, 0);
    assertEqual(adapter.edge_state.size, 0);
  });

  test("TC02: Successfully register a compositional digital twin", () => {
    const twin = adapter.registerTwin("twin-dentistry-01", ["lpd_fem_solver", "intraoral_mesh"]);
    assertEqual(twin.twin_id, "twin-dentistry-01");
    assertEqual(twin.components.length, 2);
    assertEqual(adapter.active_twins.size, 1);
  });

  test("TC03: Reject registration with duplicate twin ID", () => {
    assertThrows(() => {
      adapter.registerTwin("twin-dentistry-01", ["another_comp"]);
    }, "DUPLICATE_TWIN");
  });

  test("TC04: Reject registration with empty components array", () => {
    assertThrows(() => {
      adapter.registerTwin("twin-dentistry-02", []);
    }, "INVALID_COMPONENTS");
  });

});

describe("Suite 2 — State Synchronization & Latency Invariants", () => {

  test("TC05: Validate correct state payload format matching OpenTwins schema (OTW-I2)", () => {
    const validPayload = {
      version: "1.0",
      twin_type: "dentistry_patient",
      components_state: {
        lpd_fem_solver: { strain_xx: 0.05 },
        intraoral_mesh: { vertex_count: 50000 }
      }
    };
    assert(adapter.validateCompositionalSchema(validPayload));
    
    const invalidPayload = {
      components_state: { foo: "bar" } // missing version and twin_type
    };
    assert(!adapter.validateCompositionalSchema(invalidPayload));
  });

  test("TC06: Synchronize state successfully when latency is within 500ms budget (OTW-I1)", () => {
    const payload = {
      version: "1.0",
      twin_type: "dentistry_patient",
      components_state: { lpd_fem_solver: { displacement_x: 0.02 } }
    };
    const res = adapter.syncTwinState("twin-dentistry-01", payload, 80); // 80ms latency
    assertEqual(res.status, "SYNCHRONIZED");
    assertEqual(adapter.edge_state.get("twin-dentistry-01").lpd_fem_solver.displacement_x, 0.02);
    assertEqual(adapter.cloud_state.get("twin-dentistry-01").lpd_fem_solver.displacement_x, 0.02);
  });

  test("TC07: Block state synchronization and raise SYNC_TIMEOUT when latency exceeds 500ms budget", () => {
    const payload = {
      version: "1.0",
      twin_type: "dentistry_patient",
      components_state: { lpd_fem_solver: { displacement_x: 0.02 } }
    };
    assertThrows(() => {
      adapter.syncTwinState("twin-dentistry-01", payload, 520); // 520ms latency (> 500ms limit)
    }, "SYNC_TIMEOUT");
  });

  test("TC08: Raise TWIN_NOT_FOUND when synchronizing state for unregistered twin", () => {
    const payload = {
      version: "1.0",
      twin_type: "dentistry_patient",
      components_state: {}
    };
    assertThrows(() => {
      adapter.syncTwinState("twin-unknown", payload, 10);
    }, "TWIN_NOT_FOUND");
  });

});

describe("Suite 3 — Agent Role Mapping & Skill Registry Integration", () => {

  test("TC09: Allow registering agent if skill exists in central registry", () => {
    adapter.registerAgent("agent-fem-01", "simulation", "lpd_solver");
    assertEqual(adapter.registered_agents.size, 1);
  });

  test("TC10: Reject registering agent if skill is not in central skill registry (OTW-I3)", () => {
    assertThrows(() => {
      adapter.registerAgent("agent-bad", "monitoring", "unregistered_skill_x");
    }, "SKILL_NOT_IN_REGISTRY");
  });

  test("TC11: Dispatch task successfully to a registered agent mapping the role", () => {
    const result = adapter.dispatchToTwinsAgent("twin-dentistry-01", { force_mpa: 2.0 }, "simulation");
    assertEqual(result.status, "EXECUTED");
    assertEqual(result.agent_id, "agent-fem-01");
    assertEqual(adapter.telemetryEvents.length, 1);
  });

  test("TC12: Raise UNMAPPED_AGENT_ROLE when dispatching a task with no agent mapped to role", () => {
    assertThrows(() => {
      adapter.dispatchToTwinsAgent("twin-dentistry-01", { alert: "low_res" }, "monitoring");
    }, "UNMAPPED_AGENT_ROLE");
  });

});

// ─── Test Report ──────────────────────────────────────────────────────────────

console.log("\n" + "═".repeat(60));
console.log("  OpenCode TDD — OpenTwins Integration Adapter Test Report");
console.log("═".repeat(60));
console.log(`  Total Tests : ${TEST_RESULTS.passed + TEST_RESULTS.failed}`);
console.log(`  Passed      : ${TEST_RESULTS.passed}`);
console.log(`  Failed      : ${TEST_RESULTS.failed}`);
if (TEST_RESULTS.errors.length > 0) {
  console.log("\n  Failed Tests:");
  TEST_RESULTS.errors.forEach(e => console.log(`    - [${e.name}]: ${e.message}`));
}
const allPass = TEST_RESULTS.failed === 0;
console.log(`\n  Status: ${allPass ? "✓ ALL TESTS PASSED" : "✗ SOME TESTS FAILED"}`);
console.log("═".repeat(60));
process.exitCode = allPass ? 0 : 1;
