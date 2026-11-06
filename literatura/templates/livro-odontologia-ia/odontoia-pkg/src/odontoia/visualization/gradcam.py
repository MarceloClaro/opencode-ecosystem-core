"""
Módulo gradcam — Visualização de mapas de ativação Grad-CAM para
explicabilidade de modelos CNN em diagnóstico odontológico.

Funções:
    plot_gradcam : Gera heatmap Grad-CAM sobreposto à radiografia
"""

from __future__ import annotations

from typing import Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn.functional as F


def plot_gradcam(
    model: torch.nn.Module,
    img_tensor: torch.Tensor,
    target_class: Optional[int] = None,
    alpha: float = 0.5,
    cmap: str = "jet",
    figsize: Tuple[int, int] = (12, 5),
    title: Optional[str] = None,
    device: Optional[torch.device] = None,
) -> np.ndarray:
    """Gera e plota o mapa de ativação Grad-CAM sobre a imagem original.

    O Grad-CAM (Gradient-weighted Class Activation Mapping) destaca as
    regiões da radiografia que mais contribuíram para a decisão do modelo,
    permitindo interpretabilidade clínica.

    Args:
        model: Modelo PyTorch treinado (com ao menos uma camada Conv2d)
        img_tensor: Tensor da imagem (1, C, H, W) normalizado [0,1]
        target_class: Classe alvo para o mapa. Se None, usa a classe predita
        alpha: Peso da sobreposição do heatmap (0=só imagem, 1=só mapa)
        cmap: Mapa de cores matplotlib para o heatmap (padrão 'jet')
        figsize: Tamanho da figura (largura, altura)
        show: Se True, exibe o gráfico (plt.show())
        device: Device para inferência (None = CPU)

    Returns:
        ndarray (H, W) do heatmap Grad-CAM normalizado [0, 1]

    Example:
        >>> from odontoia.data.preprocessing import load_panoramic, to_tensor
        >>> from odontoia.models.cnn import build_simple_cnn
        >>> model = build_simple_cnn((1, 256, 256), n_classes=3)
        >>> img = load_panoramic("panoramica.dcm")
        >>> img = resize_with_aspect(img, 256)
        >>> tensor = to_tensor(img, add_batch=True)
        >>> heatmap = plot_gradcam(model, tensor, target_class=1)
    """
    if device is not None:
        model = model.to(device)
        img_tensor = img_tensor.to(device)

    model.eval()

    # Encontra a última camada convolucional
    target_layer = None
    for module in model.modules():
        if isinstance(module, torch.nn.Conv2d):
            target_layer = module

    if target_layer is None:
        raise ValueError(
            "Modelo não possui camadas Conv2d. "
            "Grad-CAM requer ao menos uma convolução."
        )

    # Arrays para armazenar ativações e gradientes
    activations = []
    gradients = []

    def forward_hook(module, input_, output):
        activations.append(output.detach())

    def backward_hook(module, grad_input, grad_output):
        gradients.append(grad_output[0].detach())

    hook_forward = target_layer.register_forward_hook(forward_hook)
    hook_backward = target_layer.register_full_backward_hook(backward_hook)

    # Forward
    with torch.set_grad_enabled(True):
        output = model(img_tensor)

        if target_class is None:
            target_class = output.argmax(dim=1).item()

        # Zera gradientes e faz backward para a classe alvo
        model.zero_grad()
        one_hot = torch.zeros_like(output)
        one_hot[0, target_class] = 1
        output.backward(gradient=one_hot)

    # Remove hooks
    hook_forward.remove()
    hook_backward.remove()

    # Constrói o mapa Grad-CAM
    if len(gradients) > 0 and len(activations) > 0:
        grads = gradients[0].squeeze(0)  # (C, H, W)
        acts = activations[0].squeeze(0)  # (C, H, W)

        # Pesos globais: média dos gradientes por canal
        weights = grads.mean(dim=(1, 2), keepdim=True)  # (C, 1, 1)

        # Combinação linear: soma ponderada das ativações
        cam = (acts * weights).sum(dim=0)  # (H, W)
        cam = F.relu(cam)  # ReLU: preserva só regiões positivas
        cam = cam.cpu().numpy()

        # Normaliza para [0, 1]
        if cam.max() > 0:
            cam = cam / cam.max()
        else:
            cam = np.zeros_like(cam)
    else:
        cam = np.zeros((img_tensor.shape[2], img_tensor.shape[3]))

    # Redimensiona ao tamanho original da imagem se necessário
    orig_h, orig_w = img_tensor.shape[2], img_tensor.shape[3]
    if cam.shape != (orig_h, orig_w):
        from skimage.transform import resize
        cam = resize(cam, (orig_h, orig_w), preserve_range=True, mode="reflect")

    # Prepara visualização
    img_disp = img_tensor.cpu().squeeze(0).numpy()
    if img_disp.shape[0] == 1:
        img_disp = img_disp.squeeze(0)

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=figsize)

    # Imagem original
    ax1.imshow(img_disp, cmap="gray")
    ax1.set_title("Radiografia Original", fontsize=12)
    ax1.axis("off")

    # Heatmap Grad-CAM
    ax2.imshow(cam, cmap=cmap, interpolation="bilinear")
    ax2.set_title(f"Grad-CAM (Classe {target_class})", fontsize=12)
    ax2.axis("off")

    # Sobreposição
    ax3.imshow(img_disp, cmap="gray")
    ax3.imshow(cam, cmap=cmap, alpha=alpha, interpolation="bilinear")
    ax3.set_title("Sobreposição", fontsize=12)
    ax3.axis("off")

    if title:
        fig.suptitle(title, fontsize=14, fontweight="bold")

    plt.tight_layout()
    plt.show()

    # Retorna o heatmap para uso posterior
    return cam