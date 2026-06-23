"""Modèle de classification — ResNet-18 en transfer learning."""
import torch.nn as nn
from torchvision import models


def build_model(num_classes=12, pretrained=True):
    """ResNet-18 (poids ImageNet) avec une tête de classification à `num_classes` sorties."""
    weights = models.ResNet18_Weights.DEFAULT if pretrained else None
    model = models.resnet18(weights=weights)
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    return model
