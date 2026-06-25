# SolarScan — image du service (API + dashboard)
# Construit depuis la racine du projet :
#   docker build -t solarscan-api -f serve/Dockerfile .
# Le modele .pt (lourd, non versionne) n'est PAS copie dans l'image :
# il est monte en volume au runtime (cf. docker-compose.yml / MODEL_PATH).
FROM python:3.11-slim

WORKDIR /app

# Dependances (torch CPU pour une image plus legere)
COPY serve/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
      --extra-index-url https://download.pytorch.org/whl/cpu

# Code applicatif + metadonnees du modele (le .pt est monte au runtime)
COPY core/ ./core/
COPY serve/ ./serve/
COPY dashboard/ ./dashboard/
COPY classes.json ./

EXPOSE 8000
# Healthcheck applicatif (pas de curl dans l'image slim -> urllib)
HEALTHCHECK --interval=10s --timeout=5s --start-period=30s --retries=5 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/health').status==200 else 1)"

CMD ["uvicorn", "serve.api:app", "--host", "0.0.0.0", "--port", "8000"]
