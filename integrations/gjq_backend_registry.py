"""Registro canônico dos recursos GJQ/Tiangong (SPEC-935-R1104).

O registro é estático e não acessa a rede. Ele separa o nome exibido na
interface do nome aceito pela API e marca explicitamente o que não foi
verificado na documentação oficial. O estado, a fila e a calibração mudam:
use o MCP `gjq-runtime` para a leitura ao vivo.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import asdict, dataclass
from typing import Any, Iterable

SNAPSHOT: dict[str, Any] = {
    "source": "https://www.tiangongqs.com/cloud/server",
    "captured_at": "2026-11-09",
    "captured_by": "user-provided",
    "note": (
        "Snapshot informado pelo usuário; não foi obtido por automação autenticada. "
        "Status, fila e calibração podem mudar. Confirme com gjq_list_backends."
    ),
}


@dataclass(frozen=True)
class Backend:
    id: str
    display_name: str
    family: str
    kind: str
    qubits: int
    status: str
    jobs: int
    t1_us: float | None
    t2_us: float | None
    calibrated_at: str | None
    api_name: str | None
    api_name_verified: bool
    aliases: tuple[str, ...]
    hardware: bool
    requires_allow_hardware: bool
    amplitude_index_required: bool = False
    partial_amplitude: bool = False
    simulator_config_required: bool = False
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


BACKENDS: tuple[Backend, ...] = (
    Backend(
        id="guoji-01",
        display_name="Guoji No.1",
        family="hardware",
        kind="superconducting",
        qubits=20,
        status="maintenance",
        jobs=0,
        t1_us=15.92,
        t2_us=4.53,
        calibrated_at="2026-10-16T17:56:02",
        api_name="Guoji01",
        api_name_verified=False,
        aliases=("Guoji1", "Guoji01", "Guoji No. 1"),
        hardware=True,
        requires_allow_hardware=True,
        notes="Hardware supercondutor em manutenção no snapshot; nome de API não confirmado.",
    ),
    Backend(
        id="guoji-04",
        display_name="Guoji No.4",
        family="hardware",
        kind="superconducting",
        qubits=100,
        status="maintenance",
        jobs=0,
        t1_us=12.89,
        t2_us=2.54,
        calibrated_at="2026-10-16T17:56:02",
        api_name="Guoji04",
        api_name_verified=False,
        aliases=("Guoji4", "Guoji04", "Guoji No. 4"),
        hardware=True,
        requires_allow_hardware=True,
        notes="Hardware supercondutor em manutenção no snapshot; nome de API não confirmado.",
    ),
    Backend(
        id="guoji-07",
        display_name="Guoji No.7",
        family="hardware",
        kind="superconducting",
        qubits=100,
        status="maintenance",
        jobs=0,
        t1_us=20.57,
        t2_us=5.43,
        calibrated_at="2026-10-16T17:56:02",
        api_name="Guoji07",
        api_name_verified=False,
        aliases=("Guoji7", "Guoji07", "Guoji No. 7"),
        hardware=True,
        requires_allow_hardware=True,
        notes="Hardware supercondutor em manutenção no snapshot; nome de API não confirmado.",
    ),
    Backend(
        id="guoji-08-sim",
        display_name="Guoji No.8 (simulate)",
        family="hardware",
        kind="emulated_hardware",
        qubits=20,
        status="online",
        jobs=0,
        t1_us=85.2,
        t2_us=48.6,
        calibrated_at="2026-11-09T08:34:35",
        api_name="Guoji08",
        api_name_verified=True,
        aliases=("Guoji8", "Guoji08", "Guoji No. 8", "Guoji No.8 (simulate)"),
        hardware=False,
        requires_allow_hardware=True,
        notes=(
            "A interface de 2026-11-09 mostra '(simulate)'. Resultados históricos "
            "rotulados Guoji08 devem ser lidos com a data e a calibração da época. "
            "O gate de hardware permanece conservador."
        ),
    ),
    Backend(
        id="baihua",
        display_name="Baihua",
        family="hardware",
        kind="superconducting",
        qubits=156,
        status="online",
        jobs=0,
        t1_us=73.06,
        t2_us=26.36,
        calibrated_at="2026-11-09T07:45:38",
        api_name="Baihua",
        api_name_verified=True,
        aliases=("Baihua 156",),
        hardware=True,
        requires_allow_hardware=True,
        notes="Hardware supercondutor online no snapshot; custo e fila não são inferidos.",
    ),
    Backend(
        id="yudu",
        display_name="Yudu",
        family="hardware",
        kind="superconducting",
        qubits=72,
        status="maintenance",
        jobs=0,
        t1_us=46.2,
        t2_us=10.21,
        calibrated_at="2026-10-16T17:56:03",
        api_name="Yudu",
        api_name_verified=False,
        aliases=("Yu Du",),
        hardware=True,
        requires_allow_hardware=True,
        notes="Hardware em manutenção no snapshot; nome de API não confirmado.",
    ),
    Backend(
        id="jiuxiao-fas-cpu",
        display_name="Jiuxiao-Full Amplitude Simulator",
        family="cpu",
        kind="full_amplitude",
        qubits=20,
        status="online",
        jobs=68,
        t1_us=None,
        t2_us=None,
        calibrated_at=None,
        api_name="FAS-CPU",
        api_name_verified=True,
        aliases=("Jiuxiao", "FAS-CPU", "Full Amplitude CPU"),
        hardware=False,
        requires_allow_hardware=False,
        notes="Simulador full-amplitude de CPU; 68 jobs no snapshot.",
    ),
    Backend(
        id="jiuyun-noise-cpu",
        display_name="Jiuyun-Noise Simulator",
        family="cpu",
        kind="noise",
        qubits=20,
        status="online",
        jobs=0,
        t1_us=None,
        t2_us=None,
        calibrated_at=None,
        api_name=None,
        api_name_verified=False,
        aliases=("Jiuyun", "Noise CPU"),
        hardware=False,
        requires_allow_hardware=False,
        notes="Simulador de ruído; modelo e opções dependem do backend, não é calibração real.",
    ),
    Backend(
        id="jiuyuan-sas-cpu",
        display_name="Jiuyuan-Single Amplitude Simulator",
        family="cpu",
        kind="single_amplitude",
        qubits=200,
        status="online",
        jobs=3,
        t1_us=None,
        t2_us=None,
        calibrated_at=None,
        api_name="SAS-CPU",
        api_name_verified=True,
        aliases=("Jiuyuan", "SAS-CPU", "Single Amplitude CPU"),
        hardware=False,
        requires_allow_hardware=False,
        amplitude_index_required=True,
        notes="Single-amplitude exige amplitude_index; 3 jobs no snapshot.",
    ),
    Backend(
        id="jiuci-pas-cpu",
        display_name="Jiuci-Partial Amplitude Simulator",
        family="cpu",
        kind="partial_amplitude",
        qubits=20,
        status="online",
        jobs=0,
        t1_us=None,
        t2_us=None,
        calibrated_at=None,
        api_name=None,
        api_name_verified=False,
        aliases=("Jiuci", "Partial Amplitude CPU"),
        hardware=False,
        requires_allow_hardware=False,
        partial_amplitude=True,
        notes="Partial-amplitude; não equivale a full-amplitude. Verifique opções no backend.",
    ),
    Backend(
        id="qilv-fas-gpu",
        display_name="Qilv-Full Amplitude Simulator",
        family="gpu",
        kind="full_amplitude",
        qubits=29,
        status="online",
        jobs=8,
        t1_us=None,
        t2_us=None,
        calibrated_at=None,
        api_name="FAS-GPU",
        api_name_verified=True,
        aliases=("Qilv", "FAS-GPU", "Full Amplitude GPU"),
        hardware=False,
        requires_allow_hardware=False,
        notes=(
            "Simulador full-amplitude de GPU; a documentação antiga citava 32 qubits "
            "e o snapshot mostra 29. Use o limite do backend ao vivo."
        ),
    ),
    Backend(
        id="qijian-noise-gpu",
        display_name="Qijian-Noise Simulator",
        family="gpu",
        kind="noise",
        qubits=29,
        status="online",
        jobs=0,
        t1_us=None,
        t2_us=None,
        calibrated_at=None,
        api_name=None,
        api_name_verified=False,
        aliases=("Qijian", "Noise GPU"),
        hardware=False,
        requires_allow_hardware=False,
        notes="Simulador de ruído em GPU; modelo e opções dependem do backend.",
    ),
    Backend(
        id="qiyao-sas-gpu",
        display_name="Qiyao-Single Amplitude Simulator",
        family="gpu",
        kind="single_amplitude",
        qubits=29,
        status="online",
        jobs=1,
        t1_us=None,
        t2_us=None,
        calibrated_at=None,
        api_name="SAS-GPU",
        api_name_verified=True,
        aliases=("Qiyao", "SAS-GPU", "Single Amplitude GPU"),
        hardware=False,
        requires_allow_hardware=False,
        amplitude_index_required=True,
        notes="Single-amplitude exige amplitude_index; 1 job no snapshot.",
    ),
    Backend(
        id="qijing-pas-gpu",
        display_name="Qijing-Partial Amplitude Simulator",
        family="gpu",
        kind="partial_amplitude",
        qubits=29,
        status="online",
        jobs=0,
        t1_us=None,
        t2_us=None,
        calibrated_at=None,
        api_name=None,
        api_name_verified=False,
        aliases=("Qijing", "Partial Amplitude GPU"),
        hardware=False,
        requires_allow_hardware=False,
        partial_amplitude=True,
        notes="Partial-amplitude em GPU; verifique opções e limites no backend.",
    ),
    Backend(
        id="mps",
        display_name="MPS Simulator",
        family="mps",
        kind="tensor_network",
        qubits=997,
        status="online",
        jobs=51,
        t1_us=None,
        t2_us=None,
        calibrated_at=None,
        api_name="MPS",
        api_name_verified=True,
        aliases=("MPS", "Tensor Network", "Matrix Product State"),
        hardware=False,
        requires_allow_hardware=False,
        simulator_config_required=True,
        notes=(
            "MPS exige simulator_config e aceita presets fast/balanced/accurate. "
            "997 qubits é capacidade, não garantia de que um circuito profundo seja prático."
        ),
    ),
    Backend(
        id="liangshi-fas-npu",
        display_name="Liangshi-Full Amplitude Simulator",
        family="npu",
        kind="full_amplitude",
        qubits=10,
        status="online",
        jobs=0,
        t1_us=None,
        t2_us=None,
        calibrated_at=None,
        api_name=None,
        api_name_verified=False,
        aliases=("Liangshi", "Full Amplitude NPU"),
        hardware=False,
        requires_allow_hardware=False,
        notes="Simulador full-amplitude em NPU; 10 qubits no snapshot.",
    ),
    Backend(
        id="weina-noise-npu",
        display_name="Weina-Noise Simulator",
        family="npu",
        kind="noise",
        qubits=10,
        status="online",
        jobs=0,
        t1_us=None,
        t2_us=None,
        calibrated_at=None,
        api_name=None,
        api_name_verified=False,
        aliases=("Weina", "Noise NPU"),
        hardware=False,
        requires_allow_hardware=False,
        notes="Simulador de ruído em NPU; modelo e opções dependem do backend.",
    ),
    Backend(
        id="weichi-sas-npu",
        display_name="Weichi-Single Amplitude Simulator",
        family="npu",
        kind="single_amplitude",
        qubits=10,
        status="online",
        jobs=0,
        t1_us=None,
        t2_us=None,
        calibrated_at=None,
        api_name=None,
        api_name_verified=False,
        aliases=("Weichi", "Single Amplitude NPU"),
        hardware=False,
        requires_allow_hardware=False,
        amplitude_index_required=True,
        notes="Single-amplitude em NPU; exige amplitude_index.",
    ),
    Backend(
        id="weixin-pas-npu",
        display_name="Weixin-Partial Amplitude Simulator",
        family="npu",
        kind="partial_amplitude",
        qubits=10,
        status="online",
        jobs=0,
        t1_us=None,
        t2_us=None,
        calibrated_at=None,
        api_name=None,
        api_name_verified=False,
        aliases=("Weixin", "Partial Amplitude NPU"),
        hardware=False,
        requires_allow_hardware=False,
        partial_amplitude=True,
        notes="Partial-amplitude em NPU; verifique opções e limites no backend.",
    ),
)

BY_ID: dict[str, Backend] = {b.id: b for b in BACKENDS}


def normalize_name(value: str) -> str:
    """Normaliza rótulos da UI/API para comparação tolerante a pontuação."""
    if not isinstance(value, str):
        return ""
    text = unicodedata.normalize("NFKD", value)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"\([^)]*\)", " ", text)
    text = re.sub(r"\bno\.?\s*", "", text.lower())
    return re.sub(r"[^a-z0-9]+", "", text)


def _keys(backend: Backend) -> set[str]:
    return {
        normalize_name(backend.id),
        normalize_name(backend.display_name),
        *(normalize_name(a) for a in backend.aliases),
        *({normalize_name(backend.api_name)} if backend.api_name else set()),
    }


def resolve_backend(query: str) -> list[dict[str, Any]]:
    """Resolve por ID, nome exibido, nome de API ou alias.

    Retorna todos os matches para que o chamador não escolha silenciosamente
    quando houver ambiguidade.
    """
    if not isinstance(query, str) or not query.strip():
        return []
    raw = query.strip()
    if raw in BY_ID:
        return [BY_ID[raw].to_dict()]
    wanted = normalize_name(raw)
    matches = [b for b in BACKENDS if wanted in _keys(b)]
    if not matches:
        # Última tentativa: prefixo/sufixo claro, sem fuzzy perigoso.
        matches = [
            b for b in BACKENDS
            if any(k.startswith(wanted) or wanted.startswith(k) for k in _keys(b))
        ]
    return [b.to_dict() for b in matches]


def get_backend(backend_id: str) -> Backend | None:
    return BY_ID.get(backend_id)


def catalog(
    family: str | None = None,
    include_maintenance: bool = True,
    only_online: bool = False,
) -> dict[str, Any]:
    rows = list(BACKENDS)
    if family:
        rows = [b for b in rows if b.family == family]
    if only_online:
        rows = [b for b in rows if b.status == "online"]
    elif not include_maintenance:
        rows = [b for b in rows if b.status != "maintenance"]
    return {
        "snapshot": SNAPSHOT,
        "total": len(rows),
        "backends": [b.to_dict() for b in rows],
    }


def snapshot_summary() -> dict[str, Any]:
    families: dict[str, int] = {}
    statuses: dict[str, int] = {}
    for backend in BACKENDS:
        families[backend.family] = families.get(backend.family, 0) + 1
        statuses[backend.status] = statuses.get(backend.status, 0) + 1
    return {
        "snapshot": SNAPSHOT,
        "total": len(BACKENDS),
        "families": families,
        "statuses": statuses,
        "max_qubits": max(b.qubits for b in BACKENDS),
        "online": sum(1 for b in BACKENDS if b.status == "online"),
        "maintenance": sum(1 for b in BACKENDS if b.status == "maintenance"),
    }


def select_backends(
    family: str | None = None,
    min_qubits: int = 1,
    status: str | None = "online",
    limit: int = 10,
) -> list[dict[str, Any]]:
    if isinstance(min_qubits, bool) or not isinstance(min_qubits, int) or min_qubits < 1:
        raise ValueError("min_qubits deve ser inteiro >= 1")
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 50:
        raise ValueError("limit deve estar entre 1 e 50")
    rows = [b for b in BACKENDS if b.qubits >= min_qubits]
    if family:
        rows = [b for b in rows if b.family == family]
    if status:
        rows = [b for b in rows if b.status == status]
    rows.sort(key=lambda b: (b.qubits, b.family, b.id))
    return [b.to_dict() for b in rows[:limit]]


def is_hardware_name(name: str) -> bool:
    """Gate conservador: nomes conhecidos de hardware/emulação exigem allow."""
    matches = resolve_backend(name)
    if matches:
        return any(m["requires_allow_hardware"] for m in matches)
    low = normalize_name(name)
    return any(token in low for token in ("guoji", "baihua", "yudu"))


def research_plan(
    goal: str,
    num_qubits: int,
    depth: int = 4,
    shots: int = 1024,
    hardware_allowed: bool = False,
    prefer: str | None = None,
    needs_single_amplitude: bool = False,
    needs_partial_amplitude: bool = False,
) -> dict[str, Any]:
    if not isinstance(goal, str) or not goal.strip():
        raise ValueError("goal obrigatório")
    for label, value in (("num_qubits", num_qubits), ("depth", depth), ("shots", shots)):
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise ValueError(f"{label} deve ser inteiro >= 1")
    if depth > 1000:
        raise ValueError("depth acima de 1000 não é planejado neste catálogo")
    if shots > 100_000:
        raise ValueError("shots acima de 100000 não é planejado neste catálogo")

    candidates = [b for b in BACKENDS if b.status == "online" and b.qubits >= num_qubits]
    if not hardware_allowed:
        candidates = [b for b in candidates if not b.requires_allow_hardware]
    if needs_single_amplitude:
        candidates = [b for b in candidates if b.amplitude_index_required]
    elif needs_partial_amplitude:
        candidates = [b for b in candidates if b.partial_amplitude]
    else:
        # Sampling geral não deve cair em single/partial amplitude por engano.
        candidates = [b for b in candidates
                      if not b.amplitude_index_required and not b.partial_amplitude]
    families = {"cpu", "gpu", "npu", "mps", "hardware"}
    pref = prefer.strip().lower() if prefer else None
    if pref is not None and pref not in families:
        raise ValueError(f"prefer deve ser um de {sorted(families)}")
    if pref == "hardware":
        candidates = [b for b in candidates if b.requires_allow_hardware]
    elif pref:
        preferred = [b for b in candidates if b.family == pref]
        candidates = preferred + [b for b in candidates if b not in preferred]

    if not candidates:
        return {
            "status": "blocked",
            "goal": goal.strip(),
            "requested": {"num_qubits": num_qubits, "depth": depth, "shots": shots,
                          "hardware_allowed": hardware_allowed,
                          "needs_single_amplitude": needs_single_amplitude,
                          "needs_partial_amplitude": needs_partial_amplitude},
            "reason": "nenhum backend online atende aos filtros",
            "warnings": [
                "Estados e capacidades mudam; confirme com gjq_list_backends.",
                "Hardware exige allow_hardware=True e revisão de custo.",
            ],
        }

    # Ordem padrão: CPU, GPU, NPU, MPS e, por último, hardware/emulação.
    # Dentro da família, o menor backend que atende. Com prefer=hardware,
    # hardware real vem antes de emulação; o custo continua sendo do operador.
    rank = {"cpu": 0, "gpu": 1, "npu": 2, "mps": 3, "hardware": 4}
    kind_rank = {
        "full_amplitude": 0,
        "tensor_network": 1,
        "noise": 2,
        "partial_amplitude": 3,
        "single_amplitude": 4,
        "superconducting": 5,
        "emulated_hardware": 6,
    }
    if pref == "hardware":
        candidates.sort(key=lambda b: (not b.hardware, kind_rank.get(b.kind, 9), b.qubits, b.id))
    else:
        candidates.sort(key=lambda b: (rank.get(b.family, 9), kind_rank.get(b.kind, 9), b.qubits, b.id))
    chosen = candidates[0]
    alternatives = candidates[1:4]
    warnings = [
        "Snapshot de 2026-11-09; confirme o nome e o estado com gjq_list_backends.",
        "Capacidade de qubits não garante que o circuito seja prático.",
        "Counts corretos não provam fidelidade, emaranhamento ou vantagem quântica.",
    ]
    if chosen.requires_allow_hardware:
        warnings.append("Backend de hardware/emulação: exige allow_hardware=True e confirm=True.")
    if chosen.amplitude_index_required:
        warnings.append("Single-amplitude exige amplitude_index.")
    if chosen.simulator_config_required:
        warnings.append("MPS exige simulator_config; presets afetam velocidade e precisão.")
    if chosen.partial_amplitude:
        warnings.append("Partial-amplitude não é full-amplitude; declare o subconjunto medido.")

    return {
        "status": "planned",
        "goal": goal.strip(),
        "requested": {"num_qubits": num_qubits, "depth": depth, "shots": shots,
                      "hardware_allowed": hardware_allowed,
                      "needs_single_amplitude": needs_single_amplitude,
                      "needs_partial_amplitude": needs_partial_amplitude},
        "recommended": chosen.to_dict(),
        "alternatives": [b.to_dict() for b in alternatives],
        "protocol": [
            "Confirme o nome e o estado com gjq_list_backends.",
            "Leia configuração/calibração com gjq_backend_config e gjq_backend_properties.",
            "Prepare o QASM e transpile para o backend escolhido.",
            "Submeta com confirm=True; hardware/emulação também exige allow_hardware=True.",
            "Guarde task_id, backend, shots, timestamp, SHA-256 do QASM e versão do SDK.",
            "Audite counts e erro padrão; não reenvie o mesmo circuito sem necessidade.",
        ],
        "warnings": warnings,
        "executed": False,
        "network_access": False,
    }


def compare_plan(
    num_qubits: int,
    shots: int = 1024,
    include_hardware: bool = False,
) -> dict[str, Any]:
    if isinstance(num_qubits, bool) or not isinstance(num_qubits, int) or num_qubits < 1:
        raise ValueError("num_qubits deve ser inteiro >= 1")
    if isinstance(shots, bool) or not isinstance(shots, int) or not 1 <= shots <= 100_000:
        raise ValueError("shots deve estar entre 1 e 100000")
    sims = [b for b in BACKENDS if b.status == "online" and b.qubits >= num_qubits
            and not b.requires_allow_hardware and not b.amplitude_index_required]
    rank = {"cpu": 0, "gpu": 1, "npu": 2, "mps": 3}
    kind_rank = {"full_amplitude": 0, "tensor_network": 1, "noise": 2,
                 "partial_amplitude": 3, "single_amplitude": 4}
    sims.sort(key=lambda b: (rank.get(b.family, 9), kind_rank.get(b.kind, 9), b.qubits, b.id))
    sim = sims[0] if sims else None
    hardware = None
    if include_hardware:
        hw = [b for b in BACKENDS if b.status == "online" and b.qubits >= num_qubits
              and b.requires_allow_hardware]
        hw.sort(key=lambda b: (not b.hardware, b.qubits, b.id))
        hardware = hw[0] if hw else None
    return {
        "status": "planned" if sim else "blocked",
        "num_qubits": num_qubits,
        "shots": shots,
        "simulator": sim.to_dict() if sim else None,
        "hardware": hardware.to_dict() if hardware else None,
        "protocol": [
            "Execute o mesmo QASM no simulador e, se autorizado, no hardware.",
            "Compare distribuições, não apenas o resultado mais frequente.",
            "Registre task_id, backend, calibração e data de cada execução.",
            "Não trate diferença como ruído sem hipótese e repetição.",
        ],
        "warnings": [
            "Comparação não é prova de fidelidade; é observação com limites.",
            "Hardware exige allow_hardware=True e revisão de custo.",
        ],
        "executed": False,
        "network_access": False,
    }


def backend_limits() -> dict[str, Any]:
    return {
        "snapshot": SNAPSHOT,
        "runtime_max_qubits_default": 200,
        "runtime_max_qubits_env": "GJQ_MAX_QUBITS",
        "max_shots_default": 100_000,
        "max_qasm_chars": 50_000,
        "max_submissions_per_process": 20,
        "by_family": {
            "hardware": {"max_qubits": max(b.qubits for b in BACKENDS if b.family == "hardware"),
                         "requires_allow_hardware": True},
            "cpu": {"max_qubits": max(b.qubits for b in BACKENDS if b.family == "cpu")},
            "gpu": {"max_qubits": max(b.qubits for b in BACKENDS if b.family == "gpu")},
            "mps": {"max_qubits": max(b.qubits for b in BACKENDS if b.family == "mps"),
                    "requires_simulator_config": True},
            "npu": {"max_qubits": max(b.qubits for b in BACKENDS if b.family == "npu")},
        },
        "constraints": [
            "Single-amplitude exige amplitude_index.",
            "MPS exige simulator_config e não garante praticidade em circuitos profundos.",
            "Hardware/emulação exige allow_hardware=True e confirm=True.",
            "O limite global de 200 qubits pode ser elevado por GJQ_MAX_QUBITS, com revisão.",
        ],
        "executed": False,
    }


def provenance_template() -> dict[str, Any]:
    return {
        "required": [
            "task_id",
            "backend",
            "backend_kind",
            "shots",
            "timestamp_utc",
            "qasm_sha256",
            "sdk_version",
            "qiskit_version",
            "status",
            "counts_or_evs",
            "audit",
            "limitations",
        ],
        "audit": {
            "counts_sum_equals_shots": "verificar",
            "standard_error": "por chave",
            "calibration_snapshot": "data e T1/T2",
            "repetitions": ">= 2 quando a conclusão depender de diferença",
        },
        "limits": "Soma correta não prova fidelidade, emaranhamento ou vantagem quântica.",
        "executed": False,
    }


def calibration_snapshot() -> dict[str, Any]:
    rows = [
        {
            "backend": b.display_name,
            "id": b.id,
            "family": b.family,
            "qubits": b.qubits,
            "status": b.status,
            "t1_us": b.t1_us,
            "t2_us": b.t2_us,
            "calibrated_at": b.calibrated_at,
        }
        for b in BACKENDS
        if b.t1_us is not None or b.t2_us is not None
    ]
    return {
        "snapshot": SNAPSHOT,
        "rows": rows,
        "warning": (
            "T1/T2 do snapshot não são promessa de desempenho. A calibração muda; "
            "leia gjq_backend_properties antes de comparar execuções."
        ),
    }
