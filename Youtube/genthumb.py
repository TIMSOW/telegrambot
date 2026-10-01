# ©️ LISA-KOREA | @LISA_FAN_LK | NT_BOT_CHANNEL | LISA-KOREA/YouTube-Video-Download-Bot
# ⚠️ Do not change this repo link ⚠️
# Repo: https://github.com/LISA-KOREA/YouTube-Video-Download-Bot

import logging
import os
import tempfile

import aiohttp
import yt_dlp
from pyrogram import Client, filters

from Youtube.config import Config
from Youtube.forcesub import handle_force_subscribe
from Youtube.helpers import base_ydl_opts

log = logging.getLogger("youtube-bot")


@Client.on_message(filters.command("thumbnail"))
async def generate_thumbnail(client, message):
    if Config.CHANNEL:
        fsub = await handle_force_subscribe(client, message)
        if fsub == 400:
            return

    if len(message.command) < 2:
        return await message.reply_text(
            "❗Please provide a YouTube video link.\n\n"
            "**Example:** `/thumbnail <YouTube_URL>`"
        )

    video_url = message.text.split(" ", 1)[1].strip()
    wait = await message.reply_text("🔍 Fetching thumbnail...")
    file_name = None

    try:
        # Extraction des informations sans téléchargement de la vidéo.
        with yt_dlp.YoutubeDL(base_ydl_opts(extract_flat=False)) as ydl:
            info = ydl.extract_info(video_url, download=False)
            thumbnail_url = info.get("thumbnail")
            if not thumbnail_url:
                for thumb in info.get("thumbnails") or []:
                    if thumb.get("url"):
                        thumbnail_url = thumb["url"]
                        break

        if not thumbnail_url:
            await wait.delete()
            return await message.reply_text("⚠️ Couldn't find any thumbnail for this video.")

        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(thumbnail_url) as response:
                if response.status != 200:
                    await wait.delete()
                    return await message.reply_text(f"Thumbnail URL: {thumbnail_url}")

                # Fichier temporaire : rien n'est laissé sur le disque.
                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as handle:
                    handle.write(await response.read())
                    file_name = handle.name

        await message.reply_photo(photo=file_name, caption="🖼️ **Video Thumbnail**")

    except Exception as error:
        log.exception("Thumbnail error:")
        await message.reply_text(f"❌ Error: `{error}`")
    finally:
        if file_name and os.path.exists(file_name):
            try:
                os.remove(file_name)
            except OSError:
                pass
        try:
            await wait.delete()
        except Exception:
            pass
