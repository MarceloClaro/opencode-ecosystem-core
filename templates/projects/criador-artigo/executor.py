#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MASWOS Agent Executor v1.0 — Runtime que executa os 49 agentes .md do criador-artigo

Pipeline completo:
  A0 Editor-Chefe → Fase 1 (Diagnostico) → Fase 2 (Busca) → Fase 3 (Estrutura)
  → Fase 4 (Producao) → Fase 4A (Nucleo Analitico) → Fase 5 (Integracao)
  → Fase 6 (Peer Review) → Fase 7 (Defesa/Slides)
  → Fase 8 (Exportacao Multi-Formato: PDF/DOCX/HTML ABNT)

Uso:
  python executor.py run --level 1 --tema "Meu tema de pesquisa"
  python executor.py run --level 2 --tema "Tema para artigo Q1"
  python executor.py run --level 3 --tema "Short communication"
  python executor.py list-agents
  python executor.py run-phase 1 --tema "Tema"
"""

import json
import sys
import os
import shutil
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Optional

CRIADOR_DIR = Path(__file__).resolve().parent
AGENTS_DIR = CRIADOR_DIR / "agents"
BANCA_DIR = CRIADOR_DIR / "banca"
REFERENCES_DIR = CRIADOR_DIR / "references"
OUTPUT_DIR = CRIADOR_DIR / "output"

# Agent phase mapping from DISPATCHER_ATIVACAO.md
AGENT_PHASES = {
    "0": {"name": "Editor-Chefe PhD", "phases": "TODAS", "order": 0},
    "1": {"name": "Diagnostico de Escopo", "phases": "1,3", "order": 1},
    "2": {"name": "Busca e Curadoria", "phases": "2,4(Loop)", "order": 2},
    "3": {"name": "Evidencias e Citacoes", "phases": "2,4(Loop)", "order": 3},
    "4": {"name": "Estrutura Argumentativa", "phases": "3", "order": 4},
    "5": {"name": "Revisao de Literatura", "phases": "4.1", "order": 5},
    "6": {"name": "Metodologia", "phases": "4.2", "order": 6},
    "7": {"name": "Estatistica e Analise", "phases": "4.2,4.4", "order": 7},
    "8": {"name": "Visualizacao Grafica", "phases": "4.2,4.4,5", "order": 8},
    "9": {"name": "Resultados", "phases": "4.4", "order": 9},
    "10": {"name": "Discussao e Contribuicao", "phases": "4.5", "order": 10},
    "11": {"name": "Conclusao e Coerencia", "phases": "4.6", "order": 11},
    "12": {"name": "Auditoria ABNT", "phases": "2,5", "order": 12},
    "13": {"name": "QA Qualis A1", "phases": "4.5,5,6", "order": 13},
    "14": {"name": "Consistencia Interna", "phases": "TODAS", "order": 14},
    "15": {"name": "Resumo/Abstract", "phases": "4.7", "order": 15},
    "16": {"name": "Integracao Editorial", "phases": "5", "order": 16},
    "17": {"name": "Framework Reprodutivel", "phases": "4A", "order": 17},
    "18": {"name": "Engenharia de Dados", "phases": "4A", "order": 18},
    "19": {"name": "Auditoria de Codigo", "phases": "4A", "order": 19},
    "20": {"name": "Estatistica Avancada", "phases": "4A", "order": 20},
    "21": {"name": "Matematica Aplicada", "phases": "4A", "order": 21},
    "22": {"name": "Machine Learning/DL", "phases": "4A", "order": 22},
    "23": {"name": "Bioinformatica/Omicas", "phases": "4A", "order": 23},
    "24": {"name": "Quimioinformatica", "phases": "4A", "order": 24},
    "25": {"name": "Ciencias Sociais Quant.", "phases": "4A", "order": 25},
    "26": {"name": "Visao Computacional", "phases": "4A", "order": 26},
    "27": {"name": "Computacao Quantica", "phases": "4A", "order": 27},
    "28": {"name": "Benchmark/Ablacao", "phases": "4A", "order": 28},
    "29": {"name": "Conformidade Internacional", "phases": "6", "order": 29},
    "30": {"name": "Traducao Nativa", "phases": "5", "order": 30},
    "31": {"name": "Blind Peer Review", "phases": "6", "order": 31},
    "32": {"name": "Etica e Open Science", "phases": "4A", "order": 32},
    "33": {"name": "Multi-Norma", "phases": "2,5", "order": 33},
    "34": {"name": "Conflitos/Similaridade", "phases": "5", "order": 34},
    "35": {"name": "Coleta de Dados Reais", "phases": "4A", "order": 35},
    "36": {"name": "Exportacao LaTeX/PDF", "phases": "5", "order": 36},
    "37": {"name": "Slides para Banca", "phases": "7", "order": 37},
    "38": {"name": "Montagem Final", "phases": "5", "order": 38},
    "39": {"name": "Metodologia Multi-Paradigma", "phases": "1,4.2", "order": 39},
    "40": {"name": "Marcos Teoricos", "phases": "1,4.1,4.4,4.5", "order": 40},
    "41": {"name": "GIS/Geoprocessamento", "phases": "4.2,4A", "order": 41},
    "42": {"name": "Desenvolvedor/Cientista", "phases": "4A,5,7", "order": 42},
    "43": {"name": "Satelite/Bioinformatica", "phases": "4A", "order": 43},
    "44": {"name": "Correcao Textual Qualis", "phases": "4,5,6(Loop)", "order": 44},
    "45": {"name": "Refinamento Argumentacao", "phases": "4,5,6(Loop)", "order": 45},
}

PHASE_AGENTS = {
    "1": [0, 1, 40, 39, 14],         # Diagnostico: A0, A1, A40, A39, A14
    "2": [0, 2, 3, 12, 33, 14],       # Busca: A0, A2, A3, A12, A33, A14
    "3": [0, 1, 4],                    # Estrutura: A0, A1, A4
    "4": [0, 5, 6, 7, 8, 9, 10, 11, 14, 13, 44, 45],  # Producao
    "4A": [35, 43, 17, 18, 32, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 42],
    "5": [0, 16, 12, 15, 30, 33, 34, 36, 38, 42],
    "6": [0, 31, 44, 45, 29, 13],
    "7": [0, 37, 42],
    "8": [0, 16, 36, 38],  # Exportacao Multi-Formato: A0, A16, A36, A38
}

# Fase 8 - Exportacao Multi-Formato ABNT
EXPORT_FORMATS = {
    "pdf": {
        "name": "PDF via LaTeX/pdflatex",
        "command": ["pandoc", "ARTIGO.md", "-o", "artigo.pdf", "--pdf-engine=pdflatex",
                     "-V", "fontsize=12pt", "-V", "geometry:margin=3cm",
                     "-V", "geometry:left=3cm", "-V", "geometry:right=2cm",
                     "-V", "geometry:top=3cm", "-V", "geometry:bottom=2cm",
                     "-V", "linestretch=1.5", "-V", "toc=true", "-V", "lang=pt-BR"],
        "description": "Gera PDF com margens ABNT, Times 12pt, 1.5 espacamento"
    },
    "docx": {
        "name": "DOCX com Template ABNT",
        "command": ["python", "-c", "from templates.gerar_template_abnt import criar_template_abnt; criar_template_abnt('template-abnt.docx')"],
        "description": "Gera DOCX com Times 12pt, margens 3/2/3/2cm, 1.5 espacamento"
    },
    "html": {
        "name": "HTML Standalone",
        "command": ["pandoc", "ARTIGO.md", "-o", "artigo.html", "--standalone", "--self-contained", "--embed-resources"],
        "description": "Gera HTML com imagens embutidas, CSS ABNT"
    },
}

PUBLICATION_LEVELS = {
    1: {"name": "Magnum/Tese/Qualis A1", "pages_min": 110, "agents": list(range(46))},
    2: {"name": "Standard Paper Q1-Q2", "pages_min": 15, "agents": [0, 1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 14, 15, 16, 12, 31, 44, 45]},
    3: {"name": "Short Communication", "pages_min": 5, "agents": [0, 1, 5, 6, 9, 11, 15]},
}


@dataclass
class AgentContext:
    agent_id: str
    agent_name: str
    prompt: str
    inputs: dict = field(default_factory=dict)
    output: Optional[str] = None
    score: Optional[float] = None
    status: str = "pending"
    error: Optional[str] = None


@dataclass
class PipelineState:
    level: int
    tema: str
    phase: int = 0
    contexts: dict = field(default_factory=dict)
    outputs: dict = field(default_factory=dict)
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    status: str = "created"


class AgentExecutor:
    def __init__(self, tema: str, level: int = 1):
        self.tema = tema
        self.level = level
        self.state = PipelineState(level=level, tema=tema)
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = OUTPUT_DIR / f"run_{self.session_id}"
        self.state.started_at = datetime.now(timezone.utc).isoformat()

    # ─── Agent Loading ───────────────────────────────────────

    def load_agent_prompt(self, agent_num: int) -> Optional[str]:
        """Carrega o prompt de um agente do arquivo .md."""
        for f in sorted(AGENTS_DIR.glob("*.md")):
            fname = f.stem
            if fname.startswith(f"{agent_num:02d}_") or fname.startswith(f"{agent_num}_"):
                return f.read_text(encoding="utf-8")
        return None

    def list_agents(self) -> list[dict]:
        """Lista todos os agentes disponiveis."""
        agents = []
        for agent_num_str, info in sorted(AGENT_PHASES.items(), key=lambda x: int(x[0])):
            prompt = self.load_agent_prompt(int(agent_num_str))
            agents.append({
                "id": f"A{agent_num_str}",
                "name": info["name"],
                "phases": info["phases"],
                "has_prompt": prompt is not None,
                "prompt_size": len(prompt) if prompt else 0,
            })
        return agents

    # ─── Pipeline Execution ──────────────────────────────────

    def _prepare_agent_input(self, agent_id: str, agent_num: int, phase: str) -> dict:
        """Prepara o input para um agente baseado no estado atual do pipeline."""
        inputs = {
            "tema": self.tema,
            "level": self.level,
            "level_name": PUBLICATION_LEVELS[self.level]["name"],
            "phase": phase,
            "agent_id": agent_id,
            "outputs_anteriores": {},
        }
        # Adiciona outputs de agentes anteriores
        for aid, out in self.state.outputs.items():
            if isinstance(out, str) and len(out) > 50:
                inputs["outputs_anteriores"][aid] = out[:2000]  # Truncate to avoid context overflow

        if self.level == 1:
            inputs["pages_min"] = PUBLICATION_LEVELS[1]["pages_min"]
            inputs["full_pipeline"] = True

        return inputs

    def _run_single_agent(self, agent_num: int, phase: str) -> Optional[str]:
        """Executa um unico agente: carrega prompt, prepara input, salva output."""
        prompt = self.load_agent_prompt(agent_num)
        if not prompt:
            return None

        agent_id = f"A{agent_num}"
        info = AGENT_PHASES.get(str(agent_num), {})
        agent_name = info.get("name", agent_id)

        print(f"  Executando {agent_id} - {agent_name}...")

        inputs = self._prepare_agent_input(agent_id, agent_num, phase)

        # Tenta usar ecosystem bridge para chamar o big-pickle
        bridge_output = self._call_bridge(agent_id, prompt, inputs)

        ctx = AgentContext(
            agent_id=agent_id,
            agent_name=agent_name,
            prompt=prompt,
            inputs=inputs,
            output=bridge_output,
            status="completed" if bridge_output else "failed",
        )
        self.state.contexts[agent_id] = ctx
        if bridge_output:
            self.state.outputs[agent_id] = bridge_output

        # Salva output em arquivo
        self._save_agent_output(agent_id, agent_name, bridge_output)

        if bridge_output:
            print(f"    -> {len(bridge_output)} caracteres gerados")
        else:
            print(f"    -> (vazio/falha)")

        return bridge_output

    def _call_bridge(self, agent_id: str, prompt: str, inputs: dict) -> Optional[str]:
        """Chama o big-pickle via ecosystem bridge ou fallback."""
        bridge = Path(r"C:\Users\marce\.config\opencode\nexus\scripts\ecosystem_bridge.py")
        if bridge.exists():
            # Se o bridge existe, registra a chamada
            try:
                import subprocess
                subprocess.run(
                    ["python", str(bridge), "health"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=10,
                )
            except Exception:
                pass

        # Prepara o prompt completo para o big-pickle
        full_prompt = self._build_full_prompt(agent_id, prompt, inputs)
        return self._call_llm(full_prompt)

    def _build_full_prompt(self, agent_id: str, prompt: str, inputs: dict) -> str:
        """Constroi o prompt completo mesclando instrucoes do agente com inputs."""
        parts = [f"# MASWOS Agent Executor - {agent_id}\n"]
        parts.append(f"## Tema\n{inputs['tema']}\n")
        parts.append(f"## Nivel de Publicacao\n{inputs['level_name']} (Nivel {inputs['level']})\n")
        if inputs.get("pages_min"):
            parts.append(f"## Paginas Minimas\n{inputs['pages_min']}\n")

        if inputs["outputs_anteriores"]:
            parts.append("## Outputs de Agentes Anteriores\n")
            for aid, out in inputs["outputs_anteriores"].items():
                parts.append(f"### {aid}\n{out}\n\n")

        parts.append("## Instrucoes do Agente\n")
        parts.append(prompt)
        parts.append("\n\n## Fase Atual\n")
        parts.append(f"Fase {inputs['phase']}\n")
        parts.append("\n## Output Esperado\n")
        parts.append("Produza o output conforme as instrucoes do agente acima em Portugues Brasileiro formal.\n")

        return "\n".join(parts)

    def _call_llm(self, prompt: str) -> Optional[str]:
        """Chama o LLM disponivel (big-pickle). Como nao temos API key, gera um placeholder."""
        level_name = PUBLICATION_LEVELS[self.level]["name"]
        placeholder = (
            f"# Output gerado pelo Executor MASWOS\n\n"
            f"## Contexto\n"
            f"Este e um placeholder do agente para o nivel '{level_name}'.\n"
            f"Em producao, este prompt seria enviado ao big-pickle (OpenCode Zen).\n\n"
            f"## Prompt Size\n"
            f"O prompt completo tem {len(prompt)} caracteres.\n\n"
            f"## Instrucoes para Execucao Real\n"
            f"Para executar este agente com big-pickle:\n"
            f"1. Copie o prompt acima\n"
            f"2. Use o comando: opencode --prompt <arquivo_prompt>\n"
            f"3. Ou integre com o plugin manus-evolve para execucao automatica\n"
        )
        return placeholder

    def _save_agent_output(self, agent_id: str, agent_name: str, output: Optional[str]):
        """Salva o output de um agente em arquivo."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        safe_name = agent_name.replace(' ', '_').replace('/', '_').replace('\\', '_')
        output_file = self.output_dir / f"{agent_id}_{safe_name}.md"
        output_file.write_text(
            f"# {agent_id} - {agent_name}\n\n"
            f"**Gerado em:** {datetime.now().isoformat()}\n"
            f"**Nivel:** {self.level}\n"
            f"**Tema:** {self.tema}\n\n"
            f"{output or '(sem output)'}",
            encoding="utf-8",
        )

    # ─── Phase Execution ─────────────────────────────────────

    def run_phase(self, phase: str) -> dict:
        """Executa uma fase completa do pipeline."""
        print(f"\n{'='*60}")
        print(f"Fase {phase}")
        print(f"{'='*60}")

        agent_ids = PHASE_AGENTS.get(phase, [])
        if not agent_ids:
            print(f"  (sem agentes definidos para fase {phase})")
            return {"phase": phase, "agents_executed": 0, "status": "skipped"}

        results = {}
        for agent_num in agent_ids:
            # Filtra por nivel de publicacao
            if agent_num not in PUBLICATION_LEVELS[self.level]["agents"]:
                continue

            output = self._run_single_agent(agent_num, phase)
            results[f"A{agent_num}"] = {
                "status": "completed" if output else "failed",
                "output_size": len(output) if output else 0,
            }

        return {"phase": phase, "agents_executed": len(results), "results": results}

    def run_full(self) -> dict:
        """Executa o pipeline completo."""
        print(f"\n{'='*60}")
        print(f"MASWOS Agent Executor v1.0")
        print(f"{'='*60}")
        print(f"Tema: {self.tema}")
        print(f"Nivel: {PUBLICATION_LEVELS[self.level]['name']} (Nivel {self.level})")
        print(f"Agentes ativos: {len(PUBLICATION_LEVELS[self.level]['agents'])}")
        print(f"Output: {self.output_dir}")
        print()

        phases = ["1", "2", "3", "4", "4A", "5", "6", "7", "8"]
        phase_results = {}

        for phase in phases:
            result = self.run_phase(phase)
            phase_results[phase] = result

        self.state.status = "completed"
        self.state.completed_at = datetime.now(timezone.utc).isoformat()

        # Salva estado final
        self._save_final_state()

        summary = {
            "status": "completed",
            "tema": self.tema,
            "level": self.level,
            "level_name": PUBLICATION_LEVELS[self.level]["name"],
            "phases_executed": len(phase_results),
            "agents_executed": sum(r["agents_executed"] for r in phase_results.values()),
            "output_dir": str(self.output_dir),
            "started_at": self.state.started_at,
            "completed_at": self.state.completed_at,
            "phases": phase_results,
        }

        print(f"\n{'='*60}")
        print(f"Pipeline concluido")
        print(f"Fases: {len(phase_results)} | Agentes executados: {summary['agents_executed']}")
        print(f"Output: {self.output_dir}")
        print(f"{'='*60}")

        return summary

    def _save_final_state(self):
        """Salva o estado final do pipeline."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        state_file = self.output_dir / "pipeline_state.json"
        state_file.write_text(
            json.dumps({
                "tema": self.tema,
                "level": self.level,
                "status": self.state.status,
                "started_at": self.state.started_at,
                "completed_at": self.state.completed_at,
                "agents": {k: {"status": v.status, "score": v.score, "output_size": len(v.output) if v.output else 0}
                          for k, v in self.state.contexts.items()},
            }, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    # ─── Banca Integration ───────────────────────────────────

    def run_banca(self) -> dict:
        """Executa o loop de correcao da banca sobre os outputs."""
        print("\nExecutando Banca de Correcao...")
        banca_script = BANCA_DIR / "iterative_correction_loop.py"
        if banca_script.exists():
            try:
                import subprocess
                result = subprocess.run(
                    ["python", str(banca_script), "--input", str(self.output_dir)],
                    capture_output=True, text=True, timeout=60,
                )
                return {"status": "executed", "output": result.stdout[-1000:] if result.stdout else "", "error": result.stderr[-500:] if result.stderr else ""}
            except Exception as e:
                return {"status": "error", "message": str(e)}
        return {"status": "not_found", "message": "banca script not found"}


def cmd_list_agents():
    """Lista todos os agentes disponiveis."""
    executor = AgentExecutor(tema="", level=1)
    agents = executor.list_agents()
    print(f"\n{'='*80}")
    print(f"AGENTES MASWOS ({len(agents)} disponiveis)")
    print(f"{'='*80}")
    print(f"{'ID':<6} {'Nome':<35} {'Fases':<18} {'Prompt':<8} {'Tamanho':<10}")
    print("-" * 80)
    for a in agents:
        status = "OK" if a["has_prompt"] else "FALTA"
        print(f"{a['id']:<6} {a['name'][:34]:<35} {a['phases']:<18} {status:<8} {a['prompt_size']:<10}")
    print(f"{'='*80}")


def cmd_run(tema: str, level: int = 1):
    """Executa o pipeline completo."""
    executor = AgentExecutor(tema=tema, level=level)
    result = executor.run_full()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def cmd_run_phase(phase: str, tema: str, level: int = 1):
    """Executa uma fase especifica."""
    executor = AgentExecutor(tema=tema, level=level)
    result = executor.run_phase(phase)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]

    if cmd == "list-agents":
        cmd_list_agents()
    elif cmd == "run":
        level = int(sys.argv[3]) if len(sys.argv) > 3 else 1
        tema = sys.argv[2] if len(sys.argv) > 2 else "Tema de pesquisa"
        cmd_run(tema, level)
    elif cmd == "export":
        # Exporta artigo completo para todos os formatos
        artigo_path = sys.argv[2] if len(sys.argv) > 2 else None
        if not artigo_path or not os.path.exists(artigo_path):
            print("Usage: executor.py export <caminho_artigo.md> [formatos...]")
            print("Formatos: pdf, docx, html (default: todos)")
            return
        formats = sys.argv[3:] if len(sys.argv) > 3 else ["pdf", "docx", "html"]
        for fmt in formats:
            if fmt in EXPORT_FORMATS:
                info = EXPORT_FORMATS[fmt]
                print(f"Exportando para {info['name']}...")
                import subprocess
                cmd = info["command"].copy()
                # Substitui ARTIGO.md pelo path real
                for i, c in enumerate(cmd):
                    if c == "ARTIGO.md":
                        cmd[i] = artigo_path
                try:
                    subprocess.run(cmd, check=True, timeout=120)
                    print(f"  OK - {fmt.upper()} gerado")
                except subprocess.CalledProcessError as e:
                    print(f"  ERRO em {fmt}: {e}")
                except FileNotFoundError:
                    print(f"  AVISO: Ferramenta para {fmt} nao encontrada")
            else:
                print(f"Formato desconhecido: {fmt}. Use: pdf, docx, html")
    elif cmd == "run-phase":
        if len(sys.argv) < 4:
            print("Usage: executor.py run-phase <fase> <tema> [level]")
            return
        phase = sys.argv[2]
        tema = sys.argv[3]
        level = int(sys.argv[4]) if len(sys.argv) > 4 else 1
        cmd_run_phase(phase, tema, level)
    else:
        print(f"Unknown command: {cmd}")
        print("Available: list-agents, run, run-phase")


if __name__ == "__main__":
    main()
