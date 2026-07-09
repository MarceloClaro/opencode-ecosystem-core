# -*- coding: utf-8 -*-
# Re-export do core
import sys, os
_core_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..")
if _core_dir not in sys.path:
    sys.path.insert(0, _core_dir)
from agentic_science_v2.evolutionary_engine import EvoEngine, EvolutionRound
