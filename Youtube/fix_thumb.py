import os
import logging

from PIL import Image

log = logging.getLogger("youtube-bot")


async def fix_thumb(thumb_path: str):
    """Redimensionne la miniature aux dimensions acceptées par Telegram.

    Retourne (largeur, hauteur, chemin). En cas de problème, le chemin vaut
    None : la vidéo est alors envoyée sans miniature.
    """
    width = 0
    height = 0

    if not thumb_path or not os.path.exists(thumb_path):
        return width, height, None

    try:
        with Image.open(thumb_path) as img:
            img = img.convert("RGB")
            original_width, original_height = img.size

            # Telegram veut une miniature de 320 px maximum sur la largeur.
            target_width = min(320, original_width) or 320
            ratio = original_height / original_width if original_width else 1
            target_height = max(1, int(target_width * ratio))

            img.resize((target_width, target_height), Image.LANCZOS).save(
                thumb_path, "JPEG", quality=85
            )
            width, height = target_width, target_height
    except Exception as error:
        log.warning("[fix_thumb] %s", error)
        return 0, 0, None

    return width, height, thumb_path
