"""Teste basico de importacao."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from opencode_evosci import MentorAgent, EvoEngine, AgenticScienceV2

def test_import():
    assert MentorAgent is not None
    assert EvoEngine is not None
    assert AgenticScienceV2 is not None
