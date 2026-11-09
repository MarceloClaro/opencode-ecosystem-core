"""Métricas e harness de eficiência de circuitos quânticos (R1108)."""
from .metrics import circuit_metrics, dist_ideal, tvd, transpile_measured
from .benchmarks import BENCHMARKS

__all__ = ["circuit_metrics", "dist_ideal", "tvd", "transpile_measured", "BENCHMARKS"]
