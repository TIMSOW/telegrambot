# ©️ LISA-KOREA | @LISA_FAN_LK | NT_BOT_CHANNEL | LISA-KOREA/YouTube-Video-Download-Bot

# [⚠️ Do not change this repo link ⚠️] :- https://github.com/LISA-KOREA/YouTube-Video-Download-Bot

import asyncio
import logging
import os
import time
import uuid
import aiofiles
import aiohttp
import yt_dlp
from pyrogram import Client, enums, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from Youtube.config import Config
from Youtube.fix_thumb import fix_thumb
from Youtube.forcesub import handle_force_subscribe, humanbytes
from Youtube.helpers import (
    TELEGRAM_MAX_UPLOAD,
    base_ydl_opts,
    cleanup,
    escape_caption,
    resolve_downloaded_file,
)

DOWNLOAD_DIR = "downloads"

# vid_key -> {"url": ..., "ts": ...}
YT_CACHE = {}
CACHE_TTL = 6 * 60 * 60  # 6 heures


def cache_put(url):
    """Enregistre une URL et retourne une clé courte utilisable en callback_data."""
    now = time.time()
    for key in [k for k, v in list(YT_CACHE.items()) if now - v["ts"] > CACHE_TTL]:
        YT_CACHE.pop(key, None)
    key = uuid.uuid4().hex[:8]
    YT_CACHE[key] = {"url": url, "ts": now}
    return key


def cache_get(key):
    entry = YT_CACHE.get(key)
    if not entry:
        return None
    if time.time() - entry["ts"] > CACHE_TTL:
        YT_CACHE.pop(key, None)
        return None
    return entry["url"]


async def pump_progress(message, state, prefix):
    """Met à jour le message pendant le téléchargement (non bloquant)."""
    last_text = None
    try:
        while True:
            percent = state.get("pct")
            if state.get("stage") == "processing":
                text = f"{prefix}\n🎬 **Processing / merging...**"
            elif percent is None:
                text = f"{prefix}\n⬇️ **Downloading...**"
            else:
                text = f"{prefix}\n⬇️ **Downloading...** `{percent}%`"
            if text != last_text:
                try:
                    await message.edit_text(text)
                    last_text = text
                except Exception:
                    pass
            await asyncio.sleep(4)
    except asyncio.CancelledError:
        raise


async def upload_progress(current, total, message, prefix):
    """Affiche la progression de l'upload (appelé par Pyrogram)."""
    try:
        if not total or current != total:
            percent = int(current * 100 / total) if total else 0
            await message.edit_text(f"{prefix}\n📤 **Uploading...** `{percent}%`")
    except Exception:
        pass


@Client.on_message(filters.regex(r"^(http(s)?://)?(www\.)?(youtube\.com|youtu\.be)/.+"))
async def youtube_downloader(client, message):
    if Config.CHANNEL:
        fsub = await handle_force_subscribe(client, message)
        if fsub == 400:
            return

    url = message.text.strip()
    processing_msg = await message.reply_text("🔍 **Fetching available formats...**")

    buttons = []
    try:
        info = await asyncio.to_thread(extract_info, url)
        formats = info.get("formats", []) or []
        title = info.get("title", "YouTube Video")
        duration = info.get("duration")
        vid_key = cache_put(url)

        for fmt in formats:
            fmt_id = fmt.get("format_id")
            note = fmt.get("format_note") or fmt.get("format") or "Unknown"
            ext = (fmt.get("ext") or "mp4").replace("|", "")
            vcodec = fmt.get("vcodec")
            size = fmt.get("filesize") or fmt.get("filesize_approx")
            size_text = humanbytes(size) if size else "Unknown"

            # On ne garde que les pistes qui contiennent de la vidéo.
            if not fmt_id or not vcodec or vcodec == "none":
                continue

            text = f"{note} • {size_text}"
            callback = f"ytdl|{vid_key}|{fmt_id}|{ext}|video"
            if len(callback.encode()) <= 64:
                buttons.append([InlineKeyboardButton(text, callback_data=callback)])

        buttons.append(
            [
                InlineKeyboardButton(
                    "🎵 Audio MP3", callback_data=f"ytdl|{vid_key}|bestaudio|mp3|audio"
                )
            ]
        )
        if duration:
            buttons.append(
                [
                    InlineKeyboardButton(
                        "⭐ Best quality (video+audio)",
                        callback_data=f"ytdl|{vid_key}|bestvideo+bestaudio|mp4|video",
                    )
                ]
            )

        await message.reply_text(
            f"**✅ Available formats for:**\n`{escape_caption(title)}`",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
        await processing_msg.delete()

    except Exception as error:
        logging.exception("Error fetching formats:")
        await processing_msg.edit_text(f"❌ Error: `{escape_caption(error)}`")


def extract_info(url):
    """Extraction synchrone exécutée dans un thread pour ne pas bloquer le bot."""
    with yt_dlp.YoutubeDL(base_ydl_opts(extract_flat=False)) as ydl:
        return ydl.extract_info(url, download=False)


def download_sync(url, opts, state):
    def hook(data):
        status = data.get("status")
        if status == "downloading":
            total = data.get("total_bytes") or data.get("total_bytes_estimate")
            downloaded = data.get("downloaded_bytes") or 0
            if total:
                state["pct"] = int(downloaded * 100 / total)
                state["stage"] = "downloading"
        elif status == "finished":
            state["pct"] = 100
            state["stage"] = "processing"
        elif status == "error":
            state["stage"] = "error"

    opts["progress_hooks"] = [hook]
    with yt_dlp.YoutubeDL(opts) as ydl:
        return ydl.extract_info(url, download=True)


@Client.on_callback_query(filters.regex(r"^ytdl\|"))
async def handle_download(client, cq):
    file_path = None
    thumb_path = None
    vid_key = None

    try:
        _, vid_key, fmt_id, ext, mode = cq.data.split("|", 4)
        url = cache_get(vid_key)
        if not url:
            await cq.message.edit_text("⚠️ Session expired. Please resend link.")
            return

        await cq.message.edit_text("⬇️ **Starting download...**")

        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        output = os.path.join(DOWNLOAD_DIR, f"{vid_key}.%(ext)s")

        if mode == "audio":
            ydl_opts = base_ydl_opts(
                format="bestaudio/best",
                outtmpl=output,
                postprocessors=[
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
            )
        else:
            ydl_opts = base_ydl_opts(
                format=f"{fmt_id}/bestvideo+bestaudio/best",
                outtmpl=output,
                merge_output_format="mp4",
            )

        state = {"pct": None, "stage": "downloading"}
        progress_task = asyncio.create_task(
            pump_progress(cq.message, state, "📥 **Please wait...**")
        )
        try:
            info = await asyncio.to_thread(download_sync, url, ydl_opts, state)
        finally:
            progress_task.cancel()
            try:
                await progress_task
            except (asyncio.CancelledError, Exception):
                pass

        title = escape_caption(info.get("title", "YouTube Video"))
        duration = info.get("duration") or 0
        width = info.get("width")
        height = info.get("height")

        prefer = "mp3" if mode == "audio" else "mp4"
        file_path = resolve_downloaded_file(info, vid_key, DOWNLOAD_DIR, prefer=prefer)

        if not file_path or not os.path.exists(file_path):
            await cq.message.edit_text(
                "❌ Download finished but the file was not found. "
                "Check that ffmpeg is installed."
            )
            return

        file_size = os.path.getsize(file_path)
        if file_size > TELEGRAM_MAX_UPLOAD:
            await cq.message.edit_text(
                f"❌ File too large for Telegram: `{humanbytes(file_size)}` "
                f"(limit {humanbytes(TELEGRAM_MAX_UPLOAD)})."
            )
            return
        file_size_text = humanbytes(file_size)

        thumb_url = info.get("thumbnail")
        thumb_path = os.path.join(DOWNLOAD_DIR, f"{vid_key}.jpg")
        if thumb_url:
            try:
                timeout = aiohttp.ClientTimeout(total=30)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get(thumb_url) as response:
                        if response.status == 200:
                            async with aiofiles.open(thumb_path, "wb") as handle:
                                await handle.write(await response.read())
                        else:
                            thumb_path = None
            except Exception:
                logging.exception("Thumbnail download failed:")
                thumb_path = None
        else:
            thumb_path = None

        _, _, thumb_path = await fix_thumb(thumb_path)

        prefix = f"📤 **Uploading** `{file_size_text}`"
        await cq.message.edit_text(f"{prefix}\n📤 **Uploading...** `0%`")

        if mode == "audio":
            await client.send_audio(
                chat_id=cq.message.chat.id,
                audio=file_path,
                caption=f"🎵 <b>{title}</b>\n📦 Size: <code>{file_size_text}</code>",
                parse_mode=enums.ParseMode.HTML,
                duration=duration,
                title=info.get("title"),
                performer=info.get("uploader"),
                thumb=thumb_path if thumb_path and os.path.exists(thumb_path) else None,
                progress=upload_progress,
                progress_args=(cq.message, prefix),
            )
        else:
            await client.send_video(
                chat_id=cq.message.chat.id,
                video=file_path,
                caption=f"🎬 <b>{title}</b>\n📦 Size: <code>{file_size_text}</code>",
                parse_mode=enums.ParseMode.HTML,
                width=width or 0,
                height=height or 0,
                duration=duration,
                thumb=thumb_path if thumb_path and os.path.exists(thumb_path) else None,
                supports_streaming=True,
                progress=upload_progress,
                progress_args=(cq.message, prefix),
            )

        await cq.message.delete()

    except Exception as error:
        logging.exception("Download error:")
        try:
            await cq.message.edit_text(f"❌ Error: `{escape_caption(error)}`")
        except Exception:
            pass

    finally:
        # Nettoyage : on ne garde jamais de fichiers sur le disque.
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass
        if thumb_path and os.path.exists(thumb_path):
            try:
                os.remove(thumb_path)
            except OSError:
                pass
        if vid_key:
            cleanup(vid_key, DOWNLOAD_DIR)

