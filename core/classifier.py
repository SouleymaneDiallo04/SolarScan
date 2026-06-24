"""Inférence du modèle de classification d'anomalies thermiques (réutilisable)."""
import json
from pathlib import Path

import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
DEVICE = 'cpu'

with open(ROOT / 'classes.json', encoding='utf-8') as f:
    CLASSES = json.load(f)

_model = models.resnet18()
_model.fc = nn.Linear(_model.fc.in_features, len(CLASSES))
_model.load_state_dict(torch.load(ROOT / 'solarscan_resnet18.pt', map_location=DEVICE))
_model.eval()

_tf = transforms.Compose([
    transforms.Grayscale(3), transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])


def classify(img: Image.Image):
    """Retourne (classe, confiance) pour l'image d'un module."""
    x = _tf(img).unsqueeze(0)
    with torch.no_grad():
        probs = torch.softmax(_model(x), 1)[0]
    idx = int(probs.argmax())
    return CLASSES[idx], float(probs[idx])
