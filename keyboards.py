from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from cities import CITIES


def main_menu():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🗺 Yo'l topish"),
                KeyboardButton(text="📍 Eng yaqin bekat"),
            ],
            [
                KeyboardButton(text="🔔 Eslatma"),
                KeyboardButton(text="ℹ️ Ma'lumot"),
            ]
        ],
        resize_keyboard=True,
        input_field_placeholder="Quyidagilardan birini tanlang 👇"
    )
    return keyboard


def city_selection_keyboard():
    city_list = list(CITIES.keys())
    city_emojis = {city: data["emoji"] for city, data in CITIES.items()}

    # 2 ta ustun qilib chiqarish
    rows = []
    row = []
    for city in city_list:
        emoji = city_emojis.get(city, "🏙")
        btn = KeyboardButton(text=f"{emoji} {city}")
        row.append(btn)
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)

    # Orqaga tugmasi
    rows.append([KeyboardButton(text="⬅️ Orqaga")])

    keyboard = ReplyKeyboardMarkup(
        keyboard=rows,
        resize_keyboard=True,
        input_field_placeholder="Shaharni tanlang 🏙"
    )
    return keyboard


def transport_type_keyboard(available_types):
    type_map = {
        "metro": "🚇 Metro",
        "avtobus": "🚌 Avtobus",
        "marshrutka": "🚐 Marshrutka",
    }

    rows = []
    for t in available_types:
        if t in type_map:
            rows.append([KeyboardButton(text=type_map[t])])

    rows.append([KeyboardButton(text="🔀 Hammasi (optimal)")])
    rows.append([KeyboardButton(text="⬅️ Orqaga")])

    keyboard = ReplyKeyboardMarkup(
        keyboard=rows,
        resize_keyboard=True,
        input_field_placeholder="Transport turini tanlang 🚌"
    )
    return keyboard


def back_button():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="⬅️ Orqaga")]],
        resize_keyboard=True
    )
    return keyboard


def confirm_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="✅ Ha, to'g'ri"),
                KeyboardButton(text="❌ Yo'q, qayta"),
            ],
            [KeyboardButton(text="⬅️ Orqaga")]
        ],
        resize_keyboard=True
    )
    return keyboard


def location_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📍 Joylashuvimni yuborish", request_location=True)],
            [KeyboardButton(text="⬅️ Orqaga")]
        ],
        resize_keyboard=True
    )
    return keyboard
