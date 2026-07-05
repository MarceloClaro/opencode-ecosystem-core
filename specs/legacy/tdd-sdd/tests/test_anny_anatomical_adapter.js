/**
 * ============================================================================
 * test_anny_anatomical_adapter.js — TDD Test Suite for Anny Body Model Adapter
 * OpenCode Ecosystem v1.1.0 (Anny Module)
 * ============================================================================
 *
 * TEST STRATEGY: Red → Green → Refactor
 * - Validates:
 *   1. Phenotype shape parameterization bounds (ANY-I1)
 *   2. Temporomandibular joint range of motion limits (ANY-I2)
 *   3. Normalized UV texture coordinates (ANY-I3)
 *   4. Differentiable optimization flow (PyTorch mock)
 * - Pure JavaScript, zero external dependencies
 * - Built-in test runner with PASS/FAIL reporting
 * - 12 test cases verifying the adapter specifications
 *
 * RUN WITH: node test_anny_anatomical_adapter.js
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

// ─── AnnyAnatomicalAdapter Implementation (Under Test) ─────────────────────────

class AnnyAnatomicalAdapter {
  constructor() {
    this.patient_shape = { age: 30, height_cm: 170, weight_kg: 70, gender: "male" };
    this.joints_pose = new Map([
      ["head", { pitch: 0, yaw: 0, roll: 0 }],
      ["temporomandibular_joint", { flexion: 0, lateral: 0 }]
    ]);
    this.uv_coordinates = [];
    this.anatomical_mesh_hash = "0xinitialhash00";
  }

  parameterizePatientShape(profile) {
    // Invariant ANY-I1 checks
    if (!profile || typeof profile !== "object") {
      throw new Error("INVALID_PROFILE");
    }
    if (profile.age < 0.0 || profile.age > 120.0) {
      throw new Error("INVALID_DEMOGRAPHICS");
    }
    if (profile.height_cm < 30.0 || profile.height_cm > 250.0) {
      throw new Error("INVALID_DEMOGRAPHICS");
    }
    if (profile.weight_kg < 2.0 || profile.weight_kg > 250.0) {
      throw new Error("INVALID_DEMOGRAPHICS");
    }

    this.patient_shape = { ...profile };
    // Recompute mock mesh geometry hash
    this.anatomical_mesh_hash = this._sha256(JSON.stringify(this.patient_shape));
    return {
      status: "PARAMETERIZED",
      mesh_hash: this.anatomical_mesh_hash
    };
  }

  animateAnatomicalPose(jointId, rotation) {
    if (!this.joints_pose.has(jointId)) {
      throw new Error("JOINT_NOT_FOUND");
    }

    // Invariant ANY-I2 check (Temporomandibular joint range limit 45 degrees)
    if (jointId === "temporomandibular_joint") {
      if (rotation.flexion < 0.0 || rotation.flexion > 45.0) {
        throw new Error("ROM_LIMIT_EXCEEDED");
      }
    }

    this.joints_pose.set(jointId, { ...rotation });
    return {
      status: "ANIMATED",
      joint: jointId,
      pose: { ...rotation }
    };
  }

  mapIntraoralTexture(meshVertices, uvs) {
    if (!meshVertices || !uvs || uvs.length === 0) {
      throw new Error("EMPTY_MAPPING_DATA");
    }

    // Invariant ANY-I3 checks (normalized UV coords)
    for (let i = 0; i < uvs.length; i++) {
      const uv = uvs[i];
      if (uv.u < 0.0 || uv.u > 1.0 || uv.v < 0.0 || uv.v > 1.0) {
        throw new Error("OUT_OF_BOUNDS_UV");
      }
    }

    this.uv_coordinates = [...uvs];
    return {
      status: "TEXTURE_MAPPED",
      coordinates_count: uvs.length
    };
  }

  // Simulated PyTorch differentiable gradient descend to align TMJ rotation
  optimizeJawOpening(targetToothDistanceMm) {
    let jawAngle = this.joints_pose.get("temporomandibular_joint").flexion;
    const learningRate = 0.78125;

    // Run 5 iteration steps simulating PyTorch forward-backward gradient steps
    for (let i = 0; i < 5; i++) {
      const simulatedDistance = jawAngle * 0.8; // simple distance function
      const loss = (simulatedDistance - targetToothDistanceMm) ** 2;
      const gradient = 2 * (simulatedDistance - targetToothDistanceMm) * 0.8;
      
      // Update parameters using gradient
      jawAngle -= learningRate * gradient;
      
      // Clip parameter to ROM constraints (ANY-I2)
      if (jawAngle > 45.0) jawAngle = 45.0;
      if (jawAngle < 0.0) jawAngle = 0.0;
    }

    this.joints_pose.set("temporomandibular_joint", { flexion: jawAngle, lateral: 0 });
    return {
      optimized_flexion: parseFloat(jawAngle.toFixed(2)),
      final_distance_mm: parseFloat((jawAngle * 0.8).toFixed(2))
    };
  }

  _sha256(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      hash = (hash << 5) - hash + str.charCodeAt(i);
      hash |= 0;
    }
    return "0x" + Math.abs(hash).toString(16).padStart(8, "0");
  }
}

// ─── Tests ───────────────────────────────────────────────────────────────────

const adapter = new AnnyAnatomicalAdapter();

describe("Suite 1 — Phenotype Demographics Shape Parameterization", () => {

  test("TC01: Verify initial demographic shape parameters structure", () => {
    assertEqual(adapter.patient_shape.age, 30);
    assertEqual(adapter.patient_shape.height_cm, 170);
  });

  test("TC02: Parameterize demographics successfully with valid WHO-compliant metrics", () => {
    const profile = { age: 24.5, height_cm: 165.0, weight_kg: 58.0, gender: "female" };
    const res = adapter.parameterizePatientShape(profile);
    assertEqual(res.status, "PARAMETERIZED");
    assertEqual(adapter.patient_shape.age, 24.5);
    assert(res.mesh_hash !== "0xinitialhash00");
  });

  test("TC03: Reject parameterization with out-of-bounds age (ANY-I1)", () => {
    const badProfile = { age: 135.0, height_cm: 170, weight_kg: 70, gender: "male" };
    assertThrows(() => {
      adapter.parameterizePatientShape(badProfile);
    }, "INVALID_DEMOGRAPHICS");
  });

  test("TC04: Reject parameterization with negative height/weight constraints", () => {
    const badProfile = { age: 40, height_cm: -10, weight_kg: 60, gender: "female" };
    assertThrows(() => {
      adapter.parameterizePatientShape(badProfile);
    }, "INVALID_DEMOGRAPHICS");
  });

});

describe("Suite 2 — Temporomandibular Joint Range of Motion Safety Gates", () => {

  test("TC05: Animate mandibular joint with flexion within safe range (30 degrees)", () => {
    const res = adapter.animateAnatomicalPose("temporomandibular_joint", { flexion: 30.0, lateral: 0 });
    assertEqual(res.status, "ANIMATED");
    assertEqual(adapter.joints_pose.get("temporomandibular_joint").flexion, 30.0);
  });

  test("TC06: Block pose animation when mandibular flexion exceeds 45 degrees limit (ANY-I2)", () => {
    assertThrows(() => {
      adapter.animateAnatomicalPose("temporomandibular_joint", { flexion: 55.0, lateral: 0 }); // > 45 degrees ROM
    }, "ROM_LIMIT_EXCEEDED");
  });

  test("TC07: Re-align head pitch joint orientation within standard parameters", () => {
    const res = adapter.animateAnatomicalPose("head", { pitch: 15.0, yaw: 0, roll: 0 });
    assertEqual(res.status, "ANIMATED");
    assertEqual(adapter.joints_pose.get("head").pitch, 15.0);
  });

});

describe("Suite 3 — Texture Mapping Coordinate Constraints", () => {

  test("TC08: Map coordinates successfully when UVs are within normalized box (0.0 to 1.0)", () => {
    const uvs = [{ u: 0.15, v: 0.85 }, { u: 0.45, v: 0.32 }];
    const vertices = [{ x: 1, y: 2, z: 3 }, { x: 4, y: 5, z: 6 }];
    const res = adapter.mapIntraoralTexture(vertices, uvs);
    assertEqual(res.status, "TEXTURE_MAPPED");
    assertEqual(adapter.uv_coordinates.length, 2);
  });

  test("TC09: Reject texture mapping when U coordinate is negative (ANY-I3)", () => {
    const badUvs = [{ u: -0.1, v: 0.5 }];
    assertThrows(() => {
      adapter.mapIntraoralTexture([{ x: 0, y: 0, z: 0 }], badUvs);
    }, "OUT_OF_BOUNDS_UV");
  });

  test("TC10: Reject texture mapping when V coordinate exceeds 1.0 boundary (ANY-I3)", () => {
    const badUvs = [{ u: 0.5, v: 1.05 }];
    assertThrows(() => {
      adapter.mapIntraoralTexture([{ x: 0, y: 0, z: 0 }], badUvs);
    }, "OUT_OF_BOUNDS_UV");
  });

});

describe("Suite 4 — Differentiable Optimizations (PyTorch Simulation)", () => {

  test("TC11: Run PyTorch-like gradient descent to fit jaw flexion to target distance (20mm)", () => {
    const res = adapter.optimizeJawOpening(20.0); // Target 20mm distance
    assertEqual(res.final_distance_mm, 20.0);
    assertEqual(res.optimized_flexion, 25.0); // 25 degrees * 0.8 = 20mm
  });

  test("TC12: Clamp optimization to range of motion limits when target distance is excessively high", () => {
    const res = adapter.optimizeJawOpening(100.0); // Target distance impossible (requires 125 degrees)
    assertEqual(res.optimized_flexion, 45.0); // Clamped at 45.0 degrees ROM
    assertEqual(res.final_distance_mm, 36.0); // 45 * 0.8 = 36mm max distance
  });

});

// ─── Test Report ──────────────────────────────────────────────────────────────

console.log("\n" + "═".repeat(60));
console.log("  OpenCode TDD — Anny Parametric Body Model Adapter Test Report");
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
