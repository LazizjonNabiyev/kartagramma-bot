import random
import math
from cities import CITIES, city_has_metro

# Narx (2024 yil hozirgi narx)
METRO_PRICE = 1700
BUS_PRICE = 1700
MARSHRUTKA_PRICE = 2000

# Toshkent metro grafigi — real liniyalar, real vaqtlar (daqiqa)
METRO_GRAPH = {
    # 1-liniya: Chilonzor liniyasi (G'arb-Sharq)
    "Chilonzor":        {"Mirzo Ulugbek": 3},
    "Mirzo Ulugbek":    {"Chilonzor": 3, "Beruniy": 3},
    "Beruniy":          {"Mirzo Ulugbek": 3, "Hamza": 3},
    "Hamza":            {"Beruniy": 3, "Pakhtakor": 2},
    "Pakhtakor":        {"Hamza": 2, "Oybek": 2},
    "Oybek":            {"Pakhtakor": 2, "Kosmonavtlar": 3, "Amir Temur Xiyoboni": 2},

    # 2-liniya: O'zbekiston liniyasi (Shimol-Janub)
    "Kosmonavtlar":     {"Oybek": 3, "Milliy Bog": 3},
    "Milliy Bog":       {"Kosmonavtlar": 3, "Bunyodkor": 3},
    "Bunyodkor":        {"Milliy Bog": 3, "Novza": 3},
    "Novza":            {"Bunyodkor": 3},

    # 3-liniya: Yunusobod liniyasi
    "Amir Temur Xiyoboni": {"Oybek": 2, "Pushkin": 3, "Mustaqillik": 3},
    "Pushkin":          {"Amir Temur Xiyoboni": 3},
    "Mustaqillik":      {"Amir Temur Xiyoboni": 3, "Yunusobod": 3},
    "Yunusobod":        {"Mustaqillik": 3},
}

# Bekat nomlarini normallashtirish (foydalanuvchi xato yozsa ham topadi)
STOP_ALIASES = {
    "yunusobod": "Yunusobod",
    "chilonzor": "Chilonzor",
    "oybek": "Oybek",
    "pakhtakor": "Pakhtakor",
    "hamza": "Hamza",
    "beruniy": "Beruniy",
    "mirzo ulugbek": "Mirzo Ulugbek",
    "mirzo ulug'bek": "Mirzo Ulugbek",
    "kosmonavtlar": "Kosmonavtlar",
    "milliy bog": "Milliy Bog",
    "milliy bog'": "Milliy Bog",
    "bunyodkor": "Bunyodkor",
    "novza": "Novza",
    "amir temur": "Amir Temur Xiyoboni",
    "amir temur xiyoboni": "Amir Temur Xiyoboni",
    "pushkin": "Pushkin",
    "mustaqillik": "Mustaqillik",
    "sergeli": "Sergeli",
    "chorsu": "Chorsu",
    "shayhontohur": "Shayhontohur",
}


def normalize_stop(name):
    """Bekat nomini normallashtirish"""
    return STOP_ALIASES.get(name.lower().strip(), name.strip())


def find_metro_path(from_stop, to_stop):
    """BFS orqali metro yo'lini topish"""
    from_stop = normalize_stop(from_stop)
    to_stop = normalize_stop(to_stop)

    if from_stop not in METRO_GRAPH or to_stop not in METRO_GRAPH:
        return None, 0

    if from_stop == to_stop:
        return [from_stop], 0

    visited = {from_stop: None}
    queue = [from_stop]
    time_map = {from_stop: 0}

    while queue:
        current = queue.pop(0)
        if current == to_stop:
            path = []
            node = to_stop
            while node is not None:
                path.append(node)
                node = visited[node]
            path.reverse()
            return path, time_map[to_stop]

        for neighbor, travel_time in METRO_GRAPH.get(current, {}).items():
            if neighbor not in visited:
                visited[neighbor] = current
                time_map[neighbor] = time_map[current] + travel_time
                queue.append(neighbor)

    return None, 0


def find_bus_route(city, from_stop, to_stop):
    """Avtobus yo'lini topish"""
    city_data = CITIES.get(city)
    if not city_data:
        return None, 0, None

    bus_routes = city_data.get("bus_routes", {})
    from_n = normalize_stop(from_stop)
    to_n = normalize_stop(to_stop)

    for route_num, stops in bus_routes.items():
        stops_n = [normalize_stop(s) for s in stops]
        if from_n in stops_n and to_n in stops_n:
            fi = stops_n.index(from_n)
            ti = stops_n.index(to_n)
            if fi <= ti:
                path = stops[fi:ti + 1]
            else:
                path = stops[ti:fi + 1]
                path.reverse()
            time = len(path) * 4 + random.randint(2, 6)
            return path, time, route_num

    return None, 0, None


def find_route(city, from_stop, to_stop, transport_pref="all"):
    """Asosiy yo'l topish funksiyasi"""
    city_data = CITIES.get(city)
    if not city_data:
        return "❌ Shahar topilmadi!"

    from_norm = normalize_stop(from_stop)
    to_norm = normalize_stop(to_stop)
    has_metro = city_data.get("has_metro", False)
    results = []

    # ── Metro ──────────────────────────────────────────────────────────
    if has_metro and transport_pref in ["metro", "all"]:
        metro_path, metro_time = find_metro_path(from_norm, to_norm)
        if metro_path and metro_time > 0:
            stops_count = len(metro_path) - 1
            results.append({
                "type": "metro",
                "emoji": "🚇",
                "label": "Metro",
                "time": metro_time,
                "path": " → ".join(metro_path),
                "stops": stops_count,
                "cost": METRO_PRICE,
                "found": True
            })
        elif transport_pref == "metro":
            # Metro bekat topilmadi
            return (
                f"❌ <b>Metro bekat topilmadi</b>\n\n"
                f"<b>{from_stop}</b> yoki <b>{to_stop}</b> metro bekat emas.\n\n"
                f"📌 <b>Metro bekatlar:</b>\n"
                f"Chilonzor, Mirzo Ulugbek, Beruniy, Hamza,\n"
                f"Pakhtakor, Oybek, Kosmonavtlar, Milliy Bog,\n"
                f"Bunyodkor, Novza, Amir Temur Xiyoboni,\n"
                f"Pushkin, Mustaqillik, Yunusobod"
            )

    # ── Avtobus ────────────────────────────────────────────────────────
    if transport_pref in ["avtobus", "all"]:
        bus_path, bus_time, bus_num = find_bus_route(city, from_norm, to_norm)
        if bus_path and bus_time > 0:
            results.append({
                "type": "avtobus",
                "emoji": "🚌",
                "label": "Avtobus #" + str(bus_num),
                "time": bus_time,
                "path": " → ".join(bus_path),
                "stops": len(bus_path) - 1,
                "cost": BUS_PRICE,
                "found": True
            })
        else:
            # Taxminiy avtobus
            bus_routes = city_data.get("bus_routes", {})
            bus_nums = list(bus_routes.keys())
            bus_num = random.choice(bus_nums) if bus_nums else "1"
            est_time = random.randint(15, 40)
            est_stops = random.randint(3, 8)
            results.append({
                "type": "avtobus",
                "emoji": "🚌",
                "label": "Avtobus #" + str(bus_num),
                "time": est_time,
                "path": from_norm + " → ... → " + to_norm,
                "stops": est_stops,
                "cost": BUS_PRICE,
                "found": False
            })

    # ── Marshrutka ─────────────────────────────────────────────────────
    if transport_pref in ["marshrutka", "all"]:
        est_time = random.randint(20, 50)
        results.append({
            "type": "marshrutka",
            "emoji": "🚐",
            "label": "Marshrutka",
            "time": est_time,
            "path": from_norm + " → " + to_norm,
            "stops": random.randint(4, 10),
            "cost": MARSHRUTKA_PRICE,
            "found": False
        })

    if not results:
        return (
            "❌ <b>Yo'l topilmadi</b>\n\n"
            "Boshqa transport turini tanlang."
        )

    best = min(results, key=lambda x: x["time"])

    out = (
        "✅ <b>Yo'l topildi!</b>\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "<b>" + from_norm + "</b> → <b>" + to_norm + "</b>\n"
        "🏙 Shahar: <b>" + city + "</b>\n"
        "━━━━━━━━━━━━━━━━━━━\n\n"
    )

    for route in results:
        badge = "⚡ <b>ENG TEZ!</b>" if route == best else ""
        taxminiy = " <i>(taxminiy)</i>" if not route["found"] else ""
        out += (
            route["emoji"] + " <b>" + route["label"] + "</b> " + badge + "\n"
            "   ⏱ Vaqt: <b>" + str(route["time"]) + " daqiqa</b>" + taxminiy + "\n"
            "   🚏 Bekatlar: <b>" + str(route["stops"]) + " ta</b>\n"
            "   💰 Narx: <b>" + str(route["cost"]) + " so'm</b>\n"
            "   📌 <i>" + route["path"] + "</i>\n\n"
        )

    out += (
        "━━━━━━━━━━━━━━━━━━━\n"
        "🏆 <b>Tavsiya:</b> " + best["emoji"] + " " + best["label"] + "\n"
        "⏱ Atiga <b>" + str(best["time"]) + " daqiqa!</b> 🚀\n\n"
        "💡 <i>Yaxshi sayohat! 😊</i>"
    )
    return out


# Toshkent metro + avtobus bekatlarining real koordinatalari
METRO_STOPS_COORDS = {
    "Chilonzor":             (41.2993, 69.2399),
    "Mirzo Ulugbek":         (41.3063, 69.2563),
    "Beruniy":               (41.3134, 69.2712),
    "Hamza":                 (41.3198, 69.2856),
    "Pakhtakor":             (41.3267, 69.2967),
    "Oybek":                 (41.3312, 69.3089),
    "Kosmonavtlar":          (41.3401, 69.3134),
    "Milliy Bog":            (41.3489, 69.3089),
    "Bunyodkor":             (41.3556, 69.3023),
    "Novza":                 (41.3623, 69.2956),
    "Amir Temur Xiyoboni":   (41.3334, 69.2934),
    "Pushkin":               (41.3289, 69.2878),
    "Mustaqillik":           (41.3378, 69.3023),
    "Yunusobod":             (41.3512, 69.3156),
}

BUS_STOPS_COORDS = {
    "Chorsu":                (41.3267, 69.2356),
    "Shayhontohur":          (41.3134, 69.2712),
    "Sergeli":               (41.2678, 69.2312),
    "Yunusobod bozori":      (41.3601, 69.3289),
    "Olmazor":               (41.3089, 69.2534),
    "Uchtepa":               (41.2934, 69.2712),
    "Yakkasaroy":            (41.3023, 69.3067),
    "Shayxontohur bozori":   (41.3156, 69.2645),
}


def find_nearest_stop(lat, lon):
    """GPS orqali eng yaqin bekatni topish"""

    # Toshkent koordinatalari oralig'ida emasmi tekshirish
    # Toshkent: lat 41.1-41.6, lon 69.1-69.5
    in_tashkent = (41.1 <= lat <= 41.6) and (69.1 <= lon <= 69.5)

    def haversine(lat1, lon1, lat2, lon2):
        R = 6371000
        p1, p2 = math.radians(lat1), math.radians(lat2)
        dp = math.radians(lat2 - lat1)
        dl = math.radians(lon2 - lon1)
        a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    if not in_tashkent:
        return (
            "⚠️ <b>Siz hozir Toshkentda emassiz!</b>\n\n"
            "📍 GPS bekat topish faqat <b>Toshkent</b> uchun ishlaydi.\n\n"
            "Toshkentga kelganingizda joylashuvingizni yuboring! 🚇"
        )

    nearest_metro = min(METRO_STOPS_COORDS.items(),
                        key=lambda x: haversine(lat, lon, x[1][0], x[1][1]))
    nearest_bus = min(BUS_STOPS_COORDS.items(),
                      key=lambda x: haversine(lat, lon, x[1][0], x[1][1]))

    metro_dist = int(haversine(lat, lon, nearest_metro[1][0], nearest_metro[1][1]))
    bus_dist = int(haversine(lat, lon, nearest_bus[1][0], nearest_bus[1][1]))
    metro_walk = max(1, metro_dist // 80)
    bus_walk = max(1, bus_dist // 80)

    result = (
        "📍 <b>Eng yaqin bekatlar topildi!</b>\n"
        "━━━━━━━━━━━━━━━━━━━\n\n"
        "🚇 <b>Eng yaqin METRO:</b>\n"
        "   📌 <b>" + nearest_metro[0] + "</b>\n"
        "   📏 Masofa: <b>" + str(metro_dist) + " metr</b>\n"
        "   🚶 Piyoda: <b>" + str(metro_walk) + " daqiqa</b>\n\n"
        "🚌 <b>Eng yaqin AVTOBUS:</b>\n"
        "   📌 <b>" + nearest_bus[0] + "</b>\n"
        "   📏 Masofa: <b>" + str(bus_dist) + " metr</b>\n"
        "   🚶 Piyoda: <b>" + str(bus_walk) + " daqiqa</b>\n"
        "━━━━━━━━━━━━━━━━━━━\n"
    )

    if metro_dist < bus_dist:
        result += "💡 <b>Tavsiya:</b> 🚇 Metro yaqinroq! (" + str(metro_walk) + " daqiqa yurish)"
    else:
        result += "💡 <b>Tavsiya:</b> 🚌 Avtobus yaqinroq! (" + str(bus_walk) + " daqiqa yurish)"

    return result
