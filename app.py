"""Tableau de bord / health-check du bot.

Deux usages :
  * hébergement Web (Heroku/Render/Koyeb...) qui exige un port HTTP ouvert :
    ``gunicorn app:app``  ou  ``python3 app.py`` ;
  * diagnostic local : la page affiche l'état réel des dépendances
    (ffmpeg, runtime JavaScript, cookies, variables d'environnement).
"""

import os
import platform
import shutil
import sys
from importlib.metadata import version

from flask import Flask, jsonify

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Youtube.config import Config  # noqa: E402
from Youtube.helpers import find_ffmpeg, find_js_runtime  # noqa: E402

app = Flask(__name__)

BOT_USERNAME = os.environ.get("BOT_USERNAME", "")


# nom du module importé -> nom du paquet distribué
PACKAGES = {
    "yt_dlp": "yt-dlp",
    "pyrogram": "pyroblock",
    "flask": "flask",
    "PIL": "pillow",
    "aiohttp": "aiohttp",
}


def _version(module_name):
    """Récupère la version installée d'un module, sans attribut obsolète."""
    package = PACKAGES.get(module_name, module_name)
    try:
        return f"{package} {version(package)}"
    except Exception:
        pass

    try:
        module = __import__(module_name)
    except Exception:
        return f"{package} : absent"

    value = getattr(module, "__version__", None) or getattr(
        getattr(module, "version", None), "__version__", None
    )
    return f"{package} {value}" if value else f"{package} : installé"


def diagnostics():
    ffmpeg = find_ffmpeg()
    runtime = find_js_runtime()
    missing = Config.missing_credentials()

    return {
        "python": platform.python_version(),
        "plateforme": f"{platform.system()} {platform.machine()}",
        "yt_dlp": _version("yt_dlp"),
        "pyrogram": _version("pyrogram"),
        "flask": _version("flask"),
        "ffmpeg": ffmpeg or None,
        "runtime_javascript": runtime,
        "cookies": "chargés" if Config.use_cookies() else "aucun (mode anonyme)",
        "force_subscribe": Config.CHANNEL or "désactivé",
        "espace_libre_go": round(shutil.disk_usage(os.getcwd()).free / 1024**3, 1),
        "variables_manquantes": missing,
        "pret": not missing,
    }


@app.route("/")
def index():
    data = diagnostics()

    def line(label, value, good=None):
        if good is None:
            good = bool(value) and value not in ("absent", "inconnue")
        icon = "✅" if good else "⚠️"
        return (
            f"<tr><td>{label}</td>"
            f"<td><span class='ico'>{icon}</span> {value}</td></tr>"
        )

    rows = [
        line("Python", data["python"]),
        line("yt-dlp", data["yt_dlp"]),
        line("Pyrogram", data["pyrogram"]),
        line("ffmpeg", data["ffmpeg"] or "introuvable — MP3 et fusion vidéo indisponibles"),
        line(
            "Runtime JavaScript (deno/node)",
            data["runtime_javascript"]
            or "introuvable — certaines vidéos YouTube seront indisponibles",
        ),
        line("Cookies YouTube", data["cookies"], good=data["cookies"] == "chargés"),
        line("Force-subscribe", data["force_subscribe"], good=bool(Config.CHANNEL)),
        line("Espace disque libre", f"{data['espace_libre_go']} Go"),
    ]

    if data["variables_manquantes"]:
        banner = (
            "<div class='banner ko'>❌ Variables d'environnement manquantes : "
            + ", ".join(data["variables_manquantes"])
            + ". Le bot ne peut pas démarrer tant qu'elles ne sont pas définies "
            "(voir <code>.env.example</code>).</div>"
        )
    else:
        banner = (
            "<div class='banner ok'>✅ Configuration complète : le bot peut démarrer "
            "(<code>python3 bot.py</code>).</div>"
        )

    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>YouTube Video Download Bot — diagnostic</title>
<style>
 :root {{ color-scheme: dark; }}
 body {{ font-family: system-ui, -apple-system, "Segoe UI", sans-serif; margin: 0;
        background: #0f1115; color: #e8ecf1; display: flex; justify-content: center; }}
 main {{ max-width: 720px; width: 100%; padding: 32px 20px 64px; }}
 h1 {{ font-size: 22px; margin: 0 0 4px; }}
 p.sub {{ color: #8b97a8; margin: 0 0 24px; font-size: 14px; }}
 .banner {{ border-radius: 10px; padding: 14px 16px; font-size: 14px; margin-bottom: 20px; }}
 .banner.ok {{ background: #10291b; border: 1px solid #1f7a45; color: #7ee2a8; }}
 .banner.ko {{ background: #2b1416; border: 1px solid #8c2b34; color: #ff9aa2; }}
 table {{ width: 100%; border-collapse: collapse; background: #151922;
          border: 1px solid #232a36; border-radius: 10px; overflow: hidden; }}
 td {{ padding: 12px 14px; border-bottom: 1px solid #1e2430; font-size: 14px; }}
 tr:last-child td {{ border-bottom: none; }}
 td:first-child {{ color: #8b97a8; width: 42%; }}
 code {{ background: #1e2430; padding: 2px 6px; border-radius: 5px; }}
 footer {{ margin-top: 24px; color: #6b7684; font-size: 12px; line-height: 1.6; }}
 .ico {{ margin-right: 4px; }}
</style>
</head>
<body>
<main>
  <h1>🤖 YouTube Video Download Bot</h1>
  <p class="sub">Diagnostic de l'environnement — page servie par <code>app.py</code></p>
  {banner}
  <table>{''.join(rows)}</table>
  <footer>
    Le bot lui-même tourne dans un second processus : <code>python3 bot.py</code>.<br>
    Cette page ne fait que vérifier que tout est prêt pour Telegram + YouTube.
  </footer>
</main>
</body>
</html>"""


@app.route("/healthz")
def healthz():
    data = diagnostics()
    return jsonify(data), (200 if data["pret"] else 503)


if __name__ == "__main__":
    # 0.0.0.0 est indispensable pour être joignable depuis un conteneur / un preview.
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
