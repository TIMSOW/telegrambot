from datetime import datetime

import pytz
from pyrogram import Client, filters

# Dictionary of time zones for various countries
COUNTRY_TIMEZONES = {
    "Argentina": "America/Argentina/Buenos_Aires",
    "Australia Eastern": "Australia/Sydney",
    "Australia Central": "Australia/Adelaide",
    "Australia Western": "Australia/Perth",
    "Brazil": "America/Sao_Paulo",
    "Canada Eastern": "America/Toronto",
    "Canada Central": "America/Winnipeg",
    "Canada Mountain": "America/Edmonton",
    "Canada Pacific": "America/Vancouver",
    "China": "Asia/Shanghai",
    "France": "Europe/Paris",
    "Germany": "Europe/Berlin",
    "India": "Asia/Kolkata",
    "Japan": "Asia/Tokyo",
    "Mexico": "America/Mexico_City",
    "Russia Moscow": "Europe/Moscow",
    "Russia Kamchatka": "Asia/Kamchatka",
    "Saudi Arabia": "Asia/Riyadh",
    "South Africa": "Africa/Johannesburg",
    "South Korea": "Asia/Seoul",
    "UAE": "Asia/Dubai",
    "UK": "Europe/London",
    "USA Eastern": "America/New_York",
    "USA Central": "America/Chicago",
    "USA Mountain": "America/Denver",
    "USA Pacific": "America/Los_Angeles",
    "USA Alaska": "America/Anchorage",
    "USA Hawaii": "Pacific/Honolulu",
}


@Client.on_message(filters.command("date"))
async def date(client, message):
    # Get the country from the message text if provided
    country = "South Korea"  # Default to South Korea
    if len(message.command) > 1:
        country = " ".join(message.command[1:])

    timezone = COUNTRY_TIMEZONES.get(country)
    if not timezone:
        return await message.reply_text(
            "Sorry, I don't have the time zone information for that country.\n"
            "Available: " + ", ".join(sorted(COUNTRY_TIMEZONES))
        )

    current_date = datetime.now(pytz.timezone(timezone)).strftime("%Y-%m-%d %H:%M:%S")
    await message.reply_text(f"The current date and time in {country} is: {current_date}")
