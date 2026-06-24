"""Pipeline d'inspection — la chaîne réelle, prête pour des images drone.

  image(s) drone  →  détection des modules  →  classification
                  →  géoréférencement EXIF  →  sévérité / perte  →  base

Aucune donnée inventée : le GPS provient de l'EXIF (None si absent), la classe
du modèle, la sévérité du barème métier. Quand un détecteur YOLO entraîné et de
vraies frames arrivent, on les branche sans toucher au reste.
"""
from pathlib import Path

from PIL import Image

from core.geo import extract_gps
from core.classifier import classify
from core.severity import assess
from core.detector import ModuleDetector
from core import db

NORMAL = 'No-Anomaly'


def process_images(paths, inspection_name='Inspection', detector=None,
                   module_wp=400, specific_yield=1600, price_eur_kwh=0.10):
    """Traite une liste d'images, stocke une inspection en base, renvoie (id, panneaux)."""
    detector = detector or ModuleDetector()
    panels = []

    for path in paths:
        path = Path(path)
        img = Image.open(path)
        gps = extract_gps(path)                      # GPS RÉEL (EXIF) ou None
        for det in detector.detect(img):
            classe, conf = classify(det['crop'].convert('RGB'))
            sev = assess(classe, module_wp, specific_yield, price_eur_kwh)
            panels.append({
                'source': path.name,
                'lat': gps[0] if gps else None,
                'lon': gps[1] if gps else None,
                'classe': classe,
                'confiance': round(conf, 4),
                'anomalie': int(classe != NORMAL),
                **sev,
            })

    db.init_db()
    inspection_id = db.create_inspection(inspection_name, panels)
    return inspection_id, panels
