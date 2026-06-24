"""Détection des modules dans une image drone.

Interface stable et branchable. L'implémentation réelle est un **YOLOv8**
entraîné sur des frames de centrales annotées (données à fournir par le terrain).
Tant qu'aucun poids n'est fourni, le détecteur considère que l'image reçue est
déjà un module unique recadré (cas du dataset de vignettes) — aucune invention.
"""
from PIL import Image


class ModuleDetector:
    def __init__(self, weights: str | None = None):
        self.weights = weights
        self.model = None
        if weights:
            from ultralytics import YOLO  # dépendance optionnelle
            self.model = YOLO(weights)

    def detect(self, img: Image.Image):
        """Retourne une liste de modules : [{'bbox': (x1,y1,x2,y2), 'crop': Image}]."""
        if self.model is None:
            return [{'bbox': (0, 0, img.width, img.height), 'crop': img}]

        out = []
        for box in self.model(img)[0].boxes.xyxy.tolist():
            x1, y1, x2, y2 = map(int, box)
            out.append({'bbox': (x1, y1, x2, y2), 'crop': img.crop((x1, y1, x2, y2))})
        return out
