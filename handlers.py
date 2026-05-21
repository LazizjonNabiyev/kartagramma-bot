from aiogram import Router, F, Bot
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import os

from database import (
    update_profile, get_user, is_registered, is_premium,
    activate_premium, get_stats, get_all_users, get_recent_activity,
    log_action, PLANS
)
from channel_check import check_subscription, subscribe_keyboard, send_log

router = Router()

ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "123456789").split(",") if x.strip()]


# ── Holatlar ──────────────────────────────────────────────────────────────────

class RegisterStates(StatesGroup):
    enter_fullname = State()
    enter_age = State()


class PremiumStates(StatesGroup):
    choose_plan = State()
    confirm_payment = State()


# ── Klaviaturalar ─────────────────────────────────────────────────────────────

def main_menu_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🗺 Yo'l topish"), KeyboardButton(text="📍 Eng yaqin bekat")],
            [KeyboardButton(text="🔔 Eslatma"), KeyboardButton(text="👤 Profil")],
            [KeyboardButton(text="⭐️ Premium"), KeyboardButton(text="ℹ️ Ma'lumot")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Quyidagilardan birini tanlang 👇"
    )


def register_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="⬅️ Orqaga")]],
        resize_keyboard=True
    )


def premium_plans_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📅 Oylik — 15,000 so'm")],
            [KeyboardButton(text="📆 3 Oylik — 35,000 so'm")],
            [KeyboardButton(text="🗓 Yillik — 99,000 so'm")],
            [KeyboardButton(text="⬅️ Orqaga")],
        ],
        resize_keyboard=True
    )


def confirm_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ To'lovni tasdiqlash")],
            [KeyboardButton(text="❌ Bekor qilish")],
        ],
        resize_keyboard=True
    )


# ── Obuna tekshiruvi (callback) ───────────────────────────────────────────────

@router.callback_query(F.data == "check_subscription")
async def check_sub_callback(callback: CallbackQuery, bot: Bot):
    subscribed = await check_subscription(bot, callback.from_user.id)
    if subscribed:
        await callback.message.delete()
        await callback.message.answer(
            "✅ <b>Rahmat! Kanalga obuna bo'ldingiz!</b>\n\n"
            "Endi botdan foydalanishingiz mumkin.\n"
            "Ro'yxatdan o'tish uchun /register yuboring.",
            reply_markup=main_menu_kb(),
            parse_mode="HTML"
        )
    else:
        await callback.answer("❗ Siz hali obuna bo'lmagansiz!", show_alert=True)


# ── Ro'yxatdan o'tish ─────────────────────────────────────────────────────────

@router.message(Command("register"))
@router.message(F.text == "📝 Ro'yxatdan o'tish")
async def start_register(message: Message, state: FSMContext, bot: Bot):
    # Obuna tekshiruv
    subscribed = await check_subscription(bot, message.from_user.id)
    if not subscribed:
        await message.answer(
            "⚠️ <b>Botdan foydalanish uchun kanalga obuna bo'ling!</b>\n\n"
            "Obuna bo'lgach, <b>Obuna bo'ldim</b> tugmasini bosing 👇",
            reply_markup=subscribe_keyboard(),
            parse_mode="HTML"
        )
        return

    if is_registered(message.from_user.id):
        await message.answer(
            "✅ <b>Siz allaqachon ro'yxatdan o'tgansiz!</b>",
            reply_markup=main_menu_kb(),
            parse_mode="HTML"
        )
        return

    await state.set_state(RegisterStates.enter_fullname)
    await message.answer(
        "👋 <b>Kartagrammaga xush kelibsiz!</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "📝 <b>Ro'yxatdan o'tish</b>\n\n"
        "Ism va familiyangizni kiriting:\n"
        "<i>Masalan: Sardor Karimov</i>",
        reply_markup=register_kb(),
        parse_mode="HTML"
    )


@router.message(RegisterStates.enter_fullname)
async def process_fullname(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await state.clear()
        await message.answer("🏠 Bosh menyu", reply_markup=main_menu_kb())
        return

    name = message.text.strip()
    if len(name) < 3 or len(name) > 60:
        await message.answer("❗ Iltimos, to'liq ism-familiyangizni kiriting (3-60 harf)")
        return

    await state.update_data(full_name=name)
    await state.set_state(RegisterStates.enter_age)
    await message.answer(
        "✅ <b>" + name + "</b> — saqlandi!\n\n"
        "🎂 Yoshingizni kiriting:\n"
        "<i>Masalan: 22</i>",
        reply_markup=register_kb(),
        parse_mode="HTML"
    )


@router.message(RegisterStates.enter_age)
async def process_age(message: Message, state: FSMContext, bot: Bot):
    if message.text == "⬅️ Orqaga":
        await state.set_state(RegisterStates.enter_fullname)
        await message.answer("Ism va familiyangizni kiriting:", reply_markup=register_kb(), parse_mode="HTML")
        return

    try:
        age = int(message.text.strip())
        if age < 5 or age > 100:
            raise ValueError
    except ValueError:
        await message.answer("❗ Yoshingizni to'g'ri kiriting (5 dan 100 gacha)")
        return

    data = await state.get_data()
    full_name = data["full_name"]

    update_profile(message.from_user.id, full_name, age)
    log_action(message.from_user.id, "registered")

    # Log kanalga yuborish
    await send_log(bot, message.from_user.id, message.from_user.username, full_name, age)

    await state.clear()
    await message.answer(
        "🎉 <b>Ro'yxatdan o'tdingiz!</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "👤 Ism: <b>" + full_name + "</b>\n"
        "🎂 Yosh: <b>" + str(age) + "</b>\n"
        "📱 Username: @" + (message.from_user.username or "yoq") + "\n"
        "━━━━━━━━━━━━━━━━━━━\n\n"
        "🚀 Endi botdan to'liq foydalanishingiz mumkin!",
        reply_markup=main_menu_kb(),
        parse_mode="HTML"
    )


# ── Profil ────────────────────────────────────────────────────────────────────

@router.message(F.text == "👤 Profil")
async def show_profile(message: Message):
    user = get_user(message.from_user.id)
    if not user or not user.get("full_name"):
        await message.answer(
            "❗ Siz hali ro'yxatdan o'tmagansiz!\n\n"
            "/register buyrug'ini yuboring.",
            reply_markup=main_menu_kb(),
            parse_mode="HTML"
        )
        return

    prem = is_premium(message.from_user.id)
    if prem:
        expires = prem["expires_at"][:10]
        premium_text = "\n⭐️ Premium: <b>Faol</b> (tugash: " + expires + ")"
    else:
        premium_text = "\n⭐️ Premium: <b>Yo'q</b>"

    joined = (user.get("joined_at") or "")[:10]
    await message.answer(
        "👤 <b>Sizning profilingiz</b>\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "📛 Ism: <b>" + (user.get("full_name") or "—") + "</b>\n"
        "🎂 Yosh: <b>" + str(user.get("age") or "—") + "</b>\n"
        "📱 Username: @" + (message.from_user.username or "yoq") + "\n"
        "🆔 ID: <code>" + str(message.from_user.id) + "</code>\n"
        "📅 Qo'shilgan: <b>" + joined + "</b>"
        + premium_text + "\n"
        "━━━━━━━━━━━━━━━━━━━",
        reply_markup=main_menu_kb(),
        parse_mode="HTML"
    )


# ── Premium ───────────────────────────────────────────────────────────────────

@router.message(F.text == "⭐️ Premium")
async def show_premium(message: Message, state: FSMContext):
    prem = is_premium(message.from_user.id)
    if prem:
        expires = prem["expires_at"][:10]
        await message.answer(
            "⭐️ <b>Sizda Premium bor!</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            "📋 Tarif: <b>" + prem["plan"] + "</b>\n"
            "📅 Tugash: <b>" + expires + "</b>\n"
            "━━━━━━━━━━━━━━━━━━━\n\n"
            "🚀 <b>Premium imkoniyatlar:</b>\n"
            "• Cheksiz yo'l topish\n"
            "• GPS bekat real vaqt\n"
            "• Cheksiz eslatmalar\n"
            "• Marshrut tarixi\n"
            "• Tezroq javob",
            reply_markup=main_menu_kb(),
            parse_mode="HTML"
        )
        return

    await state.set_state(PremiumStates.choose_plan)
    await message.answer(
        "⭐️ <b>Premium obuna</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "🚀 <b>Nima beradi?</b>\n"
        "• Cheksiz yo'l topish\n"
        "• GPS bekat real vaqt\n"
        "• Cheksiz eslatmalar\n"
        "• Marshrut tarixi\n"
        "━━━━━━━━━━━━━━━━━━━\n\n"
        "💳 <b>Tarifni tanlang:</b>",
        reply_markup=premium_plans_kb(),
        parse_mode="HTML"
    )


@router.message(PremiumStates.choose_plan)
async def process_plan(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await state.clear()
        await message.answer("🏠 Bosh menyu", reply_markup=main_menu_kb())
        return

    plan_map = {
        "📅 Oylik — 15,000 so'm": "oylik",
        "📆 3 Oylik — 35,000 so'm": "3oylik",
        "🗓 Yillik — 99,000 so'm": "yillik",
    }
    plan_key = plan_map.get(message.text)
    if not plan_key:
        await message.answer("❗ Iltimos, tarifni tanlang!")
        return

    plan_info = PLANS[plan_key]
    await state.update_data(plan=plan_key)
    await state.set_state(PremiumStates.confirm_payment)

    await message.answer(
        "💳 <b>To'lov ma'lumotlari</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "📋 Tarif: <b>" + plan_info["label"] + "</b>\n"
        "💰 Narx: <b>" + str(plan_info["price"]) + " so'm</b>\n"
        "📅 Muddat: <b>" + str(plan_info["days"]) + " kun</b>\n"
        "━━━━━━━━━━━━━━━━━━━\n\n"
        "💳 <b>To'lov rekvizitlari:</b>\n"
        "Karta: <code>8600 **** **** 9898</code>\n"
        "Egasi: <b>Laziz Nabiyev</b>\n\n"
        "⚠️ To'lovdan so'ng <b>chekni adminga yuboring</b>\n"
        "Admin: @Technologeee\n\n"
        "✅ To'lov qilgandan so'ng tasdiqlang:",
        reply_markup=confirm_kb(),
        parse_mode="HTML"
    )


@router.message(PremiumStates.confirm_payment)
async def confirm_payment(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("❌ Bekor qilindi.", reply_markup=main_menu_kb())
        return

    if message.text == "✅ To'lovni tasdiqlash":
        data = await state.get_data()
        plan = data.get("plan")
        await message.answer(
            "⏳ <b>To'lovingiz tekshirilmoqda...</b>\n\n"
            "Admin tasdiqlashi keyin Premium faollashadi.\n"
            "Odatda <b>1-24 soat</b> ichida.\n\n"
            "📩 Chekni yubordingizmi? @Technologeee",
            reply_markup=main_menu_kb(),
            parse_mode="HTML"
        )
        log_action(message.from_user.id, "premium_request:" + str(plan))
        await state.clear()


# ── Admin buyruqlari ──────────────────────────────────────────────────────────

@router.message(Command("givepremium"))
async def give_premium(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    parts = message.text.split()
    if len(parts) != 3:
        await message.answer("❗ Format: /givepremium <user_id> <oylik|3oylik|yillik>")
        return
    try:
        target_id = int(parts[1])
        plan = parts[2]
        if plan not in PLANS:
            raise ValueError
    except ValueError:
        await message.answer("❗ Noto'g'ri format!")
        return
    activate_premium(target_id, plan)
    plan_info = PLANS[plan]
    await message.answer(
        "✅ <b>Premium berildi!</b>\n"
        "👤 User ID: <code>" + str(target_id) + "</code>\n"
        "📋 Tarif: <b>" + plan_info["label"] + "</b>",
        parse_mode="HTML"
    )


@router.message(Command("stats"))
async def admin_stats(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    s = get_stats()
    reg_pct = round(s["registered"] / max(s["total_users"], 1) * 100)
    prem_pct = round(s["active_premium"] / max(s["total_users"], 1) * 100)
    await message.answer(
        "📊 <b>Kartagramma Statistika</b>\n"
        "━━━━━━━━━━━━━━━━━━━\n\n"
        "👥 <b>Foydalanuvchilar:</b>\n"
        "   Jami: <b>" + str(s["total_users"]) + "</b>\n"
        "   Ro'yxatdan o'tgan: <b>" + str(s["registered"]) + "</b> (" + str(reg_pct) + "%)\n"
        "   Bugun: <b>" + str(s["today_joins"]) + "</b>\n\n"
        "⭐️ <b>Premium:</b>\n"
        "   Faol: <b>" + str(s["active_premium"]) + "</b> (" + str(prem_pct) + "%)\n\n"
        "📈 <b>Faollik:</b>\n"
        "   7 kun: <b>" + str(s["week_active"]) + "</b> faol\n\n"
        "💰 <b>Daromad:</b>\n"
        "   30 kun: <b>" + str(s["month_revenue"]) + " so'm</b>\n"
        "   Jami: <b>" + str(s["total_revenue"]) + " so'm</b>\n"
        "━━━━━━━━━━━━━━━━━━━",
        parse_mode="HTML"
    )


@router.message(Command("users"))
async def admin_users(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    users = get_all_users(limit=20)
    if not users:
        await message.answer("Hozircha foydalanuvchi yo'q.")
        return
    lines = ["👥 <b>So'nggi 20 foydalanuvchi:</b>\n"]
    for u in users:
        prem = "⭐️" if u.get("is_premium") else "👤"
        name = u.get("full_name") or "—"
        uname = "@" + u["username"] if u.get("username") else "—"
        age = str(u.get("age") or "—")
        joined = (u.get("joined_at") or "")[:10]
        lines.append(prem + " <b>" + name + "</b> | " + uname + " | " + age + " yosh | " + joined)
    await message.answer("\n".join(lines), parse_mode="HTML")


@router.message(Command("activity"))
async def admin_activity(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    logs = get_recent_activity(limit=15)
    if not logs:
        await message.answer("Faollik yo'q.")
        return
    lines = ["📈 <b>So'nggi faollik:</b>\n"]
    for l in logs:
        name = l.get("full_name") or ("ID:" + str(l["user_id"]))
        action = l.get("action", "")
        time = (l.get("logged_at") or "")[:16].replace("T", " ")
        lines.append("• <b>" + name + "</b> → " + action + " <i>(" + time + ")</i>")
    await message.answer("\n".join(lines), parse_mode="HTML")
