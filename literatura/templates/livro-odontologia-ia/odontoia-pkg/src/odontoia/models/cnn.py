"""
Módulo cnn — Modelos de Redes Neurais Convolucionais para classificação
de imagens odontológicas.

Funções:
    build_simple_cnn          : CNN simples didática (2-3 camadas convolucionais)
    build_resnet50_finetune  : Transfer Learning com ResNet50
    predict_with_explanation : Predição com mapa de ativação Grad-CAM acoplado
"""

from __future__ import annotations

from typing import Optional, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


# =============================================================================
# Modelo CNN Didático — "OdontoCNN"
# =============================================================================


class OdontoCNN(nn.Module):
    """CNN simples e didática para classificação de radiografias odontológicas.

    Arquitetura:
        - 2 camadas convolucionais com BatchNorm e MaxPooling
        - 1 camada densa oculta com Dropout
        - Camada de saída softmax

    Args:
        input_shape: Tupla (C, H, W) — canais, altura, largura
        n_classes: Número de classes de saída

    Example:
        >>> model = OdontoCNN(input_shape=(1, 128, 128), n_classes=3)
        >>> x = torch.randn(4, 1, 128, 128)
        >>> y = model(x)
        >>> y.shape
        torch.Size([4, 3])
    """

    def __init__(self, input_shape: Tuple[int, int, int], n_classes: int):
        super().__init__()
        C, H, W = input_shape

        # Bloco convolucional 1: extrai features de baixo nível
        self.conv1 = nn.Conv2d(C, 32, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(32)
        self.pool1 = nn.MaxPool2d(2)  # reduz resolução pela metade

        # Bloco convolucional 2: extrai features de alto nível
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(64)
        self.pool2 = nn.MaxPool2d(2)

        # Bloco convolucional 3 (opcional): features mais abstratas
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm2d(128)
        self.pool3 = nn.MaxPool2d(2)

        # Calcula o tamanho do tensor achatado após as convoluções
        # Após 3 pools com fator 2: H/8, W/8
        self._feature_h = H // 8
        self._feature_w = W // 8
        self._flattened_size = 128 * self._feature_h * self._feature_w

        # Classificador denso
        self.dropout = nn.Dropout(0.5)
        self.fc1 = nn.Linear(self._flattened_size, 128)
        self.fc2 = nn.Linear(128, n_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass da CNN.

        Args:
            x: Tensor de entrada (B, C, H, W)

        Returns:
            Tensor de saída (B, n_classes) com logits
        """
        # Bloco 1
        x = self.pool1(F.relu(self.bn1(self.conv1(x))))
        # Bloco 2
        x = self.pool2(F.relu(self.bn2(self.conv2(x))))
        # Bloco 3
        x = self.pool3(F.relu(self.bn3(self.conv3(x))))

        # Flatten para o classificador
        x = x.view(x.size(0), -1)

        # Classificador denso
        x = self.dropout(F.relu(self.fc1(x)))
        x = self.fc2(x)  # logits
        return x


# =============================================================================
# ResNet50 Finetune (Transfer Learning)
# =============================================================================


class ResNet50Finetune(nn.Module):
    """Modelo de Transfer Learning usando ResNet50 pré-treinada no ImageNet

    Adaptada para classificação de radiografias odontológicas:
        - Substitui a última camada fully connected
        - Aceita 1 canal (tons de cinza) repetido para 3 canais
        - Congela camadas iniciais opcionalmente

    Args:
        n_classes: Número de classes odontológicas
        freeze_backbone: Se True (padrão), congela pesos do ResNet50

    Example:
        >>> model = ResNet50Finetune(n_classes=5)
        >>> x = torch.randn(2, 1, 224, 224)  # radiografia em tons de cinza
        >>> y = model(x)
        >>> y.shape
        torch.Size([2, 5])
    """

    def __init__(self, n_classes: int, freeze_backbone: bool = True):
        from torchvision.models import resnet50, ResNet50_Weights

        super().__init__()
        # Carrega ResNet50 pré-treinada
        weights = ResNet50_Weights.IMAGENET1K_V2
        self.backbone = resnet50(weights=weights)

        # Modifica primeira convolução para aceitar 1 canal (radiografia)
        # Repete o peso médio dos 3 canais RGB para o único canal
        original_conv = self.backbone.conv1
        self.backbone.conv1 = nn.Conv2d(
            1,
            original_conv.out_channels,
            kernel_size=original_conv.kernel_size,
            stride=original_conv.stride,
            padding=original_conv.padding,
            bias=False,
        )
        with torch.no_grad():
            # Média dos pesos RGB -> peso único para tons de cinza
            self.backbone.conv1.weight.data = original_conv.weight.data.mean(
                dim=1, keepdim=True
            )

        # Congela backbone se solicitado
        if freeze_backbone:
            for param in self.backbone.parameters():
                param.requires_grad = False
            # Descongela a última camada (layer4) para fine-tuning parcial
            for param in self.backbone.layer4.parameters():
                param.requires_grad = True

        # Substitui o classificador final
        in_features = self.backbone.fc.in_features
        self.backbone.fc = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(in_features, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, n_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass: entrada monocromática, saída logits por classe."""
        return self.backbone(x)


# =============================================================================
# Funções de alto nível
# =============================================================================


def build_simple_cnn(
    input_shape: Tuple[int, int, int],
    n_classes: int,
    pretrained: bool = False,
) -> torch.nn.Module:
    """Constrói uma CNN simples para classificação de imagens odontológicas.

    Esta função é a interface de alto nível recomendada para o Capítulo 5
    do livro (CNNs para Diagnóstico Bucal).

    Args:
        input_shape: Shape da imagem (C, H, W)
            Ex: (1, 128, 128) para radiografias em tons de cinza
        n_classes: Número de classes odontológicas
            Ex: 3 para (saudável, cárie, lesão periapical)
        pretrained: Se True, usa ResNet50 finetune em vez da CNN simples

    Returns:
        Modelo PyTorch pronto para treinamento

    Example:
        >>> model = build_simple_cnn((1, 256, 256), n_classes=3)
        >>> print(sum(p.numel() for p in model.parameters()))
        1234567  # número de parâmetros
    """
    if pretrained:
        model = ResNet50Finetune(n_classes=n_classes)
    else:
        model = OdontoCNN(input_shape=input_shape, n_classes=n_classes)
    return model


def build_resnet50_finetune(
    n_classes: int,
    freeze_backbone: bool = True,
) -> torch.nn.Module:
    """Constrói modelo ResNet50 com fine-tuning para diagnóstico odontológico.

    Args:
        n_classes: Número de classes alvo (ex: 6 para lesões bucais)
        freeze_backbone: Congela pesos do ImageNet nas camadas iniciais

    Returns:
        Modelo ResNet50 adaptado para radiografias odontológicas

    Example:
        >>> model = build_resnet50_finetune(n_classes=6)
    """
    return ResNet50Finetune(n_classes=n_classes, freeze_backbone=freeze_backbone)


def predict_with_explanation(
    model: torch.nn.Module,
    img_tensor: torch.Tensor,
    device: Optional[torch.device] = None,
) -> Tuple[int, np.ndarray, float]:
    """Realiza predição com mapa de ativação Grad-CAM para explicabilidade.

    A função retorna:
        1. Classe predita (índice)
        2. Mapa de calor Grad-CAM (H, W) para visualização
        3. Score de confiança da predição

    Args:
        model: Modelo treinado (com .features ou hook para gradientes)
        img_tensor: Tensor da imagem (1, C, H, W) normalizado
        device: Device para inferência (CPU/GPU)

    Returns:
        Tupla (classe_idx, gradcam_map, confidence)

    Example:
        >>> from odontoia.preprocessing import to_tensor
        >>> model = build_simple_cnn((1, 256, 256), n_classes=3)
        >>> img_tensor = to_tensor(img, add_batch=True)
        >>> cls_idx, heatmap, conf = predict_with_explanation(model, img_tensor)
    """
    _model = None
    if device is not None:
        _model = model.to(device)
        img_tensor = img_tensor.to(device)
    else:
        _model = model

    # Modo avaliação
    _model.eval()

    # Registra hook para capturar gradientes da última camada convolucional
    gradients = []
    activations = []

    def forward_hook(module, input_, output):
        activations.append(output)

    def backward_hook(module, grad_input, grad_output):
        gradients.append(grad_output[0])

    # Encontra a última camada Conv2d do modelo
    last_conv = None
    for module in _model.modules():
        if isinstance(module, nn.Conv2d):
            last_conv = module

    if last_conv is not None:
        hook_forward = last_conv.register_forward_hook(forward_hook)
        hook_backward = last_conv.register_full_backward_hook(backward_hook)

    # Forward
    with torch.set_grad_enabled(True):
        output = _model(img_tensor)
        pred_class = output.argmax(dim=1).item()
        confidence = torch.softmax(output, dim=1)[0, pred_class].item()

        if last_conv is not None:
            # Backward para obter gradientes
            _model.zero_grad()
            output[0, pred_class].backward()

            # Grad-CAM: pondera os mapas de ativação pelos gradientes globais
            if len(gradients) > 0 and len(activations) > 0:
                grads = gradients[0].squeeze(0)  # (C, H, W)
                acts = activations[0].squeeze(0)  # (C, H, W)
                weights = grads.mean(dim=(1, 2), keepdim=True)  # (C, 1, 1)
                cam = (acts * weights).sum(dim=0)  # (H, W)
                cam = F.relu(cam)  # ReLU: só regiões positivas
                cam = cam.detach().cpu().numpy()

                # Normaliza para [0, 1]
                if cam.max() > 0:
                    cam = cam / cam.max()
                heatmap = cam
            else:
                heatmap = np.zeros((img_tensor.shape[2], img_tensor.shape[3]))
        else:
            heatmap = np.zeros((img_tensor.shape[2], img_tensor.shape[3]))

    # Limpa hooks
    if last_conv is not None and "hook_forward" in dir():
        hook_forward.remove()
        hook_backward.remove()

    return pred_class, heatmap, pred



def get_last_conv_layer(model: nn.Module) -> Optional[nn.Module]:
    """Retorna a última camada convolucional do modelo.

    Args:
        model: Modelo PyTorch qualquer

    Returns:
        Último módulo Conv2d encontrado, ou None
    """
    last_conv = None
    for module in model.modules():
        if isinstance(module, nn.Conv2d):
            last_conv = module
    return last_conv