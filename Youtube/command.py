# ©️ LISA-KOREA | @LISA_FAN_LK | NT_BOT_CHANNEL | LISA-KOREA/YouTube-Video-Download-Bot

# [⚠️ Do not change this repo link ⚠️] :- https://github.com/LISA-KOREA/YouTube-Video-Download-Bot



from pyrogram import Client, filters
import datetime
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ForceReply, LinkPreviewOptions
from Youtube.config import Config
from Youtube.script import Translation
from Youtube.forcesub import handle_force_subscribe


#########################


def current_wish():
    """Salutation calculée à chaque message (et non au démarrage du bot)."""
    current_time = datetime.datetime.now()
    if current_time.hour < 12:
        return "Good morning 🌞"
    if 12 <= current_time.hour < 18:
        return "Good afternoon 🌤️"
    return "Good evening 🌝"


########################🎊 Lisa | NT BOTS 🎊######################################################
@Client.on_callback_query(filters.regex("cancel"))
async def cancel(client, callback_query):
    await callback_query.message.delete()

# About command handler
@Client.on_message(filters.private & filters.command("about"))
async def about(client, message):
    if Config.CHANNEL:
      fsub = await handle_force_subscribe(client, message)
      if fsub == 400:
        return
    await message.reply_text(
        text=Translation.ABOUT_TXT,
        link_preview_options=LinkPreviewOptions(is_disabled=True),
        reply_markup=InlineKeyboardMarkup(
        [
            [InlineKeyboardButton('⛔️ Close', callback_data='cancel')]
        ]
    ))


# Start command handler
@Client.on_message(filters.private & filters.command("start"))
async def start(client, message):
    if Config.CHANNEL:
      fsub = await handle_force_subscribe(client, message)
      if fsub == 400:
        return
    #user = message.from_user
    await message.reply_text(
        text=Translation.START_TEXT.format(message.from_user.first_name, current_wish()),
        reply_markup=InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton('📍 Update Channel', url='https://t.me/NT_BOT_CHANNEL'),
            ],
            [
                InlineKeyboardButton('👩‍💻 Developer', url='https://t.me/LISA_FAN_LK'),
                InlineKeyboardButton('👥 Support Group', url='https://t.me/NT_BOTS_SUPPORT'),
            ],
            [
                InlineKeyboardButton('⛔️ Close', callback_data='cancel')
            ]
        ]
    ))

# Help command handler
@Client.on_message(filters.private & filters.command("help"))
async def help(client, message):
    if Config.CHANNEL:
        fsub = await handle_force_subscribe(client, message)
        if fsub == 400:
            return
    help_text = """
Welcome to the YouTube Video Uploader Bot!

To upload a YouTube video, simply send me the YouTube link.

Enjoy using the bot!

©️ Channel : @NT_BOT_CHANNEL
    """
    await message.reply_text(help_text)


########################🎊 Lisa | NT BOTS 🎊######################################################
