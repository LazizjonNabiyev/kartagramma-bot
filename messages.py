# Barcha xabarlar — chiroyli va dopaminli! 🔥

WELCOME_MSG = """
🚀 <b>Salom, {name}!</b>

<b>O'zbekiston Transport Bot</b>ga xush kelibsiz! 🇺🇿

━━━━━━━━━━━━━━━━━━━
🗺 <b>Yo'l topish</b> — eng tez marshrut
📍 <b>Eng yaqin bekat</b> — GPS orqali
🔔 <b>Eslatma</b> — tushishni unutma!
ℹ️ <b>Ma'lumot</b> — bot haqida
━━━━━━━━━━━━━━━━━━━

🏙 <b>14 ta viloyat</b> qo'llab-quvvatlanadi
🚇 Metro • 🚌 Avtobus • 🚐 Marshrutka

<i>Quyidagi tugmalardan birini tanlang 👇</i>
"""

CHOOSE_CITY_MSG = """
🏙 <b>Shahringizni tanlang!</b>

━━━━━━━━━━━━━━━━━━━
🚇 <b>Metro bor:</b> Toshkent
🚌 <b>Avtobus + Marshrutka:</b> Barcha viloyatlar
━━━━━━━━━━━━━━━━━━━

👇 Quyidan tanlang:
"""

CHOOSE_TRANSPORT_MSG = """
🚌 <b>Qanday transport bilan borasiz?</b>

Shaharingizda mavjud transportlar ko'rsatilgan 👇
"""

ROUTE_RESULT_MSG = """
✅ <b>Yo'l topildi!</b>
━━━━━━━━━━━━━━━━━━━
📍 {from_stop} → {to_stop}
━━━━━━━━━━━━━━━━━━━

{routes}

🏆 <b>Eng tez variant:</b> {best_route}
⚡ Atiga <b>{best_time} daqiqa!</b>

<i>Yaxshi sayohat! 😊</i>
"""

NEAREST_STOP_MSG = """
📍 <b>Eng yaqin bekatlar:</b>

🚇 <b>Metro:</b> {metro_stop}
   📏 {metro_dist} metr • 🚶 {metro_walk} daqiqa

🚌 <b>Avtobus:</b> {bus_stop}
   📏 {bus_dist} metr • 🚶 {bus_walk} daqiqa

💡 <b>Tavsiya:</b> {recommendation}
"""

REMINDER_SET_MSG = """
🔔 <b>Eslatma o'rnatildi!</b>

━━━━━━━━━━━━━━━━━━━
🗺 Marshrut: <b>{route}</b>
🚏 Tushish: <b>{stops} bekatdan keyin</b>
━━━━━━━━━━━━━━━━━━━

✅ Yo'lga chiqganingizda bot sizni <b>eslatib qo'yadi!</b>

⚠️ <i>Eslatma: Hozircha bu funksiya test rejimida.
Tez orada real-time ishlaydi! 🚀</i>
"""

ERROR_MSG = """
❌ <b>Xatolik yuz berdi!</b>

Iltimos, qaytadan urinib ko'ring yoki /start bosing.
"""

CITY_NOT_FOUND_MSG = """
❓ <b>Bu shahar topilmadi!</b>

Iltimos, ro'yxatdan shahar tanlang 👇
"""

NO_ROUTE_MSG = """
😔 <b>Yo'l topilmadi</b>

📍 <b>{from_stop}</b> → <b>{to_stop}</b>

Mumkin bo'lgan sabablar:
• Bekat nomi noto'g'ri
• Bu shahrda bu transport yo'q
• Bevosita yo'l yo'q

💡 <b>Maslahat:</b> "🔀 Hammasi (optimal)" tanlab ko'ring!
"""
