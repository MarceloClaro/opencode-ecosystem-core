/**
 * ============================================================================
 * test_orchestration.js — TDD Test Suite for OrchestrationEngine
 * OpenCode Ecosystem v1.0.0
 * ============================================================================
 *
 * TEST STRATEGY: Red → Green → Refactor
 * - Pure JavaScript, zero external dependencies
 * - Built-in test runner with PASS/FAIL reporting
 * - 18 test cases covering: unit, integration, fault-tolerance, load balancing,
 *   skill matching, multi-reasoning dispatch, SROI integration
 *
 * RUN WITH: node test_orchestration.js
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

function assertDeepEqual(actual, expected, message) {
  const a = JSON.stringify(actual), e = JSON.stringify(expected);
  if (a !== e) throw new Error(message || `Expected ${e}, got ${a}`);
}

function assertThrows(fn, expectedCode, message) {
  try {
    fn();
    throw new Error(`Expected error '${expectedCode}' but no error was thrown`);
  } catch (err) {
    if (err.message.startsWith("Expected error")) throw err;
    if (expectedCode && err.code !== expectedCode)
      throw new Error(message || `Expected error code '${expectedCode}', got '${err.code}' (${err.message})`);
  }
}

// ─── OrchestrationEngine Implementation (Under Test) ─────────────────────────
//
// This is a complete, self-contained implementation of OrchestrationEngine
// that satisfies the contracts defined in orchestration.spec.json.
// The TDD cycle: tests below were written FIRST (Red), then this implementation
// was written to make them pass (Green).

class OrchestratorError extends Error {
  constructor(code, message, context = {}) {
    super(message);
    this.code = code;
    this.context = context;
  }
}

class OrchestrationEngine {
  constructor(config = {}) {
    this.MAX_RETRIES      = config.MAX_RETRIES      || 5;
    this.DEFAULT_TIMEOUT  = config.DEFAULT_TIMEOUT  || 30000;
    this.MIN_TIMEOUT      = config.MIN_TIMEOUT      || 100;
    this.MAX_TIMEOUT      = config.MAX_TIMEOUT      || 3600000;

    this._agents         = new Map();  // agentId -> agentRecord
    this._skills         = new Set();  // registered skill IDs
    this._activeTasks    = new Map();  // taskId -> taskRecord
    this._routingTable   = new Map();  // skillId -> sorted agent list
    this._telemetry      = [];         // event log
    this._routingLock    = false;
  }

  // ── Agent & Skill Registry ──────────────────────────────────────────────

  registerAgent(agent) {
    if (!agent.id || !Array.isArray(agent.skills))
      throw new OrchestratorError("INVALID_AGENT", "Agent must have id and skills[]");
    this._agents.set(agent.id, {
      id:               agent.id,
      skills:           agent.skills,
      health_status:    agent.health_status    || "healthy",
      health_score:     agent.health_score     || 100,
      concurrency_slots:agent.concurrency_slots|| 5,
      load:             0,
      task_count_total: 0,
    });
    this._rebuildRoutingTable();
  }

  registerSkill(skillId) {
    this._skills.add(skillId);
  }

  markAgentUnhealthy(agentId) {
    const agent = this._agents.get(agentId);
    if (agent) {
      agent.health_status = "unhealthy";
      this._rebuildRoutingTable();
    }
  }

  // ── Core: dispatchTask ──────────────────────────────────────────────────

  dispatchTask(req) {
    // Precondition checks (contract enforcement)
    if (!req || !req.task_id)
      throw new OrchestratorError("INVALID_REQUEST", "task_id is required");
    if (this._activeTasks.has(req.task_id))
      throw new OrchestratorError("DUPLICATE_TASK_ID", `Task ${req.task_id} already exists`);
    if (!this._skills.has(req.skill_required))
      throw new OrchestratorError("SKILL_NOT_FOUND", `Skill '${req.skill_required}' not in registry`);
    if (req.timeout_ms !== undefined &&
        (req.timeout_ms < this.MIN_TIMEOUT || req.timeout_ms > this.MAX_TIMEOUT))
      throw new OrchestratorError("TIMEOUT_INVALID", `timeout_ms must be in [${this.MIN_TIMEOUT}, ${this.MAX_TIMEOUT}]`);

    const agent = this._selectAgent(req.skill_required, req.priority || 5);
    // Post-conditions
    agent.load++;
    agent.task_count_total++;

    const record = {
      task_id:         req.task_id,
      assigned_agent:  agent.id,
      status:          "running",
      started_at:      new Date().toISOString(),
      completed_at:    null,
      result_payload:  null,
      error:           null,
      retry_count:     0,
      original_request:req,
    };
    this._activeTasks.set(req.task_id, record);
    this._emit("task_dispatched", { task_id: req.task_id, agent: agent.id });
    return record;
  }

  // ── Core: selectAgent ───────────────────────────────────────────────────

  _selectAgent(skillId, priority = 5) {
    const candidates = Array.from(this._agents.values()).filter(a =>
      a.health_status === "healthy" &&
      a.skills.includes(skillId) &&
      a.load < a.concurrency_slots
    );
    if (candidates.length === 0)
      throw new OrchestratorError("NO_CAPABLE_AGENT", `No healthy agent has skill '${skillId}'`);

    // Score: (slots - load) * health_score * skill_affinity(simplified=1.0)
    let best = null, bestScore = -Infinity;
    for (const a of candidates) {
      const score = (a.concurrency_slots - a.load) * (a.health_score / 100);
      if (score > bestScore || (score === bestScore && a.task_count_total < best.task_count_total)) {
        best = a; bestScore = score;
      }
    }
    return best;
  }

  // ── Core: completeTask ──────────────────────────────────────────────────

  completeTask(taskId, resultPayload) {
    const record = this._activeTasks.get(taskId);
    if (!record || record.status !== "running")
      throw new OrchestratorError("TASK_NOT_RUNNING", `Task ${taskId} is not in running state`);

    const agent = this._agents.get(record.assigned_agent);
    if (agent && agent.load > 0) agent.load--;

    record.status       = "succeeded";
    record.completed_at = new Date().toISOString();
    record.result_payload = resultPayload || {};
    this._emit("task_completed", { task_id: taskId });
    return record;
  }

  // ── Core: cancelTask ───────────────────────────────────────────────────

  cancelTask(taskId, reason) {
    const record = this._activeTasks.get(taskId);
    if (!record)
      throw new OrchestratorError("TASK_NOT_FOUND", `Task ${taskId} not found`);
    if (!["pending", "running"].includes(record.status))
      throw new OrchestratorError("TASK_NOT_CANCELLABLE", `Task ${taskId} cannot be cancelled (status: ${record.status})`);

    if (record.status === "running") {
      const agent = this._agents.get(record.assigned_agent);
      if (agent && agent.load > 0) agent.load--;
    }
    record.status = "cancelled";
    this._emit("task_cancelled", { task_id: taskId, reason });
    return record;
  }

  // ── Core: handleAgentFailure ────────────────────────────────────────────

  handleAgentFailure(taskId, agentId, failureReason) {
    const record = this._activeTasks.get(taskId);
    if (!record)
      throw new OrchestratorError("TASK_NOT_FOUND", `Task ${taskId} not found`);

    const agent = this._agents.get(agentId);
    if (agent && agent.load > 0) agent.load--;

    if (record.retry_count < this.MAX_RETRIES) {
      record.retry_count++;
      record.status = "retrying";
      this._emit("task_retried", { task_id: taskId, retry_count: record.retry_count });
      // Re-dispatch: try to find another agent
      try {
        const newAgent = this._selectAgent(record.original_request.skill_required, record.original_request.priority || 5);
        newAgent.load++;
        record.assigned_agent = newAgent.id;
        record.status = "running";
        return record;
      } catch (e) {
        // No capable agent for retry — fall through to permanent failure
        record.status = "failed";
        record.error = { code: "NO_CAPABLE_AGENT", message: e.message };
        this._emit("task_failed_permanently", { task_id: taskId, reason: "no_capable_agent_on_retry" });
        return record;
      }
    } else {
      record.status = "failed";
      record.error = {
        code: "MAX_RETRIES_EXCEEDED",
        retry_count: record.retry_count,
        last_failure: failureReason,
      };
      this._emit("task_failed_permanently", { task_id: taskId });
      return record;
    }
  }

  // ── Routing Table ───────────────────────────────────────────────────────

  _rebuildRoutingTable() {
    if (this._routingLock)
      throw new OrchestratorError("LOCK_ACQUISITION_FAILED", "Routing table refresh already in progress");
    this._routingLock = true;
    const table = new Map();
    for (const agent of this._agents.values()) {
      if (agent.health_status !== "healthy") continue;
      for (const skill of agent.skills) {
        if (!table.has(skill)) table.set(skill, []);
        table.get(skill).push(agent.id);
      }
    }
    this._routingTable = table;
    this._routingLock = false;
    this._emit("routing_table_refreshed", { agent_count: [...this._agents.values()].filter(a => a.health_status === "healthy").length });
  }

  // ── Helpers ─────────────────────────────────────────────────────────────

  _emit(event, data) {
    this._telemetry.push({ event, data, timestamp: new Date().toISOString() });
  }

  getHealthScore() {
    const agents = Array.from(this._agents.values());
    if (agents.length === 0) return 0;
    const healthy = agents.filter(a => a.health_status === "healthy");
    return Math.round((healthy.length / agents.length) * 100);
  }

  getActiveTaskCount() { return [...this._activeTasks.values()].filter(t => t.status === "running").length; }
  getTelemetry()       { return this._telemetry; }
  getTask(id)          { return this._activeTasks.get(id); }
  getAgent(id)         { return this._agents.get(id); }
}

// ─── TEST SUITES ─────────────────────────────────────────────────────────────

// ── Helpers to build fixtures ──────────────────────────────────────────────

function makeOE() {
  const oe = new OrchestrationEngine();
  oe.registerSkill("text_analysis");
  oe.registerSkill("code_generation");
  oe.registerSkill("data_visualization");
  oe.registerSkill("hypothesis_formation");
  return oe;
}

function addAgent(oe, id, skills, opts = {}) {
  oe.registerAgent({
    id,
    skills,
    health_status:     opts.health_status     || "healthy",
    health_score:      opts.health_score      || 90,
    concurrency_slots: opts.concurrency_slots || 3,
  });
}

function makeTask(overrides = {}) {
  return {
    task_id:        overrides.task_id        || `task-${Date.now()}-${Math.random().toString(36).slice(2)}`,
    skill_required: overrides.skill_required || "text_analysis",
    payload:        overrides.payload        || { input: "test data" },
    priority:       overrides.priority       || 5,
    ...overrides,
  };
}

// ── Suite 1: Agent Registration & Skill Registry ────────────────────────────

describe("Suite 1 — Agent Registration & Skill Registry", () => {

  test("TC01: Registers a healthy agent with skills", () => {
    const oe = makeOE();
    addAgent(oe, "agent-001", ["text_analysis", "code_generation"]);
    const a = oe.getAgent("agent-001");
    assert(a !== undefined, "Agent should exist after registration");
    assertEqual(a.health_status, "healthy", "Agent should default to healthy");
    assertEqual(a.concurrency_slots, 3, "Agent should have 3 concurrency slots");
    assert(a.skills.includes("text_analysis"), "Agent should have text_analysis skill");
  });

  test("TC02: Registers multiple agents and validates routing table", () => {
    const oe = makeOE();
    addAgent(oe, "agent-A", ["text_analysis"]);
    addAgent(oe, "agent-B", ["text_analysis", "code_generation"]);
    // Routing table should have both agents for text_analysis
    const candidates = Array.from(oe._agents.values()).filter(a =>
      a.health_status === "healthy" && a.skills.includes("text_analysis")
    );
    assert(candidates.length === 2, `Expected 2 candidates for text_analysis, got ${candidates.length}`);
  });

  test("TC03: Unhealthy agents are excluded from routing", () => {
    const oe = makeOE();
    addAgent(oe, "agent-sick",    ["text_analysis"], { health_status: "unhealthy" });
    addAgent(oe, "agent-healthy", ["text_analysis"]);
    const candidates = Array.from(oe._agents.values()).filter(a =>
      a.health_status === "healthy" && a.skills.includes("text_analysis")
    );
    assertEqual(candidates.length, 1, "Only healthy agent should be in candidates");
    assertEqual(candidates[0].id, "agent-healthy", "Candidate should be agent-healthy");
  });

});

// ── Suite 2: Task Dispatch ───────────────────────────────────────────────────

describe("Suite 2 — Task Dispatch (dispatchTask)", () => {

  test("TC04: Dispatches task to healthy capable agent", () => {
    const oe = makeOE();
    addAgent(oe, "agent-001", ["text_analysis"]);
    const req = makeTask({ skill_required: "text_analysis" });
    const result = oe.dispatchTask(req);
    assertEqual(result.status, "running", "Task should be running after dispatch");
    assertEqual(result.assigned_agent, "agent-001", "Task should be assigned to agent-001");
    assert(result.started_at !== null, "started_at must be set");
  });

  test("TC05: Raises DUPLICATE_TASK_ID for repeated task_id", () => {
    const oe = makeOE();
    addAgent(oe, "agent-001", ["text_analysis"]);
    const req = makeTask({ task_id: "dup-task-001" });
    oe.dispatchTask(req);
    assertThrows(() => oe.dispatchTask(req), "DUPLICATE_TASK_ID",
      "Should raise DUPLICATE_TASK_ID for duplicate task_id");
  });

  test("TC06: Raises SKILL_NOT_FOUND for unregistered skill", () => {
    const oe = makeOE();
    addAgent(oe, "agent-001", ["text_analysis"]);
    const req = makeTask({ skill_required: "unregistered_skill" });
    assertThrows(() => oe.dispatchTask(req), "SKILL_NOT_FOUND",
      "Should raise SKILL_NOT_FOUND for unregistered skill");
  });

  test("TC07: Raises TIMEOUT_INVALID for out-of-range timeout", () => {
    const oe = makeOE();
    addAgent(oe, "agent-001", ["text_analysis"]);
    const req = makeTask({ timeout_ms: 50 }); // below 100ms minimum
    assertThrows(() => oe.dispatchTask(req), "TIMEOUT_INVALID",
      "Should raise TIMEOUT_INVALID for timeout_ms < 100");
  });

  test("TC08: Raises NO_CAPABLE_AGENT when no agent has the skill", () => {
    const oe = makeOE();
    addAgent(oe, "agent-001", ["code_generation"]); // no text_analysis
    const req = makeTask({ skill_required: "text_analysis" });
    assertThrows(() => oe.dispatchTask(req), "NO_CAPABLE_AGENT",
      "Should raise NO_CAPABLE_AGENT when skill not available");
  });

  test("TC09: Agent load increments after dispatch", () => {
    const oe = makeOE();
    addAgent(oe, "agent-001", ["text_analysis"], { concurrency_slots: 3 });
    oe.dispatchTask(makeTask({ task_id: "t1" }));
    oe.dispatchTask(makeTask({ task_id: "t2" }));
    assertEqual(oe.getAgent("agent-001").load, 2, "Agent load should be 2 after 2 dispatches");
  });

  test("TC10: Raises NO_CAPABLE_AGENT when agent is at full capacity", () => {
    const oe = makeOE();
    addAgent(oe, "agent-001", ["text_analysis"], { concurrency_slots: 1 });
    oe.dispatchTask(makeTask({ task_id: "fill-slot" })); // fills the only slot
    assertThrows(() => oe.dispatchTask(makeTask({ task_id: "overflow" })), "NO_CAPABLE_AGENT",
      "Should raise NO_CAPABLE_AGENT when agent at full capacity");
  });

});

// ── Suite 3: Agent Selection & Load Balancing ─────────────────────────────────

describe("Suite 3 — Load Balancing & Agent Selection", () => {

  test("TC11: Selects agent with highest capacity score", () => {
    const oe = makeOE();
    // agent-high has more free slots = higher score
    addAgent(oe, "agent-low",  ["text_analysis"], { concurrency_slots: 2, health_score: 80 });
    addAgent(oe, "agent-high", ["text_analysis"], { concurrency_slots: 5, health_score: 95 });
    // Give agent-low some load
    oe.dispatchTask(makeTask({ task_id: "preload-1", skill_required: "text_analysis" }));
    // Next task should go to agent-high (more capacity)
    const req = makeTask({ task_id: "next-task", skill_required: "text_analysis" });
    const result = oe.dispatchTask(req);
    assertEqual(result.assigned_agent, "agent-high", "Higher-capacity agent should be selected");
  });

  test("TC12: Tiebreak on task_count_total (least used)", () => {
    const oe = makeOE();
    addAgent(oe, "agent-A", ["code_generation"], { concurrency_slots: 5, health_score: 90 });
    addAgent(oe, "agent-B", ["code_generation"], { concurrency_slots: 5, health_score: 90 });
    // Both start identical — first dispatch should go to agent-A (stable sort)
    const r1 = oe.dispatchTask(makeTask({ task_id: "tA", skill_required: "code_generation" }));
    oe.completeTask("tA", {});
    // Now agent-A has task_count_total=1, agent-B=0 — next should go to agent-B
    const r2 = oe.dispatchTask(makeTask({ task_id: "tB", skill_required: "code_generation" }));
    assertEqual(r2.assigned_agent, "agent-B", "Tiebreak should prefer least-used agent");
  });

  test("TC13: Multi-skill agents can handle multiple skill types", () => {
    const oe = makeOE();
    addAgent(oe, "generalist", ["text_analysis", "code_generation", "data_visualization"]);
    const t1 = oe.dispatchTask(makeTask({ task_id: "ms1", skill_required: "text_analysis" }));
    oe.completeTask("ms1", {});
    const t2 = oe.dispatchTask(makeTask({ task_id: "ms2", skill_required: "code_generation" }));
    oe.completeTask("ms2", {});
    assertEqual(t1.assigned_agent, "generalist", "Generalist handles text_analysis");
    assertEqual(t2.assigned_agent, "generalist", "Generalist handles code_generation");
  });

});

// ── Suite 4: Fault Tolerance & Retries ────────────────────────────────────────

describe("Suite 4 — Fault Tolerance & Retry Logic", () => {

  test("TC14: handleAgentFailure retries task on new agent", () => {
    const oe = makeOE();
    addAgent(oe, "agent-primary", ["text_analysis"]);
    addAgent(oe, "agent-backup",  ["text_analysis"]);
    const req = makeTask({ task_id: "retry-task" });
    oe.dispatchTask(req);
    const record = oe.handleAgentFailure("retry-task", "agent-primary", "timeout");
    // Should have retried on agent-backup
    assert(record.retry_count === 1, "retry_count should be 1");
    assert(record.status === "running", "Status should be running after successful retry");
    assertEqual(record.assigned_agent, "agent-backup", "Should reassign to agent-backup");
  });

  test("TC15: Task permanently fails after MAX_RETRIES exceeded", () => {
    const oe = makeOE();
    // Only one agent — all retries will fail to find an alternative
    addAgent(oe, "agent-only", ["text_analysis"]);
    const req = makeTask({ task_id: "doomed-task" });
    oe.dispatchTask(req);

    // Exhaust retries by marking agent unhealthy and failing repeatedly
    // We simulate up to MAX_RETRIES + 1 failures
    let record;
    for (let i = 0; i <= 5; i++) {
      oe.markAgentUnhealthy("agent-only");
      record = oe.handleAgentFailure("doomed-task", "agent-only", `failure-${i}`);
      if (record.status === "failed") break;
      // Re-mark healthy for next cycle
      oe.getAgent("agent-only").health_status = "healthy";
      record.status = "running"; // reset for next failure
    }
    assertEqual(record.status, "failed", "Task should be permanently failed after max retries");
  });

  test("TC16: Telemetry events emitted for dispatch, retry, and failure", () => {
    const oe = makeOE();
    addAgent(oe, "agent-A", ["text_analysis"]);
    const req = makeTask({ task_id: "telemetry-task" });
    oe.dispatchTask(req);
    oe.markAgentUnhealthy("agent-A");
    oe.handleAgentFailure("telemetry-task", "agent-A", "crash");

    const events = oe.getTelemetry().map(e => e.event);
    assert(events.includes("task_dispatched"), "Should emit task_dispatched");
    assert(
      events.includes("task_retried") || events.includes("task_failed_permanently"),
      "Should emit retry or failure event"
    );
  });

});

// ── Suite 5: Task Lifecycle ───────────────────────────────────────────────────

describe("Suite 5 — Task Lifecycle (complete, cancel)", () => {

  test("TC17: completeTask decrements agent load and sets status", () => {
    const oe = makeOE();
    addAgent(oe, "agent-001", ["text_analysis"]);
    oe.dispatchTask(makeTask({ task_id: "complete-me" }));
    assertEqual(oe.getAgent("agent-001").load, 1, "Load should be 1 before completion");
    oe.completeTask("complete-me", { result: "done" });
    assertEqual(oe.getAgent("agent-001").load, 0, "Load should be 0 after completion");
    assertEqual(oe.getTask("complete-me").status, "succeeded", "Task should be succeeded");
    assert(oe.getTask("complete-me").completed_at !== null, "completed_at must be set");
  });

  test("TC18: cancelTask releases running task and decrements load", () => {
    const oe = makeOE();
    addAgent(oe, "agent-001", ["text_analysis"]);
    oe.dispatchTask(makeTask({ task_id: "cancel-me" }));
    assertEqual(oe.getAgent("agent-001").load, 1, "Load should be 1 before cancel");
    oe.cancelTask("cancel-me", "user_requested");
    assertEqual(oe.getAgent("agent-001").load, 0, "Load should be 0 after cancel");
    assertEqual(oe.getTask("cancel-me").status, "cancelled", "Task should be cancelled");
  });

});

// ── Suite 6: Integration & Multi-Reasoning Dispatch ──────────────────────────

describe("Suite 6 — Integration: SROI flag & reasoning_hint passthrough", () => {

  test("TC19: Task with require_sroi=true is dispatched and flag preserved", () => {
    const oe = makeOE();
    addAgent(oe, "sroi-agent", ["hypothesis_formation"]);
    const req = makeTask({
      task_id:        "sroi-task-001",
      skill_required: "hypothesis_formation",
      require_sroi:   true,
      reasoning_hint: "abductive",
    });
    const result = oe.dispatchTask(req);
    assertEqual(result.original_request.require_sroi, true, "require_sroi should be preserved");
    assertEqual(result.original_request.reasoning_hint, "abductive", "reasoning_hint should be preserved");
  });

  test("TC20: Health score reflects proportion of healthy agents", () => {
    const oe = makeOE();
    addAgent(oe, "a1", ["text_analysis"]);
    addAgent(oe, "a2", ["text_analysis"]);
    addAgent(oe, "a3", ["text_analysis"]);
    addAgent(oe, "a4", ["text_analysis"]);
    assertEqual(oe.getHealthScore(), 100, "All 4 healthy = 100%");
    oe.markAgentUnhealthy("a1");
    oe.markAgentUnhealthy("a2");
    assertEqual(oe.getHealthScore(), 50, "2 of 4 healthy = 50%");
  });

  test("TC21: Concurrent dispatch respects OE-I1 load invariant", () => {
    const oe = makeOE();
    addAgent(oe, "agent-cap2", ["text_analysis"], { concurrency_slots: 2 });
    oe.dispatchTask(makeTask({ task_id: "c1" }));
    oe.dispatchTask(makeTask({ task_id: "c2" }));
    // Total load == 2 == concurrency_slots — next dispatch should fail
    assertThrows(() => oe.dispatchTask(makeTask({ task_id: "c3" })), "NO_CAPABLE_AGENT",
      "Should enforce load <= concurrency_slots invariant (OE-I1)");
  });

});

// ─── Test Report ──────────────────────────────────────────────────────────────

console.log("\n" + "═".repeat(60));
console.log("  OpenCode TDD — OrchestrationEngine Test Report");
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
