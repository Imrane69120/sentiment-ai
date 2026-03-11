FROM python:3.11-slim

WORKDIR /app

# Copie des dépendances en premier pour profiter du cache Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY src/ ./src/
COPY tests/ ./tests/

# Exposition du port Flask
EXPOSE 5000

# Lancement de l'API par défaut
CMD ["python", "-m", "src.app"]
