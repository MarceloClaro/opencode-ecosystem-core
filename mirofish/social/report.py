"""
MiroFish Social — ReportAgent determinístico (MIT, stdlib).

Gera relatório markdown estruturado a partir do resultado da simulação:
objetivo, metodologia, agentes, linha do tempo, sentimento e conclusão.
"""
from __future__ import annotations

from typing import Dict, List

from .contracts import OasisAgentProfile
from .engine import SimulationResult

SECTION_TITLES = [
    "Objetivo",
    "Metodologia",
    "Agentes",
    "Linha do Tempo",
    "Sentimento",
    "Conclusão",
]


class SocialReportGenerator:
    """Produz relatório markdown a partir de um SimulationResult."""

    def __init__(self, result: SimulationResult):
        self.result = result
        self._opinions = dict(result.final_opinions)

    def generate(self) -> str:
        lines: List[str] = []
        lines.append(f"# Relatório de Simulação Social — {self.result.simulation_id}")
        lines.append("")
        lines.append(self._section_obj())
        lines.append(self._section_method())
        lines.append(self._section_agents())
        lines.append(self._section_timeline())
        lines.append(self._section_sentiment())
        lines.append(self._section_conclusion())
        return "\n".join(lines)

    def _section_obj(self) -> str:
        req = self.result.parameters.simulation_requirement or "analisar a reação pública"
        return (
            f"## Objetivo\n\n"
            f"Simular a opinião pública sobre: **{req}**.\n\n"
            f"Total de {len(self.result.profiles)} agentes, {len(self.result.rounds)} rounds.\n"
        )

    def _section_method(self) -> str:
        pm = self.result.parameters
        return (
            "## Metodologia\n\n"
            f"- Motor: MiroFish Social determinístico (SPEC-976), seed={self.result.seed}.\n"
            f"- Plataforma: {pm.twitter_config.platform if pm.twitter_config else 'twitter'}.\n"
            f"- Horas simuladas: {pm.time_config.total_simulation_hours}, "
            f"{pm.time_config.minutes_per_round} min/round.\n"
            f"- Câmara de eco: {pm.twitter_config.echo_chamber_strength if pm.twitter_config else 0.5}.\n"
            f"- Tópicos quentes: {', '.join(pm.event_config.hot_topics) or 'n/d'}.\n"
        )

    def _section_agents(self) -> str:
        header = "| ID | Nome | Postura | Viés | Influência | Atividade |\n"
        sep = "|---:|---|---|---:|---:|---:|\n"
        rows = []
        for p in self.result.profiles:
            rows.append(
                f"| {p.user_id} | {p.name} | {p.stance} | {p.sentiment_bias:+.2f} "
                f"| {p.influence_weight:.2f} | {p.activity_level:.2f} |"
            )
        return "## Agentes\n\n" + header + sep + "\n".join(rows) + "\n"

    def _section_timeline(self) -> str:
        lines = ["## Linha do Tempo\n"]
        last_hour = None
        for r in self.result.rounds:
            hour = r.started_at_hour
            if hour != last_hour:
                lines.append(f"\n### Hora {hour:02d}:00 — {len(r.active_agents)} agentes ativos")
                last_hour = hour
            posts = [a for a in r.actions if a.action_type in ("CREATE_POST", "QUOTE_POST")]
            for a in posts[:3]:
                text = a.action_args.get("text", "")
                lines.append(f"- *{a.agent_name}*: {text}")
        return "\n".join(lines) + "\n"

    def _section_sentiment(self) -> str:
        lines = ["## Sentimento\n"]
        if not self.result.rounds:
            lines.append("Nenhum round registrado.\n")
            return "\n".join(lines)
        avg_series = [r.avg_sentiment for r in self.result.rounds if r.actions]
        if avg_series:
            first = avg_series[0]
            last = avg_series[-1]
            trend = "positiva ↗" if last > first + 0.05 else ("negativa ↘" if last < first - 0.05 else "estável →")
            lines.append(
                f"Sentimento inicial: **{first:+.3f}** → final: **{last:+.3f}** "
                f"(tendência {trend}).\n"
            )
        supportive = sum(1 for v in self._opinions.values() if v > 0.1)
        opposing = sum(1 for v in self._opinions.values() if v < -0.1)
        neutral = len(self._opinions) - supportive - opposing
        lines.append(
            f"Distribuição final: {supportive} favoráveis, {opposing} contrários, "
            f"{neutral} neutros.\n"
        )
        return "\n".join(lines) + "\n"

    def _section_conclusion(self) -> str:
        if not self._opinions:
            return "## Conclusão\n\nSimulação vazia — nenhum agente gerado.\n"
        mean = sum(self._opinions.values()) / len(self._opinions)
        verdict = "apoio majoritário" if mean > 0.1 else ("oposição majoritária" if mean < -0.1 else "polarização/neutralidade")
        return (
            "## Conclusão\n\n"
            f"O sentimento agregado final foi **{mean:+.3f}** (escala −1 a +1), indicando "
            f"**{verdict}**.\n\n"
            "*Relatório gerado pelo motor determinístico local (SPEC-976); não constitui "
            "pesquisa empírica com humanos reais.*\n"
        )


def _summarize(result: SimulationResult) -> Dict[str, object]:
    """Resumo compacto para integração com o orquestrador."""
    opinions = list(result.final_opinions.values())
    mean = sum(opinions) / len(opinions) if opinions else 0.0
    return {
        "simulation_id": result.simulation_id,
        "agents": len(result.profiles),
        "rounds": len(result.rounds),
        "final_sentiment": round(mean, 4),
        "post_count": sum(
            1 for r in result.rounds for a in r.actions
            if a.action_type in ("CREATE_POST", "QUOTE_POST")
        ),
    }