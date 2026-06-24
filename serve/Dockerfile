# SolarScan — image du service (API + dashboard)
# Construit depuis la racine du projet (le modele .pt doit etre present) :
#   docker build -t solarscan-api -f serve/Dockerfile .
FROM python:3.11-slim

WORKDIR /app

# Dependances (torch CPU pour une image plus legere)
COPY serve/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
      --extra-index-url https://download.pytorch.org/whl/cpu

# Code applicatif + artefacts du modele
COPY core/ ./core/
COPY serve/ ./serve/
COPY dashboard/ ./dashboard/
COPY classes.json solarscan_resnet18.pt ./

EXPOSE 8000
CMD ["uvicorn", "serve.api:app", "--host", "0.0.0.0", "--port", "8000"]
