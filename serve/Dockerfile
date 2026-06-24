# SolarScan — image Docker du service d'inférence
# Build (depuis la racine du projet) :
#   docker build -t solarscan-api -f serve/Dockerfile .
# Run :
#   docker run -p 8000:8000 solarscan-api
FROM python:3.11-slim

WORKDIR /app

# Dépendances (torch CPU pour une image légère)
COPY serve/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
      --extra-index-url https://download.pytorch.org/whl/cpu

# Code + artefacts du modèle
COPY serve/api.py serve/api.py
COPY classes.json solarscan_resnet18.pt ./

EXPOSE 8000
CMD ["uvicorn", "serve.api:app", "--host", "0.0.0.0", "--port", "8000"]
