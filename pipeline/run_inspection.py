"""SolarScan — pipeline d'inspection (simulation d'un vol drone sur une centrale).

Prend un lot d'images thermiques de modules, les classe, les dispose sur une
grille (la centrale), leur attribue des coordonnées GPS, et produit :
  - reports/report.csv     une ligne par panneau (position, GPS, état, type)
  - reports/plant_map.png  carte de la centrale (panneaux coloriés par état)

Exemple :
    py pipeline/inspect.py --n 200 --rows 10
"""
import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import matplotlib.patches as mpatches

import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
DEVICE = 'cpu'
NORMAL_CLASS = 'No-Anomaly'

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


def classify(path: Path):
    x = _tf(Image.open(path)).unsqueeze(0)
    with torch.no_grad():
        probs = torch.softmax(_model(x), 1)[0]
    idx = int(probs.argmax())
    return CLASSES[idx], float(probs[idx]), CLASSES[idx] != NORMAL_CLASS


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--images_dir', default=str(ROOT / 'data' / 'images'))
    ap.add_argument('--n', type=int, default=200, help='nombre de panneaux survoles')
    ap.add_argument('--rows', type=int, default=10, help='rangees de la centrale')
    ap.add_argument('--base_lat', type=float, default=32.2230, help='coin de la centrale (Benguerir)')
    ap.add_argument('--base_lon', type=float, default=-7.9540)
    ap.add_argument('--spacing_m', type=float, default=2.0, help='espacement entre panneaux (m)')
    args = ap.parse_args()

    images = sorted(Path(args.images_dir).glob('*.jpg'))[:args.n]
    cols = math.ceil(len(images) / args.rows)
    d_lat = args.spacing_m / 111320.0
    d_lon = args.spacing_m / (111320.0 * math.cos(math.radians(args.base_lat)))

    out = ROOT / 'reports'
    out.mkdir(exist_ok=True)
    grid = np.full((args.rows, cols), np.nan)
    records = []

    print(f'Inspection de {len(images)} panneaux ({args.rows} x {cols})...')
    for k, path in enumerate(images):
        row, col = k // cols, k % cols
        classe, conf, anomalie = classify(path)
        grid[row, col] = 1.0 if anomalie else 0.0
        records.append({
            'panel_id': k,
            'row': row, 'col': col,
            'lat': round(args.base_lat + row * d_lat, 6),
            'lon': round(args.base_lon + col * d_lon, 6),
            'classe': classe,
            'confiance': round(conf, 4),
            'anomalie': int(anomalie),
        })

    # --- CSV ---
    with open(out / 'report.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(records[0].keys()))
        w.writeheader()
        w.writerows(records)

    # --- Carte de la centrale ---
    cmap = ListedColormap(['#2ca02c', '#d62728'])
    cmap.set_bad('#eeeeee')
    plt.figure(figsize=(cols * 0.45 + 2, args.rows * 0.45 + 2))
    plt.imshow(np.ma.masked_invalid(grid), cmap=cmap, vmin=0, vmax=1)
    plt.xticks([]); plt.yticks([])
    n_anom = sum(r['anomalie'] for r in records)
    plt.title(f'Centrale solaire — {len(records)} panneaux | {n_anom} anomalies '
              f'({100 * n_anom / len(records):.0f}%)')
    plt.legend(handles=[mpatches.Patch(color='#2ca02c', label='Sain'),
                        mpatches.Patch(color='#d62728', label='Anomalie')],
               loc='upper center', bbox_to_anchor=(0.5, -0.03), ncol=2)
    plt.tight_layout()
    plt.savefig(out / 'plant_map.png', dpi=130, bbox_inches='tight')

    # --- Synthese console ---
    from collections import Counter
    types = Counter(r['classe'] for r in records if r['anomalie'])
    print(f"\nRapport ecrit : {out / 'report.csv'}")
    print(f"Carte ecrite  : {out / 'plant_map.png'}")
    print(f"\nAnomalies : {n_anom}/{len(records)} ({100 * n_anom / len(records):.1f}%)")
    print('Repartition des defauts detectes :')
    for c, n in types.most_common():
        print(f'  {c:16s} : {n}')


if __name__ == '__main__':
    main()
