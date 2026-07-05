# SPEC-AGE-11: Blockchain Security Auditor
Version: 1.0.0 | Status: verified | TDD: verified | Domain: specialized

## Objective
Agente especializado em auditoria de seguranca de smart contracts. Detecta vulnerabilidades conhecidas (reentrancy, unchecked calls, overflow, tx.origin, timestamp), calcula risk scores e gera relatorios estruturados.

## Acceptance Criteria
- [x] CT-1: Vulnerability risk scores map CRITICAL=10, HIGH=7, MEDIUM=4, LOW=2, INFO=0
- [x] CT-2: Aggregate risk score computes weighted average and determines safety threshold
- [x] CT-3: Pattern scanning detects known Solidity vulnerabilities in source code
- [x] CT-4: Report generation includes contract metadata, severity breakdown, and findings list

## Engine
<scripts/blockchain_auditor_engine.py> -> BlockchainAuditor

## Test Results
All CTs PASSED
