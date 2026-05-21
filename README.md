# 🚀 O'zbekiston Transport Bot

O'zbekistonning barcha viloyatlari uchun aqlli transport boti!

## ✨ Funksiyalar

- 🗺 **Yo'l topish** — Metro + Avtobus + Marshrutka
- 📍 **Eng yaqin bekat** — GPS orqali topish
- 🔔 **Eslatma** — Tushishni eslatib qo'yish
- 🏙 **14 ta viloyat** — Barcha O'zbekiston
- 🚇 Metro (Toshkent) + 🚌 Avtobus + 🚐 Marshrutka

---

## ⚡ Ishga tushirish (Railway — BEPUL)

### 1-qadam: GitHub
1. GitHub.com → New repository → "transport-bot"
2. Barcha fayllarni yuklang

### 2-qadam: Railway
1. **railway.app** ga kiring
2. "New Project" → "Deploy from GitHub"
3. Repozitoriyangizni tanlang
4. **Variables** bo'limiga kiring
5. Qo'shing:
   ```
   BOT_TOKEN = sizning_token_ingiz
   ```
6. Deploy! ✅

### 3-qadam: Test qiling
Telegram'da botingizni oching → `/start`

---

## 📁 Fayl strukturasi

```
transport_bot/
 ├── main.py          ← Asosiy bot logikasi
 ├── cities.py        ← Shaharlar ma'lumotlari
 ├── routes.py        ← Yo'l topish algoritmi
 ├── keyboards.py     ← Telegram tugmalari
 ├── messages.py      ← Bot xabarlari
 ├── requirements.txt ← Python kutubxonalar
 ├── Procfile         ← Railway uchun
 └── .env.example     ← Token namunasi
```

---

## 🏙 Qo'llab-quvvatlanadigan shaharlar

| Shahar | Metro | Avtobus | Marshrutka |
|--------|-------|---------|------------|
| Toshkent | ✅ | ✅ | ✅ |
| Samarqand | ❌ | ✅ | ✅ |
| Namangan | ❌ | ✅ | ✅ |
| Andijon | ❌ | ✅ | ✅ |
| Farg'ona | ❌ | ✅ | ✅ |
| Buxoro | ❌ | ✅ | ✅ |
| Qarshi | ❌ | ✅ | ✅ |
| Nukus | ❌ | ✅ | ✅ |
| Urganch | ❌ | ✅ | ✅ |
| Termiz | ❌ | ✅ | ✅ |
| Jizzax | ❌ | ✅ | ✅ |
| Navoiy | ❌ | ✅ | ✅ |
| Guliston | ❌ | ✅ | ✅ |
| Toshkent vil. | ❌ | ✅ | ✅ |

---

## 🔧 Local ishga tushirish

```bash
pip install -r requirements.txt
cp .env.example .env
# .env faylida BOT_TOKEN ni to'ldiring
python main.py
```

---

## 🚀 Keyingi yangilanishlar

- [ ] Real-time avtobus jadval (API)
- [ ] Foydalanuvchi sevimli marshrutlar
- [ ] Narx hisoblash (Uzcard)
- [ ] Ko'p til (O'z + Ru + En)
- [ ] Avtobus kelish vaqti (live)
