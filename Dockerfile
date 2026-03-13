FROM python:3.13-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends fluidsynth libsndfile1 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY config.json voices.json ./
COPY midi_soundfonts/ midi_soundfonts/
COPY src/ src/

CMD ["python", "-m", "src.worker"]