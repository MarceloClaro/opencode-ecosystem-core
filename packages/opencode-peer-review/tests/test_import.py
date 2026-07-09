"""Teste basico de importacao."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from opencode_peer_review import RubricEngine, MultiCriticReviewer, OrchestratorReviewer

def test_import():
    assert RubricEngine is not None
    assert MultiCriticReviewer is not None
    assert OrchestratorReviewer is not None
