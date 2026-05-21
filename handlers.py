from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import os

from database import (
    update_profile, get_user, is_registered, is_premium,
    activate_premium, get_stats, get_all_users, get_recent_activity,
    log_action, PLANS
)

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


# ── Ro'yxatdan o'tish ─────────────────────────────────────────────────────────

@router.message(Command("register"))
@router.message(F.text == "📝 Ro'yxatdan o'tish")
async def start_register(message: Message, state: FSMContext):
    if is_registered(message.from_user.id):
        await message.answer(
            "✅ <b>Siz allaqachon ro'yxatdan o'tgansiz!</b>\n\n"
            "👤 Profilingizni ko'rish uchun <b>Profil</b> tugmasini bosing.",
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
    if not all(c.isalpha() or c.isspace() for c in name):
        await message.answer("❗ Faqat harf va bo'sh joy ishlating")
        return

    await state.update_data(full_name=name)
    await state.set_state(RegisterStates.enter_age)
    await message.answer(
        f"✅ <b>{name}</b> — saqlandi!\n\n"
        f"🎂 Yoshingizni kiriting:\n"
        f"<i>Masalan: 22</i>",
        reply_markup=register_kb(),
        parse_mode="HTML"
    )


@router.message(RegisterStates.enter_age)
async def process_age(message: Message, state: FSMContext):
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
    await state.clear()

    await message.answer(
        f"🎉 <b>Ro'yxatdan o'tdingiz!</b>\n\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"👤 Ism: <b>{full_name}</b>\n"
        f"🎂 Yosh: <b>{age}</b>\n"
        f"📱 Username: @{message.from_user.username or 'yoq'}\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
        f"🚀 Endi botdan to'liq foydalanishingiz mumkin!\n"
        f"⭐️ <b>Premium</b> olish uchun Premium tugmasini bosing.",
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
            "📝 Ro'yxatdan o'tish uchun /register buyrug'ini yuboring.",
            reply_markup=main_menu_kb(),
            parse_mode="HTML"
        )
        return

    prem = is_premium(message.from_user.id)
    premium_text = ""
    if prem:
        expires = prem["expires_at"][:10]
        premium_text = f"\n⭐️ Premium: <b>Faol</b> (tugash: {expires})"
    else:
        premium_text = "\n⭐️ Premium: <b>Yo'q</b>"

    joined = user.get("joined_at", "")[:10]

    await message.answer(
        f"👤 <b>Sizning profilingiz</b>\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"📛 Ism: <b>{user.get('full_name', '—')}</b>\n"
        f"🎂 Yosh: <b>{user.get('age', '—')}</b>\n"
        f"📱 Username: @{message.from_user.username or 'yoq'}\n"
        f"🆔 ID: <code>{message.from_user.id}</code>\n"
        f"📅 Qo'shilgan: <b>{joined}</b>"
        f"{premium_text}\n"
        f"━━━━━━━━━━━━━━━━━━━",
        reply_markup=main_menu_kb(),
        parse_mode="HTML"
    )


# ── Premium ───────────────────────────────────────────────────────────────────

@router.message(F.text == "⭐️ Premium")
async def show_premium(message: Message, state: FSMContext):
    prem = is_premium(message.from_user.id)

    if prem:
        expires = prem["expires_at"][:10]
        plan = prem["plan"]
        await message.answer(
            f"⭐️ <b>Sizda Premium bor!</b>\n\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"📋 Tarif: <b>{plan}</b>\n"
            f"📅 Tugash sanasi: <b>{expires}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━\n\n"
            f"🚀 <b>Premium imkoniyatlar:</b>\n"
            f"• 🗺 Cheksiz yo'l topish\n"
            f"• 📍 GPS bekat — real vaqt\n"
            f"• 🔔 Cheksiz eslatmalar\n"
            f"• 📊 Marshrut tarixi\n"
            f"• ⚡ Tezroq javob",
            reply_markup=main_menu_kb(),
            parse_mode="HTML"
        )
        return

    await state.set_state(PremiumStates.choose_plan)
    await message.answer(
        f"⭐️ <b>Premium obuna</b>\n\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"🚀 <b>Nima beradi?</b>\n"
        f"• Cheksiz yo'l topish\n"
        f"• GPS bekat — real vaqt\n"
        f"• Cheksiz eslatmalar\n"
        f"• Marshrut tarixi\n"
        f"• Tezroq javob\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
        f"💳 <b>Tarifni tanlang:</b>",
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
        f"💳 <b>To'lov ma'lumotlari</b>\n\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"📋 Tarif: <b>{plan_info['label']}</b>\n"
        f"💰 Narx: <b>{plan_info['price']:,} so'm</b>\n"
        f"📅 Muddat: <b>{plan_info['days']} kun</b>\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
        f"💳 <b>To'lov rekvizitlari:</b>\n"
        f"Karta: <code>8600 0000 0000 0000</code>\n"
        f"Ism: <b>KARTAGRAMMA BOT</b>\n\n"
        f"⚠️ To'lovdan so'ng <b>chekni adminga yuboring</b>\n"
        f"Admin: @kartagramma_admin\n\n"
        f"✅ To'lov qilgandan so'ng tasdiqlang:",
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
            f"⏳ <b>To'lovingiz tekshirilmoqda...</b>\n\n"
            f"Admin tasdiqlashi keyin Premium faollashadi.\n"
            f"Odatda <b>1-24 soat</b> ichida.\n\n"
            f"📩 Chekni yubordingizmi? @kartagramma_admin",
            reply_markup=main_menu_kb(),
            parse_mode="HTML"
        )
        log_action(message.from_user.id, f"premium_request:{plan}")
        await state.clear()


# ── Admin: Premium berish ─────────────────────────────────────────────────────

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
        f"✅ <b>Premium berildi!</b>\n"
        f"👤 User ID: <code>{target_id}</code>\n"
        f"📋 Tarif: <b>{plan_info['label']}</b>",
        parse_mode="HTML"
    )


# ── Admin: Statistika ─────────────────────────────────────────────────────────

@router.message(Command("stats"))
async def admin_stats(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ Ruxsat yo'q!")
        return

    s = get_stats()
    reg_pct = round(s["registered"] / max(s["total_users"], 1) * 100)
    prem_pct = round(s["active_premium"] / max(s["total_users"], 1) * 100)

    text = (
        f"📊 <b>Kartagramma Statistika</b>\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 <b>Foydalanuvchilar:</b>\n"
        f"   Jami: <b>{s['total_users']:,}</b>\n"
        f"   Ro'yxatdan o'tgan: <b>{s['registered']:,}</b> ({reg_pct}%)\n"
        f"   Bugun qo'shilgan: <b>{s['today_joins']}</b>\n\n"
        f"⭐️ <b>Premium:</b>\n"
        f"   Faol obunalar: <b>{s['active_premium']:,}</b> ({prem_pct}%)\n\n"
        f"📈 <b>Faollik:</b>\n"
        f"   So'nggi 7 kun: <b>{s['week_active']:,}</b> faol user\n\n"
        f"💰 <b>Daromad:</b>\n"
        f"   Oxirgi 30 kun: <b>{s['month_revenue']:,} so'm</b>\n"
        f"   Jami: <b>{s['total_revenue']:,} so'm</b>\n"
        f"━━━━━━━━━━━━━━━━━━━"
    )
    await message.answer(text, parse_mode="HTML")


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
        uname = f"@{u['username']}" if u.get("username") else "—"
        age = u.get("age") or "—"
        joined = (u.get("joined_at") or "")[:10]
        lines.append(
            f"{prem} <b>{name}</b> | {uname} | Yosh: {age} | {joined}"
        )

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
        name = l.get("full_name") or f"ID:{l['user_id']}"
        action = l.get("action", "")
        time = (l.get("logged_at") or "")[:16].replace("T", " ")
        lines.append(f"• <b>{name}</b> → {action} <i>({time})</i>")

    await message.answer("\n".join(lines), parse_mode="HTML")
