import os

# Charge automatiquement un fichier .env s'il existe (pratique en local).
# Sans .env, les variables d'environnement classiques sont utilisées.
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # python-dotenv non installé : on continue quand même
    pass


def _clean(value):
    """Nettoie une valeur : espaces et guillemets autour (erreur classique en .env)."""
    value = str(value or "").strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        value = value[1:-1].strip()
    return value


def _get_str(name, default=""):
    return _clean(os.environ.get(name, default))


def _get_int(name, default=0):
    try:
        return int(_clean(os.environ.get(name, "")))
    except (TypeError, ValueError):
        return default


class Config(object):

    BOT_TOKEN = _get_str("BOT_TOKEN")
    API_ID = _get_int("API_ID", 0)
    API_HASH = _get_str("API_HASH")

    # ID / username du channel pour le force-subscribe (optionnel).
    CHANNEL = _get_str("CHANNEL")

    # Fichier de cookies YouTube (optionnel). Peut pointer ailleurs :
    #   COOKIE_FILE=/etc/secrets/cookies.txt
    COOKIE_FILE = _get_str("COOKIE_FILE", "cookies.txt") or "cookies.txt"

    # Proxy HTTP optionnel (ex. http://user:pass@host:port)
    HTTP_PROXY = _get_str("HTTP_PROXY")

    # Chemin vers le binaire ffmpeg si celui-ci n'est pas dans le PATH.
    FFMPEG_LOCATION = _get_str("FFMPEG_LOCATION")

    # True = bloquer l'utilisateur si le force-subscribe est mal configuré.
    # False (par défaut) = laisser passer et écrire un avertissement dans les logs.
    FORCE_SUB_STRICT = _get_str("FORCE_SUB_STRICT").lower() in ("1", "true", "yes", "on")

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
