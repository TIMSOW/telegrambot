# Image de base : même version Python que runtime.txt (validée avec ce projet).
FROM python:3.11-alpine

WORKDIR /app

# ffmpeg est obligatoire (conversion MP3 + fusion vidéo/audio).
RUN apk add --no-cache \
    ffmpeg \
    jq \
    python3-dev \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    curl \
    unzip

# Runtime JavaScript requis par yt-dlp pour YouTube (challenges JS).
ENV DENO_INSTALL=/root/.deno
ENV PATH=$DENO_INSTALL/bin:$PATH
RUN curl -fsSL https://deno.land/install.sh | sh && deno --version

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN yt-dlp --version && ffmpeg -version && python3 -m pip check

# Le bot (worker) + le tableau de bord de diagnostic (port HTTP).
CMD ["python3", "bot.py"]
