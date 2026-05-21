import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import os

from keyboards import city_selection_keyboard, transport_type_keyboard, back_button
from messages import CHOOSE_CITY_MSG, REMINDER_SET_MSG
from routes import find_route, find_nearest_stop
from cities import CITIES
from database import init_db, upsert_user, update_last_active, log_action, is_registered
from handlers import router as extra_router, main_menu_kb
from channel_check import check_subscription, subscribe_keyboard

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TOKEN")

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
dp.include_router(extra_router)


class RouteStates(StatesGroup):
    choosing_city = State()
    choosing_from = State()
    choosing_to = State()
    choosing_transport = State()


class NearestStopStates(StatesGroup):
    waiting_location = State()


class ReminderStates(StatesGroup):
    choosing_city = State()
    entering_route = State()
    entering_stops = State()


def register_only_kb():
    """Faqat ro'yxatdan o'tish tugmasi — menyu yo'q"""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📝 Ro'yxatdan o'tish")]],
        resize_keyboard=True
    )


# ── /start ─────────────────────────────────────────────────────────────────────
@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    upsert_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
        message.from_user.last_name,
    )

    # 1. Kanalga obuna tekshiruv
    subscribed = await check_subscription(bot, message.from_user.id)
    if not subscribed:
        await message.answer(
            "👋 <b>Salom, " + message.from_user.first_name + "!</b>\n\n"
            "🚀 <b>Kartagramma</b> — O'zbekiston transport boti\n\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            "⚠️ Botdan foydalanish uchun\n"
            "<b>kanalga obuna bo'ling!</b>\n"
            "━━━━━━━━━━━━━━━━━━━",
            reply_markup=subscribe_keyboard(),
            parse_mode="HTML"
        )
        return

    # 2. Ro'yxatdan o'tgan-o'tmaganligini tekshirish
    if not is_registered(message.from_user.id):
        await message.answer(
            "👋 <b>Salom, " + message.from_user.first_name + "!</b>\n\n"
            "🚀 <b>Kartagramma</b> — O'zbekiston transport boti\n\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            "📝 Botdan foydalanish uchun\n"
            "<b>ro'yxatdan o'ting!</b>\n"
            "━━━━━━━━━━━━━━━━━━━",
            reply_markup=register_only_kb(),
            parse_mode="HTML"
        )
        return

    # 3. Hamma narsa OK — menyu ko'rsatish
    await message.answer(
        "🚀 <b>Xush kelibsiz, " + message.from_user.first_name + "!</b>\n\n"
        "🏙 14 ta viloyat • 🚇 Metro • 🚌 Avtobus • 🚐 Marshrutka\n\n"
        "Quyidagilardan birini tanlang 👇",
        reply_markup=main_menu_kb(),
        parse_mode="HTML"
    )


# ── Middleware ────────────────────────────────────────────────────────────────
@dp.message.middleware()
async def track_activity(handler, message, data):
    uid = message.from_user.id
    update_last_active(uid)
    if message.text and not message.text.startswith("/"):
        log_action(uid, "msg:" + message.text[:30])
    return await handler(message, data)


# ── Menyu tugmalari — faqat ro'yxatdan o'tganlarga ───────────────────────────
async def require_registered(message: Message, bot: Bot) -> bool:
    """Ro'yxatdan o'tmaganlarni tekshirish"""
    subscribed = await check_subscription(bot, message.from_user.id)
    if not subscribed:
        await message.answer(
            "⚠️ Avval kanalga obuna bo'ling!",
            reply_markup=subscribe_keyboard(),
            parse_mode="HTML"
        )
        return False
    if not is_registered(message.from_user.id):
        await message.answer(
            "❗ Avval ro'yxatdan o'ting!",
            reply_markup=register_only_kb(),
            parse_mode="HTML"
        )
        return False
    return True


# ── Yo'l topish ────────────────────────────────────────────────────────────────
@dp.message(F.text == "🗺 Yo'l topish")
async def route_planner(message: Message, state: FSMContext):
    if not await require_registered(message, bot):
        return
    await state.set_state(RouteStates.choosing_city)
    await message.answer(CHOOSE_CITY_MSG, reply_markup=city_selection_keyboard(), parse_mode="HTML")


@dp.message(F.text == "📍 Eng yaqin bekat")
async def nearest_stop(message: Message, state: FSMContext):
    if not await require_registered(message, bot):
        return
    await state.set_state(NearestStopStates.waiting_location)
    await message.answer(
        "📍 <b>Joylashuvingizni yuboring!</b>\n\nPastdagi 📎 → <b>Location</b>",
        reply_markup=back_button(), parse_mode="HTML"
    )


@dp.message(F.text == "🔔 Eslatma")
async def reminder_menu(message: Message, state: FSMContext):
    if not await require_registered(message, bot):
        return
    await state.set_state(ReminderStates.choosing_city)
    await message.answer(
        "🔔 <b>Tushish eslatmasi</b>\n\nShaharni tanlang:",
        reply_markup=city_selection_keyboard(), parse_mode="HTML"
    )


@dp.message(F.text == "ℹ️ Ma'lumot")
async def info_menu(message: Message):
    await message.answer(
        "ℹ️ <b>Kartagramma haqida</b>\n\n"
        "🚇 Metro • 🚌 Avtobus • 🚐 Marshrutka\n"
        "🏙 14 ta viloyat\n\n"
        "📌 <b>Funksiyalar:</b>\n"
        "• 🗺 Yo'l topish\n"
        "• 📍 Eng yaqin bekat\n"
        "• 🔔 Eslatma\n"
        "• ⭐️ Premium\n\n"
        "👨‍💻 @Technologeee",
        reply_markup=main_menu_kb(), parse_mode="HTML"
    )


# ── Route flow ────────────────────────────────────────────────────────────────
@dp.message(RouteStates.choosing_city)
async def process_city(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await state.clear()
        await message.answer("🏠 Bosh menyu", reply_markup=main_menu_kb())
        return
    city = message.text.strip()
    city_clean = city.split(" ", 1)[-1] if " " in city else city
    if city_clean not in CITIES:
        await message.answer("❗ Ro'yxatdan shahar tanlang!")
        return
    await state.update_data(city=city_clean)
    stops = CITIES[city_clean]["stops"]
    await state.set_state(RouteStates.choosing_from)
    await message.answer(
        "🏙 <b>" + city_clean + "</b>\n\n📍 <b>Qayerdan?</b>\n<i>Masalan: " + stops[0] + "</i>",
        reply_markup=back_button(), parse_mode="HTML"
    )


@dp.message(RouteStates.choosing_from)
async def process_from(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await state.set_state(RouteStates.choosing_city)
        await message.answer(CHOOSE_CITY_MSG, reply_markup=city_selection_keyboard(), parse_mode="HTML")
        return
    await state.update_data(from_stop=message.text.strip())
    await state.set_state(RouteStates.choosing_to)
    await message.answer("🏁 <b>Qayerga?</b>", reply_markup=back_button(), parse_mode="HTML")


@dp.message(RouteStates.choosing_to)
async def process_to(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await state.set_state(RouteStates.choosing_from)
        await message.answer("📍 <b>Qayerdan?</b>", reply_markup=back_button(), parse_mode="HTML")
        return
    data = await state.get_data()
    if data["from_stop"].lower() == message.text.strip().lower():
        await message.answer("❗ Boshlang'ich va tugash bir xil bo'lmasin!")
        return
    await state.update_data(to_stop=message.text.strip())
    transports = CITIES[data["city"]]["transport_types"]
    await state.set_state(RouteStates.choosing_transport)
    await message.answer("🚌 <b>Transport turini tanlang:</b>",
                         reply_markup=transport_type_keyboard(transports), parse_mode="HTML")


@dp.message(RouteStates.choosing_transport)
async def process_transport(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await state.set_state(RouteStates.choosing_to)
        await message.answer("🏁 <b>Qayerga?</b>", parse_mode="HTML")
        return
    transport = "all"
    if "Metro" in message.text: transport = "metro"
    elif "Avtobus" in message.text: transport = "avtobus"
    elif "Marshrutka" in message.text: transport = "marshrutka"

    data = await state.get_data()
    await message.answer("⏳ <b>Yo'l hisoblanmoqda...</b>", parse_mode="HTML")
    result = find_route(data["city"], data["from_stop"], data["to_stop"], transport)
    log_action(message.from_user.id, "route:" + data["from_stop"] + "->" + data["to_stop"])
    await message.answer(result, reply_markup=main_menu_kb(), parse_mode="HTML")
    await state.clear()


# ── GPS ───────────────────────────────────────────────────────────────────────
@dp.message(NearestStopStates.waiting_location, F.location)
async def process_location(message: Message, state: FSMContext):
    await message.answer("📡 <b>Qidirilmoqda...</b>", parse_mode="HTML")
    result = find_nearest_stop(message.location.latitude, message.location.longitude)
    log_action(message.from_user.id, "nearest_stop")
    await message.answer(result, reply_markup=main_menu_kb(), parse_mode="HTML")
    await state.clear()


@dp.message(NearestStopStates.waiting_location)
async def location_text(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await state.clear()
        await message.answer("🏠 Bosh menyu", reply_markup=main_menu_kb())
        return
    await message.answer("📍 Location tugmasini bosing!", parse_mode="HTML")


# ── Eslatma flow ──────────────────────────────────────────────────────────────
@dp.message(ReminderStates.choosing_city)
async def reminder_city(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await state.clear()
        await message.answer("🏠 Bosh menyu", reply_markup=main_menu_kb())
        return
    city = message.text.strip()
    city_clean = city.split(" ", 1)[-1] if " " in city else city
    if city_clean not in CITIES:
        await message.answer("❗ Ro'yxatdan shahar tanlang!")
        return
    await state.update_data(city=city_clean)
    await state.set_state(ReminderStates.entering_route)
    await message.answer(
        "🔔 Marshrutingizni yozing:\n<i>Masalan: Chilonzor → Yunusobod</i>",
        reply_markup=back_button(), parse_mode="HTML"
    )


@dp.message(ReminderStates.entering_route)
async def reminder_route(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await state.set_state(ReminderStates.choosing_city)
        await message.answer(CHOOSE_CITY_MSG, reply_markup=city_selection_keyboard(), parse_mode="HTML")
        return
    await state.update_data(route=message.text.strip())
    await state.set_state(ReminderStates.entering_stops)
    await message.answer(
        "🔢 Necha bekatdan keyin tushishingiz kerak?\n<i>Masalan: 3</i>",
        reply_markup=back_button(), parse_mode="HTML"
    )


@dp.message(ReminderStates.entering_stops)
async def reminder_stops(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await state.set_state(ReminderStates.entering_route)
        await message.answer("Marshrutingizni yozing:", reply_markup=back_button(), parse_mode="HTML")
        return
    try:
        stops_count = int(message.text.strip())
        if stops_count < 1 or stops_count > 50: raise ValueError
    except ValueError:
        await message.answer("❗ 1 dan 50 gacha raqam kiriting")
        return
    data = await state.get_data()
    log_action(message.from_user.id, "reminder:" + data["route"])
    await message.answer(
        REMINDER_SET_MSG.format(route=data["route"], stops=stops_count),
        reply_markup=main_menu_kb(), parse_mode="HTML"
    )
    await state.clear()


@dp.message(F.text == "⬅️ Orqaga")
async def go_back(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("🏠 Bosh menyu", reply_markup=main_menu_kb())


async def main():
    init_db()
    logger.info("Kartagramma ishga tushdi!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
