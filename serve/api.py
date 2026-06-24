"""SolarScan — API de production (FastAPI), adossée au pipeline et à la base.

Endpoints
---------
GET   /health                  état du service
POST  /predict                 une image -> classe + sévérité + perte estimée
POST  /inspections             upload d'images -> traite (détection/classif/GPS/sévérité) -> stocke
GET   /inspections             liste des inspections
GET   /inspections/{id}        panneaux d'une inspection (triés par gravité)
PATCH /panels/{id}             met à jour le statut maintenance (workflow terrain)

Lancement : uvicorn serve.api:app --port 8000   (doc : /docs)
"""
import io
import os
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from pydantic import BaseModel
from PIL import Image

from core import db, pipeline
from core.classifier import classify, CLASSES
from core.severity import assess

app = FastAPI(
    title='SolarScan API', version='2.0',
    description="Inspection de panneaux solaires par imagerie thermique de drone.")

db.init_db()
NORMAL = 'No-Anomaly'


@app.get('/health')
def health():
    return {'status': 'ok', 'classes': len(CLASSES)}


@app.post('/predict')
async def predict(file: UploadFile = File(...)):
    img = Image.open(io.BytesIO(await file.read())).convert('RGB')
    classe, conf = classify(img)
    return {'classe': classe, 'confiance': round(conf, 4),
            'anomalie': classe != NORMAL, **assess(classe)}


@app.post('/inspections')
async def create_inspection(nom: str = Form('Inspection'),
                            files: list[UploadFile] = File(...)):
    # Les uploads sont écrits sur disque pour que le GPS EXIF soit lisible par chemin.
    tmp = Path(tempfile.mkdtemp())
    paths = []
    for f in files:
        p = tmp / (f.filename or 'img.jpg')
        p.write_bytes(await f.read())
        paths.append(p)
    iid, panels = pipeline.process_images(paths, inspection_name=nom)
    for p in paths:
        try:
            os.remove(p)
        except OSError:
            pass
    return {'inspection_id': iid, 'n_panneaux': len(panels),
            'n_anomalies': sum(p['anomalie'] for p in panels)}


@app.get('/inspections')
def get_inspections():
    return db.list_inspections()


@app.get('/inspections/{iid}')
def get_inspection(iid: int):
    panels = db.get_panels(iid)
    if not panels:
        raise HTTPException(404, 'inspection inexistante ou vide')
    return {'inspection_id': iid, 'panels': panels}


class StatusUpdate(BaseModel):
    statut: str   # a_valider | valide | fausse_alerte | repare


@app.patch('/panels/{pid}')
def patch_panel(pid: int, body: StatusUpdate):
    db.update_status(pid, body.statut)
    return {'panel_id': pid, 'statut': body.statut}
