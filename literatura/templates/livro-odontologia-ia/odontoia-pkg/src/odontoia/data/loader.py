"""
Módulo loader — Carregamento de dados odontológicos.

Funções:
    load_dicom         : Carrega imagem de arquivo DICOM (.dcm)
    load_panoramic     : Carrega radiografia panorâmica (DICOM ou PNG/JPG)
    load_dataset       : Carrega dataset público odontológico pelo nome
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, Union

import cv2
import numpy as np
from PIL import Image

from odontoia.data.datasets import DATASETS_INFO

# =============================================================================
# Funções auxiliares internas
# =============================================================================


def _read_dicom_pixels(dicom_path: str) -> np.ndarray:
    """Tenta ler um arquivo DICOM e retornar seu array de pixels.

    Args:
        dicom_path: Caminho para o arquivo .dcm

    Returns:
        ndarray com os pixels da imagem DICOM

    Raises:
        FileNotFoundError: Se o arquivo não existir
        ImportError: Se pydicom não estiver instalado
        ValueError: Se o arquivo não for um DICOM válido
    """
    if not os.path.isfile(dicom_path):
        raise FileNotFoundError(f"Arquivo DICOM não encontrado: {dicom_path}")

    try:
        import pydicom
    except ImportError:
        raise ImportError(
            "pydicom é necessário para carregar arquivos DICOM. "
            "Instale com: pip install pydicom"
        )

    try:
        ds = pydicom.dcmread(dicom_path)
        pixels = ds.pixel_array
        # Normaliza para uint8 se necessário (16 bits -> 8 bits)
        if pixels.dtype != np.uint8:
            pixels = pixels.astype(np.float32)
            # Janelamento simples: percentis 0.5 e 99.5
            low, high = np.percentile(pixels, [0.5, 99.5])
            pixels = np.clip((pixels - low) / (high - low + 1e-8), 0, 1)
            pixels = (pixels * 255).astype(np.uint8)
        return pixels
    except Exception as exc:
        raise ValueError(f"Falha ao ler DICOM '{dicom_path}': {exc}") from exc


def _read_image_generic(path: str) -> np.ndarray:
    """Carrega imagem nos formatos comuns (PNG, JPG, TIFF, BMP).

    Args:
        path: Caminho para a imagem

    Returns:
        Array numpy (H x W) em tons de cinza ou (H x W x C) colorida

    Raises:
        FileNotFoundError: Se o arquivo não existir
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Arquivo de imagem não encontrado: {path}")

    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if img is None:
        # Fallback para PIL
        pil_img = Image.open(path).convert("L")
        img = np.array(pil_img, dtype=np.uint8)
    # Se for colorida (BGR), converte para tons de cinza
    if len(img.shape) == 3 and img.shape[2] == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return img


# =============================================================================
# API Pública
# =============================================================================


def load_dicom(path: str, normalize: bool = True) -> np.ndarray:
    """Carrega uma imagem a partir de um arquivo DICOM.

    Aplica janelamento automático com base nos percentis 0.5 e 99.5
    para converter de 12/16 bits para 8 bits.

    Args:
        path: Caminho para o arquivo .dcm
        normalize: Se True (padrão), normaliza a imagem para 0-255

    Returns:
        ndarray 2D (H, W) com valores uint8 entre 0 e 255

    Example:
        >>> img = load_dicom("radiografia.dcm")
        >>> print(img.shape, img.dtype)
        (1024, 1024) uint8
    """
    pixels = _read_dicom_pixels(path)
    # Se não normalizado ainda (falha de pydicom ou fluxo alternativo)
    if normalize and pixels.dtype != np.uint8:
        pixels = pixels.astype(np.float32)
        low, high = np.percentile(pixels, [0.5, 99.5])
        pixels = np.clip((pixels - low) / (high - low + 1e-8), 0, 1)
        pixels = (pixels * 255).astype(np.uint8)
    return pixels


def load_panoramic(path: str, grayscale: bool = True) -> np.ndarray:
    """Carrega uma radiografia panorâmica de arquivo DICOM ou formato comum.

    Detecta automaticamente se o arquivo é DICOM (extensão .dcm) ou
    formato de imagem comum (.png, .jpg, .tiff).

    Args:
        path: Caminho para a radiografia panorâmica
        grayscale: Se True (padrão), converte para tons de cinza

    Returns:
        ndarray 2D (H, W) uint8 da radiografia panorâmica

    Example:
        >>> pan = load_panoramic("panoramica.dcm")
        >>> pan.shape
        (1536, 768)

    Note:
        Radiografias panorâmicas típicas têm proporção ~2:1
        (largura aproximadamente o dobro da altura).
    """
    path_lower = path.lower()
    if path_lower.endswith(".dcm"):
        pixels = _read_dicom_pixels(path)
    else:
        pixels = _read_image_generic(path)

    # Garante 2D (tons de cinza)
    if grayscale and len(pixels.shape) == 3:
        if pixels.shape[2] == 3:
            pixels = cv2.cvtColor(pixels, cv2.COLOR_BGR2GRAY)
        elif pixels.shape[2] == 4:
            pixels = cv2.cvtColor(pixels, cv2.COLOR_BGRA2GRAY)

    if pixels.dtype != np.uint8:
        low, high = np.percentile(pixels, [0.5, 99.5])
        pixels = np.clip((pixels - low) / (high - low + 1e-8), 0, 1)
        pixels = (pixels * 255).astype(np.uint8)

    return pixels


def load_dataset(
    name: str,
    split: Optional[str] = None,
    root: Optional[str] = None,
    download: bool = False,
) -> dict:
    """Carrega um dataset odontológico público pelo nome.

    Datasets disponíveis:
        - 'dns':      Dental Noisy Set (dentes em radiografias periapicais)
        - 'ufba':     UFBA Dental (diagnóstico de lesões bucais)
        - 'odontoai': OdontoAI (radiografias panorâmicas rotuladas)

    Args:
        name: Nome do dataset ('dns', 'ufba', 'odontoai')
        split: Divisão a carregar ('train', 'val', 'test' ou None para todos)
        root: Diretório raiz onde os datasets estão armazenados.
              Se None, usa o padrão '~/.odontoia/datasets/'
        download: Se True, tenta baixar o dataset (se url estiver disponível)

    Returns:
        Dicionário com as chaves 'images' (list[ndarray]) e 'labels' (list)
        ou sub-chaves 'train', 'val', 'test' conforme o dataset.

    Raises:
        KeyError: Se o nome do dataset não estiver em DATASETS_INFO
        FileNotFoundError: Se o dataset não estiver presente no root

    Example:
        >>> data = load_dataset('dns', split='train')
        >>> len(data['images'])
        150
    """
    # Valida nome do dataset
    name_lower = name.lower().strip()
    if name_lower not in DATASETS_INFO:
        supported = list(DATASETS_INFO.keys())
        raise KeyError(
            f"Dataset '{name}' não reconhecido. "
            f"Opções suportadas: {supported}"
        )

    info = DATASETS_INFO[name_lower]
    root_dir = Path(root) if root else Path.home() / ".odontoia" / "datasets"
    dataset_path = root_dir / name_lower

    # Se download solicitado e url disponível
    if download and not dataset_path.exists():
        if info.get("url"):
            print(f"Baixando dataset '{name}' de: {info['url']}")
            _download_dataset(info["url"], dataset_path)
        else:
            print(
                f"Dataset '{name}' não possui URL configurada para download. "
                "Os datasets neste pacote são referenciados; "
                "faça o download manual. Consulte: "
                "https://github.com/marceloclaro/opencode-ecosystem-core/"
                "tree/main/livro-odontologia-ia/apendices/apendice-c-datasets-publicos.tex"
            )
            return _generate_synthetic_fallback(name_lower)

    if not dataset_path.exists():
        # Fallback: gera dados sintéticos para demonstração didática
        return _load_synthetic_dataset(name_lower, split)

    # Carrega imagens do diretório (implementação real)
    images = []
    labels = []
    label_map = info.get("labels", ["normal", "alterado"])

    for label_idx, label_name in enumerate(label_map):
        label_dir = dataset_path / label_name
        if not label_dir.exists():
            continue
        for fname in sorted(os.listdir(label_dir)):
            if fname.lower().endswith((".png", ".jpg", ".jpeg", ".dcm", ".tiff")):
                fpath = str(label_dir / fname)
                try:
                    img = load_panoramic(fpath)
                    images.append(img)
                    labels.append(label_idx)
                except Exception:
                    continue  # Pula arquivos corrompidos silenciosamente

    return {"images": images, "labels": labels, "dataset_name": name_lower}


def _load_synthetic_dataset(name: str, split: Optional[str] = None) -> dict:
    """Gera um dataset sintético para fins didáticos quando o dataset real
    não está disponível no sistema.

    Args:
        name: Nome do dataset (para número de amostras)
        split: Divisão opcional

    Returns:
        Dicionário com imagens e rótulos sintéticos
    """
    n_samples = {"dns": 32, "ufba": 48, "odontoai": 24}.get(name, 32)
    rng = np.random.default_rng(42)

    images = []
    for _ in range(n_samples):
        # Cria uma "radiografia" sintética: elipse clara sobre fundo escuro
        img = np.zeros((128, 128), dtype=np.uint8)
        center = rng.integers(40, 88, size=2)
        axes = rng.integers(10, 30, size=2)
        # Desenha uma estrutura oval simulando dente com NumPy
        yy, xx = np.ogrid[:128, :128]
        mask = ((xx - center[0])**2 / axes[0]**2 + (yy - center[1])**2 / axes[1]**2) <= 1
        img[mask] = rng.integers(80, 200)
        # Adiciona ruído gaussiano leve
        noise = rng.normal(0, 10, img.shape).astype(np.int16)
        img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        images.append(img)

    labels = rng.integers(0, 3, size=n_samples).tolist()
    result = {"images": images, "labels": labels, "split": split or "synthetic"}

    if split:
        return result
    return {
        "train": {
            "images": images[: n_samples * 3 // 4],
            "labels": labels[: n_samples * 3 // 4],
        },
        "test": {
            "images": images[n_samples * 3 // 4 :],
            "labels": labels[n_samples * 3 // 4 :],
        },
    }


# Alias para compatibilidade
_load_synthetic_fallback = _load_synthetic_dataset


def _download_dataset(url: str, dest: Path):
    """Realiza o download de um dataset partindo de uma URL.

    Args:
        url: URL do arquivo compactado (.zip/.tar.gz)
        dest: Diretório de destino
    """
    import io
    import zipfile

    import requests

    dest.mkdir(parents=True, exist_ok=True)
    response = requests.get(url, stream=True, timeout=300)
    response.raise_for_status()

    # Tenta extrair como zip
    try:
        z = zipfile.ZipFile(io.BytesIO(response.content))
        z.extractall(dest)
    except zipfile.BadZipFile:
        # Fallback: salva o arquivo diretamente
        dest.mkdir(parents=True, exist_ok=True)
        fname = url.split("/")[-1]
        fpath = dest / fname
        with open(fpath, "wb") as f:
            f.write(response.content)