#!/usr/bin/env bash
# Démarrage local du bot : ./start.sh
#   - utilise le venv .venv s'il existe
#   - charge le fichier .env s'il existe
#   - vérifie les prérequis avant de lancer bot.py
set -euo pipefail

cd "$(dirname "$0")"

PYTHON="${PYTHON:-python3}"
if [ -x ".venv/bin/python" ]; then
    PYTHON=".venv/bin/python"
fi

# Charge les variables du fichier .env (sans écraser celles déjà définies).
if [ -f ".env" ]; then
    set -a
    # shellcheck disable=SC1091
    . ./.env
    set +a
    echo "ℹ️  .env chargé"
fi

echo "🐍 Interpréteur : $($PYTHON --version 2>&1)"

# ffmpeg : présent dans le PATH ou fourni via FFMPEG_LOCATION
if command -v ffmpeg >/dev/null 2>&1; then
    echo "✅ ffmpeg : $(command -v ffmpeg)"
elif [ -n "${FFMPEG_LOCATION:-}" ] && [ -x "${FFMPEG_LOCATION}" ]; then
    echo "✅ ffmpeg : ${FFMPEG_LOCATION}"
else
    echo "⚠️  ffmpeg introuvable : la conversion MP3 et la fusion vidéo+audio échoueront."
    echo "    Debian/Ubuntu : sudo apt install -y ffmpeg"
    echo "    macOS         : brew install ffmpeg"
fi

# Runtime JavaScript utilisé par yt-dlp pour YouTube
if command -v deno >/dev/null 2>&1; then
    echo "✅ deno : $(command -v deno)"
elif command -v node >/dev/null 2>&1; then
    echo "✅ node : $(command -v node)"
else
    echo "⚠️  Ni deno ni node trouvés : certaines vidéos YouTube seront indisponibles."
    echo "    deno : curl -fsSL https://deno.land/install.sh | sh"
fi

if [ -z "${BOT_TOKEN:-}" ] || [ -z "${API_ID:-}" ] || [ -z "${API_HASH:-}" ]; then
    echo "❌ BOT_TOKEN, API_ID et API_HASH sont obligatoires."
    echo "   Copie .env.example en .env puis remplis tes valeurs : cp .env.example .env"
    exit 1
fi

echo "🚀 Démarrage du bot (Ctrl+C pour arrêter)..."
exec "$PYTHON" bot.py
