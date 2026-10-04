# ©️ LISA-KOREA | @LISA_FAN_LK | NT_BOT_CHANNEL | LISA-KOREA/YouTube-Video-Download-Bot

# [⚠️ Do not change this repo link ⚠️] :- https://github.com/LISA-KOREA/YouTube-Video-Download-Bot

import logging
import sys

from pyrogram import Client

from Youtube.config import Config
from Youtube.helpers import find_ffmpeg, find_js_runtime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
log = logging.getLogger("youtube-bot")


def check_environment():
    """Vérifie la configuration avant de démarrer et explique quoi corriger."""
    missing = Config.missing_credentials()

    print("\n" + "=" * 60)
    print("🚨  SECURITY WARNING for Forked Users  🚨")
    print("-" * 60)
    print("⚠️  This is a PUBLIC repository.")
    print("🧠  Do NOT expose your BOT_TOKEN, API_ID, API_HASH, or cookies.txt.")
    print("💡  Always use Heroku Config Vars or a private .env file to store secrets.")
    print("🔒  Never commit sensitive data to your fork — anyone can steal it!")
    print("📢  Support: @NT_BOTS_SUPPORT")
    print("=" * 60 + "\n")

    if missing:
        print("❌ Configuration incomplète / Missing configuration: " + ", ".join(missing))
        print("-" * 60)
        print("Renseigne ces variables d'environnement (ou crée un fichier .env) :")
        print("  BOT_TOKEN  → token donné par @BotFather")
        print("  API_ID     → https://my.telegram.org  (API development tools)")
        print("  API_HASH   → https://my.telegram.org")
        print("  CHANNEL    → (optionnel) id du channel pour le force-subscribe")
        print("\nExemple :")
        print('  export BOT_TOKEN="123456:ABC..." API_ID=1234567 API_HASH="abcdef..."')
        print("  python3 bot.py")
        print("=" * 60 + "\n")
        sys.exit(1)

    ffmpeg = find_ffmpeg()
    if ffmpeg:
        log.info("ffmpeg trouvé : %s", ffmpeg)
    else:
        log.warning(
            "ffmpeg est introuvable : la conversion MP3 et la fusion vidéo+audio "
            "échoueront. Installe-le (apt install ffmpeg) ou définis FFMPEG_LOCATION."
        )

    runtime = find_js_runtime()
    if runtime:
        log.info("Runtime JavaScript détecté : %s", runtime)
    else:
        log.warning(
            "Aucun runtime JavaScript (deno/node) trouvé : certaines vidéos YouTube "
            "pourront être indisponibles. Installe deno (curl -fsSL https://deno.land/install.sh | sh) "
            "ou node."
        )

    if Config.CHANNEL:
        log.info("Force-subscribe actif sur le channel : %s", Config.CHANNEL)
    log.info("Cookies : %s", "chargés" if Config.use_cookies() else "aucun (mode anonyme)")


# Create a Pyrogram client
app = Client(
    "my_bot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    plugins=dict(root="Youtube"),
)


if __name__ == "__main__":
    check_environment()
    print("🎊 I AM ALIVE 🎊")
    app.run()
