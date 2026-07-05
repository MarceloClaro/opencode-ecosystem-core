# SPEC_EVO14_SPE_BLOCKCHAIN_AUDITOR -- Blockchain Security Auditor Engine v1.0

**Domain**: agency-agents/specialized/blockchain-security-auditor
**Python**: 3.12, stdlib only
**Status**: Draft

---

## CT-01: Vulnerability Risk Scores
CRITICAL=10, HIGH=7, MEDIUM=4, LOW=2, INFO=0. is_critical_or_high e needs_immediate_action.

## CT-02: Aggregate Risk Score
3 findings (C+H+M) = 21/3 = 7.0. total_findings=3, critical_count=1, is_safe=False.

## CT-03: Pattern Scanning
Codigo Solidity com reentrancy detecta findings > 0 via scan_patterns().

## CT-04: Report Generation
generate_report() contem todos os campos: contract, address, total_findings, critical, severity_breakdown, risk_score.

---

## Implementation
- `scripts/blockchain_auditor_engine.py`: ContractAudit, Vulnerability, VulnSeverity, scan_patterns, KNOWN_PATTERNS
- `tests/test_blockchain_auditor.py`: 4 CTs via pytest
