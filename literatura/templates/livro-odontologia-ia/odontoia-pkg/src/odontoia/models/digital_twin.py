"""
Módulo digital_twin — Gêmeos digitais odontológicos simplificados.

Implementa conceitos do Capítulo 13 (Gêmeos Digitais em Odontologia),
incluindo:
    - Representação digital simplificada da arcada dentária
    - Codificação de características em espaço latente (encoder)
    - Simulação de intervenções odontológicas
    - Visualização básica do gêmeo digital

Classes:
    DentalTwin         : Gêmeo digital de uma arcada dentária
    TwinEncoder        : Autoencoder simplificado para representação latente

Funções:
    build_twin_encoder     : Constrói encoder para representação compacta
    estimate_intervention  : Simula intervenção odontológica no gêmeo digital
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


# =============================================================================
# Estruturas de dados
# =============================================================================


@dataclass
class ToothState:
    """Estado odontológico de um dente individual.

    Attributes:
        numero: Número do dente (FDI: 11-48, ou  51-85 para decíduas)
        saudavel: Se o dente está hígido
        carie: Presença de cárie (True/False)
        restaurado: Presença de restauração (True/False)
        lesao_periapical: Presença de lesão periapical (True/False)
        fratura: Presença de fratura (True/False)
        mobilidade: Grau de mobilidade (0-3)
        profundidade_sondagem: Profundidade de sondagem periodontal (mm)
        perda_ossea: Perda óssea radiográfica estimada (%)
        pos_x, pos_y: Posição aproximada na arcada dentária (coordenadas)
    """

    numero: int
    saudavel: bool = True
    carie: bool = False
    restaurado: bool = False
    lesao_periapical: bool = False
    fratura: bool = False
    mobilidade: int = 0
    profundidade_sondagem: float = 2.0
    perda_ossea: float = 0.0
    pos_x: float = 0.0
    pos_y: float = 0.0

    def to_vector(self) -> np.ndarray:
        """Converte o estado do dente em vetor numérico.

        Returns:
            ndarray de 8 elementos com o estado codificado
        """
        return np.array(
            [
                float(self.saudavel),
                float(self.carie),
                float(self.restaurado),
                float(self.lesao_periapical),
                float(self.fratura),
                float(self.mobilidade) / 3.0,  # normaliza
                self.profundidade_sondagem / 12.0,  # normaliza (max ~12mm)
                self.perda_ossea / 100.0,  # normaliza (0-100%)
            ],
            dtype=np.float32,
        )


@dataclass
class DentalTwin:
    """Gêmeo digital de uma arcada dentária.

    Representação computacional da condição odontológica do paciente,
    permitindo simulação de intervenções e prognósticos.

    Attributes:
        patient_id: Identificador do paciente
        teeth: Lista de estados dentários (ToothState)
        periodontal_stage: Estágio periodontal (0-5 conforme AAP/EFP)
        hygiene_index: Índice de higiene oral (0-5)
        bone_density: Densidade óssea estimada (0-100%)
        created_at: Timestamp de criação (opcional)
        metadata: Metadados adicionais do paciente
    """

    patient_id: str
    teeth: List[ToothState] = field(default_factory=list)
    periodontal_stage: int = 0
    hygiene_index: float = 3.0
    bone_density: float = 80.0
    metadata: Dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.teeth:
            self._init_default_teeth()

    def _init_default_teeth(self):
        """Inicializa os 32 dentes permanentes em estado saudável
        com posições aproximadas na arcada.
        """
        # Dentes superiores (11-28)
        for i, num in enumerate(range(11, 29)):
            # Posição em parábola superior
            angle = np.pi * (i / 17)  # distribuição em 180 graus
            x = 50 * np.cos(angle - np.pi / 2)
            y = 30 * np.sin(np.pi - angle) + 60
            self.teeth.append(ToothState(numero=num, pos_x=x, pos_y=y))

        # Dentes inferiores (31-48)
        for i, num in enumerate(range(31, 49)):
            angle = np.pi * (i / 17)
            x = 50 * np.cos(angle - np.pi / 2)
            y = -30 * np.sin(np.pi - angle) - 60
            self.teeth.append(ToothState(numero=num, pos_x=x, pos_y=y))

    def to_feature_vector(self) -> np.ndarray:
        """Converte o gêmeo digital completo em vetor de características.

        Returns:
            ndarray (32 * 8 + 4) = 260 elementos
                32 dentes x 8 variáveis + 4 variáveis globais
        """
        teeth_features = [t.to_vector() for t in self.teeth]
        teeth_array = np.array(teeth_features).flatten()
        global_features = np.array([
            self.periodontal_stage / 5.0,
            self.hygiene_index / 5.0,
            self.bone_density / 100.0,
            len(self.teeth) / 32.0,
        ])
        return np.concatenate([teeth_array, global_features])

    def apply_intervention(self, intervention: dict) -> DentalTwin:
        """Aplica uma intervenção odontológica simulada ao gêmeo digital.

        Args:
            intervention: Dicionário descrevendo a intervenção
                Ex::
                    {"tipo": "restauracao", "dentes": [11, 12, 16]}
                    {"tipo": "exodontia", "dentes": [18, 28]}
                    {"tipo": "periodontal", "tratamento": "raspagem"}

        Returns:
            Novo DentalTwin com as alterações aplicadas

        Raises:
            ValueError: Se a intervenção for inválida ou o dente não existir
        """
        twin_new = DentalTwin(
            patient_id=self.patient_id,
            periodontal_stage=self.periodontal_stage,
            hygiene_index=self.hygiene_index,
            bone_density=self.bone_density,
        )

        # Copia dentes
        teeth_map = {t.numero: t for t in self.teeth}
        twin_new.teeth = []
        for t in self.teeth:
            twin_new.teeth.append(ToothState(
                numero=t.numero,
                saudavel=t.saudavel,
                carie=t.carie,
                restaurado=t.restaurado,
                lesao_periapical=t.lesao_periapical,
                fratura=t.fratura,
                mobilidade=t.mobilidade,
                profundidade_sondagem=t.profundidade_sondagem,
                perda_ossea=t.perda_ossea,
                pos_x=t.pos_x,
                pos_y=t.pos_y,
            ))

        intervention_type = intervention.get("tipo", "")

        if intervention_type == "restauracao":
            for num in intervention.get("dentes", []):
                if num in teeth_map:
                    t = twin_new._find_teeth_by_number(num)
                    if t is not None:
                        t.restaurado = True
                        t.carie = True
        elif intervention_type == "exodontia":
            for num in intervention.get("dentes", []):
                if num in teeth_map:
                    # Remove o dente da lista
                    twin_new.teeth = [t for t in twin_new.teeth if t.numero != num]
        elif intervention_type == "endodontia":
            for num in intervention.get("dentes", []):
                t = twin_new._find_teeth_by_number(num)
                if t is not None:
                    t.lesao_periapical = False
                    t.restaurado = True
        elif intervention_type == "periodontal":
            # Melhora os parâmetros periodontais
            twin_new.periodontal_stage = max(0, self.periodontal_stage - 1)
            for t in twin_new.teeth:
                t.profundidade_sondagem = max(2.0, t.profundidade_sondagem - 1.0)
                t.mobilidade = max(0, t.mobilidade - 1)
        elif intervention_type == "higiene":
            twin_new.hygiene_index = max(0, self.hygiene_index - 2.0)
        else:
            raise ValueError(f"Tipo de intervenção '{intervention_type}' não reconhecido")

        twin_new.metadata["ultima_intervencao"] = intervention
        return twin_new

    def _find_teeth_by_number(self, numero: int) -> Optional[ToothState]:
        """Retorna dente pelo número FDI."""
        for t in self.teeth:
            if t.numero == numero:
                return t
        return None


# =============================================================================
# Encoder de gêmeo digital (autoencoder simplificado)
# =============================================================================


class TwinEncoder(nn.Module):
    """Autoencoder simplificado para representação latente de gêmeos digitais.

    Codifica o estado dental do paciente (260 features) em um espaço
    latente de dimensão reduzida (64 por padrão) e reconstrói.

    Útil para:
        - Agrupar pacientes por similaridade de condição
        - Detectar anomalias em comparação com a população
        - Visualizar evolução no espaço latente

    Args:
        input_dim: Dimensão do vetor de entrada (padrão 260)
        latent_dim: Dimensão do espaço latente (padrão 32)
        hidden_dim: Dimensão das camadas ocultas (padrão 128)

    Example:
        >>> encoder = TwinEncoder(input_dim=260, latent_dim=32)
        >>> x = torch.randn(4, 260)
        >>> z, x_recon = encoder(x)
        >>> z.shape  # espaço latente
        torch.Size([4, 32])
    """

    def __init__(
        self,
        input_dim: int = 260,
        latent_dim: int = 32,
        hidden_dim: int = 128,
    ):
        super().__init__()

        # Encoder
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, latent_dim),
        )

        # Decoder
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, input_dim),
            nn.Sigmoid(),  # Reconstrói em [0, 1]
        )

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward: codifica e decodifica.

        Args:
            x: Tensor (B, input_dim)

        Returns:
            latent: Tensor (B, latent_dim)
            reconst: Tensor (B, input_dim)
        """
        latent = self.encoder(x)
        reconst = self.decoder(latent)
        return latent, reconst


def build_twin_encoder(latent_dim: int = 32, input_dim: int = 260) -> nn.Module:
    """Constrói um autoencoder para representação compacta de gêmeos digitais.

    Args:
        latent_dim: Dimensão do espaço latente (padrão 32)
        input_dim: Dimensão da entrada (260 para 32 dentes + variáveis globais)

    Returns:
        Modelo TwinEncoder não-treinado

    Example:
        >>> encoder = build_twin_encoder(latent_dim=16)
        >>> x = torch.randn(4, 260)
        >>> z, _ = encoder(x)
        >>> z.shape
        torch.Size([4, 16])
    """
    return TwinEncoder(input_dim=input_dim, latent_dim=latent_dim)


def estimate_intervention(
    twin: DentalTwin,
    intervention: dict,
) -> Dict:
    """Estima o resultado de uma intervenção odontológica simulada.

    Args:
        twin: DentalTwin do paciente atual
        intervention: Dicionário da intervenção (ver DentalTwin.apply_intervention)

    Returns:
        Dicionário com diagnóstico pré, intervenção e prognóstico pós

    Example:
        >>> twin = DentalTwin(patient_id="P001")
        >>> result = estimate_intervention(twin, {"tipo": "higiene"})
        >>> print(result["prognostico"]["hygiene_index"])
        1.0
    """
    twin_post = twin.apply_intervention(intervention)

    return {
        "diagnostico_pre": {
            "periodontal_stage": twin.periodontal_stage,
            "hygiene_index": twin.hygiene_index,
            "dentes_comprometidos": sum(
                1 for t in twin.teeth if not t.saudavel
            ),
        },
        "intervencao": intervention,
        "prognostico": {
            "periodontal_stage": twin_post.periodontal_stage,
            "hygiene_index": twin_post.hygiene_index,
            "dentes_comprometidos": sum(
                1 for t in twin_post.teeth if not t.saudavel
            ),
        },
        "melhora": twin.hygiene_index > twin_post.hygiene_index
        or twin.periodontal_stage > twin_post.periodontal_stage,
    }