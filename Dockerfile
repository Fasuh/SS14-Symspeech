# Builder
FROM python:3.13-slim AS builder
WORKDIR /src
RUN apt-get update && apt-get install -y --no-install-recommends \
    cmake \
    build-essential \
    git \
    libglib2.0-dev \
    libsndfile1-dev &&\
    apt-get clean &&\ 
    rm -rf /var/lib/apt/lists/* &&\
    git clone --depth 1 https://github.com/FluidSynth/fluidsynth.git && \
    cd fluidsynth && mkdir build && cd build && \
    cmake .. \
        -DCMAKE_INSTALL_PREFIX=/usr/local \
        -Denable-sdl2=OFF \
        -Denable-pulseaudio=OFF \
        -Denable-alsa=OFF \
        -Denable-oss=OFF \
        -Denable-jack=OFF \
        -Denable-dbus=OFF \
        -DCMAKE_BUILD_TYPE=Release && \
    make -j$(nproc) && \
    make install
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Runner
FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app
COPY --from=builder /usr/local/lib /usr/local/lib
COPY --from=builder /usr/local/bin/fluidsynth /usr/local/bin/fluidsynth
RUN apt-get update && apt-get install -y --no-install-recommends libsndfile1 libglib2.0-0 libgomp1 &&\ 
    apt-get clean && rm -rf /var/lib/apt/lists/* &&\
    ldconfig

COPY --from=builder /install /usr/local
COPY config.json voices.json ./
COPY midi_soundfonts/ midi_soundfonts/
COPY src/ src/
CMD ["python", "-m", "src.worker"]