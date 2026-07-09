"""Teste basico de importacao."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from opencode_deep_research import EvidenceGraph, BFRSAgent, OrchestratorAgent

def test_import():
    assert EvidenceGraph is not None
    assert BFRSAgent is not None
    assert OrchestratorAgent is not None
