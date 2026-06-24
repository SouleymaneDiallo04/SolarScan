"""SolarScan — API d'inférence de production (FastAPI).

Sert le modèle de classification d'anomalies thermiques derrière une API REST.

Endpoints
---------
GET  /health         état du service
POST /predict        une image thermique -> classe + probabilités + drapeau anomalie
POST /predict_batch  plusieurs images -> rapport synthétique (utile pour un vol drone)

Lancement local :
    uvicorn serve.api:app --reload --port 8000
Doc interactive : http://127.0.0.1:8000/docs
"""
import io
import json
from pathlib import Path

import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
from fastapi import FastAPI, File, UploadFile

ROOT = Path(__file__).resolve().parent.parent
DEVICE = 'cpu'
NORMAL_CLASS = 'No-Anomaly'

with open(ROOT / 'classes.json', encoding='utf-8') as f:
    CLASSES = json.load(f)

model = models.resnet18()
model.fc = nn.Linear(model.fc.in_features, len(CLASSES))
model.load_state_dict(torch.load(ROOT / 'solarscan_resnet18.pt', map_location=DEVICE))
model.eval()

MEAN, STD = [0.485, 0.456, 0.406], [0.229, 0.224, 0.225]
_tf = transforms.Compose([
    transforms.Grayscale(3), transforms.Resize((224, 224)),
    transforms.ToTensor(), transforms.Normalize(MEAN, STD)])

app = FastAPI(
    title='SolarScan API',
    version='1.0',
    description="Détection de défauts sur panneaux solaires à partir d'imagerie thermique.")


def _infer(img: Image.Image) -> dict:
    x = _tf(img).unsqueeze(0)
    with torch.no_grad():
        probs = torch.softmax(model(x), 1)[0].tolist()
    idx = max(range(len(probs)), key=lambda i: probs[i])
    return {
        'classe': CLASSES[idx],
        'confiance': round(probs[idx], 4),
        'anomalie': CLASSES[idx] != NORMAL_CLASS,
        'probabilites': {CLASSES[i]: round(probs[i], 4) for i in range(len(CLASSES))},
    }


@app.get('/health')
def health():
    return {'status': 'ok', 'model': 'resnet18', 'classes': len(CLASSES)}


@app.post('/predict')
async def predict(file: UploadFile = File(...)):
    img = Image.open(io.BytesIO(await file.read()))
    return _infer(img)


@app.post('/predict_batch')
async def predict_batch(files: list[UploadFile] = File(...)):
    results, n_anom = [], 0
    for f in files:
        img = Image.open(io.BytesIO(await f.read()))
        r = _infer(img)
        r['fichier'] = f.filename
        results.append(r)
        n_anom += int(r['anomalie'])
    return {'total': len(results), 'anomalies': n_anom, 'resultats': results}
