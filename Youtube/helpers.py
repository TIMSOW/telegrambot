"""Fonctions utilitaires partagées par le bot (ffmpeg, runtime JS, formatage)."""

import glob
import os
import shutil

from Youtube.config import Config

# Taille maximale acceptée par l'API Telegram pour un bot (2 Go).
TELEGRAM_MAX_UPLOAD = 2 * 1024 * 1024 * 1024

FFMPEG_NAMES = ("ffmpeg", "ffmpeg.exe")
JS_RUNTIMES = (
    ("deno", "deno"),
    ("node", "node"),
    ("bun", "bun"),
    ("quickjs", "qjs"),
)


def find_ffmpeg():
    """Cherche un binaire ffmpeg utilisable et retourne son chemin (ou None).

    Ordre de recherche : variable FFMPEG_LOCATION, PATH, puis emplacements
    classiques (dont un dossier ``bin/`` à la racine du projet).
    """
    candidates = [
        os.environ.get("FFMPEG_LOCATION") or "",
        getattr(Config, "FFMPEG_LOCATION", "") or "",
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bin", "ffmpeg"),
        "/usr/bin/ffmpeg",
        "/usr/local/bin/ffmpeg",
        "/opt/homebrew/bin/ffmpeg",
    ]

    for candidate in candidates:
        if candidate and os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate

    found = shutil.which("ffmpeg") or shutil.which("ffmpeg.exe")
    if found:
        return found
    return None


def ffmpeg_location():
    """Chemin à passer à yt-dlp (dossier ou binaire) pour trouver ffmpeg."""
    path = find_ffmpeg()
    if not path:
        return None
    # yt-dlp accepte indifféremment le binaire ou son dossier.
    return path


def find_js_runtime():
    """Retourne le nom du premier runtime JavaScript disponible pour yt-dlp.

    yt-dlp en a besoin pour résoudre les challenges JavaScript de YouTube
    (vidéos « format dramatique », signatures...). Sans runtime, beaucoup de
    vidéos restent indisponibles.
    """
    for name, binary in JS_RUNTIMES:
        if shutil.which(binary):
            return name
    return None


def cleanup(prefix, directory="downloads"):
    """Supprime les fichiers temporaires commençant par ``prefix``."""
    removed = []
    pattern = os.path.join(directory, f"{prefix}*")
    for path in glob.glob(pattern):
        try:
            if os.path.isdir(path):
                shutil.rmtree(path, ignore_errors=True)
            else:
                os.remove(path)
            removed.append(path)
        except OSError:
            pass
    return removed


def resolve_downloaded_file(info, prefix, directory="downloads", prefer=None):
    """Retrouve le chemin du fichier réellement produit par yt-dlp."""
    for entry in info.get("requested_downloads") or []:
        filepath = entry.get("filepath")
        if filepath and os.path.exists(filepath):
            return filepath

    candidates = [
        path
        for path in glob.glob(os.path.join(directory, f"{prefix}*"))
        if not path.endswith((".part", ".ytdl", ".temp", ".jpg", ".jpeg", ".png", ".webp"))
    ]
    if not candidates:
        return None

    if prefer:
        for path in candidates:
            if path.lower().endswith(f".{prefer.lower()}"):
                return path
    # À défaut, on prend le plus gros fichier (c'est la vidéo finale).
    candidates.sort(key=os.path.getsize, reverse=True)
    return candidates[0]


def escape_caption(text):
    """Échappe le texte pour un envoi en HTML (titres YouTube)."""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def base_ydl_opts(**extra):
    """Options yt-dlp communes : cookies (si réels), ffmpeg, runtime JS."""
    opts = {"quiet": True, "noprogress": True, "nocheckcertificate": True}

    if Config.use_cookies():
        opts["cookiefile"] = Config.COOKIE_FILE

    ffmpeg = ffmpeg_location()
    if ffmpeg:
        opts["ffmpeg_location"] = ffmpeg

    runtime = find_js_runtime()
    if runtime:
        opts["js_runtimes"] = {runtime: {}}

    proxy = Config.HTTP_PROXY
    if proxy:
        opts["proxy"] = proxy

    opts.update(extra)
    return opts
