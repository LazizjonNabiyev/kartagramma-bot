import os
from aiogram import Bot
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

# Kanallar
REQUIRED_CHANNEL = os.getenv("REQUIRED_CHANNEL", "@kartagrammachat")
LOG_CHANNEL = os.getenv("LOG_CHANNEL", "@kartabaza")


async def check_subscription(bot: Bot, user_id: int) -> bool:
    """Foydalanuvchi kanalga obuna bo'lganmi?"""
    try:
        member = await bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False


def subscribe_keyboard():
    """Obuna bo'lish tugmasi"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Kanalga obuna bo'lish", url=f"https://t.me/kartagrammachat")],
        [InlineKeyboardButton(text="✅ Obuna bo'ldim", callback_data="check_subscription")]
    ])


async def send_log(bot: Bot, user_id: int, username: str, full_name: str, age: int):
    """Log kanalga yangi foydalanuvchi ma'lumotini yuborish"""
    try:
        text = (
            "👤 <b>Yangi foydalanuvchi!</b>\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            "📛 Ism: <b>" + (full_name or "—") + "</b>\n"
            "🎂 Yosh: <b>" + str(age) + "</b>\n"
            "📱 Username: @" + (username or "yoq") + "\n"
            "🆔 ID: <code>" + str(user_id) + "</code>\n"
            "━━━━━━━━━━━━━━━━━━━"
        )
        await bot.send_message(LOG_CHANNEL, text, parse_mode="HTML")
    except Exception as e:
        print(f"Log yuborishda xato: {e}")
