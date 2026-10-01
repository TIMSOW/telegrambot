import os

# Charge automatiquement un fichier .env s'il existe (pratique en local).
# Sans .env, les variables d'environnement classiques sont utilisées.
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # python-dotenv non installé : on continue quand même
    pass


def _get_int(name, default=0):
    value = os.environ.get(name, "")
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


class Config(object):

    BOT_TOKEN = (os.environ.get("BOT_TOKEN") or "").strip()
    API_ID = _get_int("API_ID", 0)
    API_HASH = (os.environ.get("API_HASH") or "").strip()

    # ID / username du channel pour le force-subscribe (optionnel).
    CHANNEL = (os.environ.get("CHANNEL") or "").strip()

    # Fichier de cookies YouTube (optionnel). Peut pointer ailleurs :
    #   COOKIE_FILE=/etc/secrets/cookies.txt
    COOKIE_FILE = (os.environ.get("COOKIE_FILE") or "cookies.txt").strip()

    # Proxy HTTP optionnel (ex. http://user:pass@host:port)
    HTTP_PROXY = (os.environ.get("HTTP_PROXY") or "").strip()

    # Chemin vers le binaire ffmpeg si celui-ci n'est pas dans le PATH.
    FFMPEG_LOCATION = (os.environ.get("FFMPEG_LOCATION") or "").strip()

    # True = bloquer l'utilisateur si le force-subscribe est mal configuré.
    # False (par défaut) = laisser passer et écrire un avertissement dans les logs.
    FORCE_SUB_STRICT = (os.environ.get("FORCE_SUB_STRICT") or "").strip().lower() in ("1", "true", "yes", "on")

    @classmethod
    def missing_credentials(cls):
        """Retourne la liste des variables d'environnement obligatoires absentes."""
        missing = []
        if not cls.BOT_TOKEN:
            missing.append("BOT_TOKEN")
        if not cls.API_ID:
            missing.append("API_ID")
        if not cls.API_HASH:
            missing.append("API_HASH")
        return missing

    @classmethod
    def use_cookies(cls):
        """True si le fichier de cookies existe et contient au moins un cookie réel."""
        path = cls.COOKIE_FILE
        if not path or not os.path.exists(path):
            return False
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as handle:
                for line in handle:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        return True
        except OSError:
            return False
        return False
