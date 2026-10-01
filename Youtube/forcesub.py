import asyncio
import logging

from pyrogram import Client, enums
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LinkPreviewOptions,
)

from Youtube.config import Config

log = logging.getLogger("youtube-bot")


########################🎊 Lisa | NT BOTS 🎊######################################################


async def handle_force_subscribe(bot, message):
    try:
        invite_link = await bot.create_chat_invite_link(int(Config.CHANNEL))
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return 400
    except Exception as error:
        log.warning("Impossible de créer le lien d'invitation (%s) : %s", Config.CHANNEL, error)
        return 400 if Config.FORCE_SUB_STRICT else None

    try:
        user = await bot.get_chat_member(int(Config.CHANNEL), message.from_user.id)
        if user.status == enums.ChatMemberStatus.BANNED:
            await bot.send_message(
                chat_id=message.from_user.id,
                text="Sorry Sir, You are Banned. Contact My [Support Group](https://t.me/NT_BOTS_SUPPORT).",
                link_preview_options=LinkPreviewOptions(is_disabled=True),
            )
            return 400
    except UserNotParticipant:
        await bot.send_message(
            chat_id=message.from_user.id,
            text="Pʟᴇᴀsᴇ Jᴏɪɴ Mʏ Uᴘᴅᴀᴛᴇs Cʜᴀɴɴᴇʟ Tᴏ Usᴇ Mᴇ!\n\nDᴜᴇ ᴛᴏ Oᴠᴇʀʟᴏᴀᴅ, Oɴʟʏ Cʜᴀɴɴᴇʟ Sᴜʙsᴄʀɪʙᴇʀs Cᴀɴ Usᴇ Mᴇ!",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "🤖 Pʟᴇᴀsᴇ Jᴏɪɴ Mʏ Cʜᴀɴɴᴇʟ 🤖",
                            url=invite_link.invite_link,
                        )
                    ],
                ]
            ),
        )
        return 400
    except Exception as error:
        log.warning("Force-subscribe indisponible : %s", error)
        return 400 if Config.FORCE_SUB_STRICT else None


def humanbytes(size):
    if not size:
        return "0 B"
    power = 2**10
    n = 0
    dict_power_n = {0: "", 1: "Ki", 2: "Mi", 3: "Gi", 4: "Ti"}
    while size > power and n < 4:
        size /= power
        n += 1
    return f"{round(size, 2)} {dict_power_n[n]}B"


########################🎊 Lisa | NT BOTS 🎊######################################################
