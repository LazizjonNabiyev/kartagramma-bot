import random
import math
from cities import CITIES, city_has_metro

# Toshkent metro grafigi (real liniyalar)
METRO_GRAPH = {
    # 1-liniya: Chilonzor liniyasi
    "Oybek": {"Pakhtakor": 2, "Kosmonavtlar": 3},
    "Pakhtakor": {"Oybek": 2, "Hamza": 2},
    "Hamza": {"Pakhtakor": 2, "Beruniy": 3},
    "Beruniy": {"Hamza": 3, "Mirzo Ulug'bek": 3},
    "Mirzo Ulug'bek": {"Beruniy": 3, "Chilonzor": 3},
    "Chilonzor": {"Mirzo Ulug'bek": 3},

    # 2-liniya: O'zbekiston liniyasi
    "Kosmonavtlar": {"Oybek": 3, "Milliy Bog'": 3},
    "Milliy Bog'": {"Kosmonavtlar": 3, "Bunyodkor": 4},
    "Bunyodkor": {"Milliy Bog'": 4, "Novza": 3},
    "Novza": {"Bunyodkor": 3},

    # 3-liniya: Yunusobod liniyasi
    "Amir Temur Xiyoboni": {"Pushkin": 3, "Mustaqillik": 3},
    "Pushkin": {"Amir Temur Xiyoboni": 3},
    "Mustaqillik": {"Amir Temur Xiyoboni": 3, "Yunusobod": 4},
    "Yunusobod": {"Mustaqillik": 4},
}


def find_metro_path(from_stop, to_stop):
    """BFS orqali metro yo'lini topish"""
    if from_stop not in METRO_GRAPH or to_stop not in METRO_GRAPH:
        return None, 0

    visited = {from_stop: None}
    queue = [from_stop]
    time_map = {from_stop: 0}

    while queue:
        current = queue.pop(0)
        if current == to_stop:
            # Yo'lni qayta tiklash
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

    for route_num, stops in bus_routes.items():
        if from_stop in stops and to_stop in stops:
            from_idx = stops.index(from_stop)
            to_idx = stops.index(to_stop)
            # Yo'nalishni to'g'irlash
            if from_idx <= to_idx:
                path = stops[from_idx:to_idx + 1]
            else:
                path = stops[to_idx:from_idx + 1]
                path.reverse()
            time = len(path) * 5 + random.randint(2, 8)
            return path, time, route_num

    return None, 0, None


def estimate_time(from_stop, to_stop, transport):
    """Taxminiy vaqt hisoblash"""
    base_time = random.randint(10, 45)
    if transport == "metro":
        return max(5, base_time - 10)
    elif transport == "marshrutka":
        return base_time + random.randint(5, 15)
    return base_time


def find_route(city, from_stop, to_stop, transport_pref="all"):
    """Asosiy yo'l topish funksiyasi"""
    city_data = CITIES.get(city)
    if not city_data:
        return "❌ Shahar topilmadi!"

    has_metro = city_data.get("has_metro", False)
    results = []

    # ── Metro yo'li ──────────────────────────────────────────────────
    if has_metro and transport_pref in ["metro", "all"]:
        metro_path, metro_time = find_metro_path(from_stop, to_stop)

        if metro_path and metro_time > 0:
            stops_count = len(metro_path) - 1
            path_str = " → ".join(metro_path)
            results.append({
                "type": "metro",
                "emoji": "🚇",
                "label": "Metro",
                "time": metro_time,
                "path": path_str,
                "stops": stops_count,
                "cost": 1400,
                "detail": f"{stops_count} bekat"
            })
        elif transport_pref == "metro":
            # Metro yo'li topilmasa, taxminiy hisoblash
            est_time = estimate_time(from_stop, to_stop, "metro")
            results.append({
                "type": "metro",
                "emoji": "🚇",
                "label": "Metro",
                "time": est_time,
                "path": f"{from_stop} → ... → {to_stop}",
                "stops": random.randint(2, 6),
                "cost": 1400,
                "detail": "Taxminiy yo'l"
            })

    # ── Avtobus yo'li ─────────────────────────────────────────────────
    if transport_pref in ["avtobus", "all"]:
        bus_path, bus_time, bus_num = find_bus_route(city, from_stop, to_stop)

        if bus_path and bus_time > 0:
            path_str = " → ".join(bus_path)
            results.append({
                "type": "avtobus",
                "emoji": "🚌",
                "label": f"Avtobus #{bus_num}",
                "time": bus_time,
                "path": path_str,
                "stops": len(bus_path) - 1,
                "cost": 1400,
                "detail": f"#{bus_num} avtobus"
            })
        elif transport_pref in ["avtobus", "all"]:
            # Taxminiy avtobus yo'li
            est_time = estimate_time(from_stop, to_stop, "avtobus")
            est_stops = random.randint(3, 8)
            # Random avtobus raqami
            bus_routes = city_data.get("bus_routes", {})
            bus_nums = list(bus_routes.keys())
            bus_num = random.choice(bus_nums) if bus_nums else "1"

            results.append({
                "type": "avtobus",
                "emoji": "🚌",
                "label": f"Avtobus #{bus_num}",
                "time": est_time,
                "path": f"{from_stop} → ... → {to_stop}",
                "stops": est_stops,
                "cost": 1400,
                "detail": f"#{bus_num} avtobus"
            })

    # ── Marshrutka ───────────────────────────────────────────────────
    if transport_pref in ["marshrutka", "all"]:
        est_time = estimate_time(from_stop, to_stop, "marshrutka")
        est_stops = random.randint(3, 10)
        results.append({
            "type": "marshrutka",
            "emoji": "🚐",
            "label": "Marshrutka",
            "time": est_time,
            "path": f"{from_stop} → ... → {to_stop}",
            "stops": est_stops,
            "cost": 1500,
            "detail": "To'g'ridan to'g'ri"
        })

    # ── Natijani formatlash ────────────────────────────────────────────
    if not results:
        return (
            f"❌ <b>Yo'l topilmadi</b>\n\n"
            f"📍 <b>{from_stop}</b> → <b>{to_stop}</b>\n\n"
            f"Iltimos, boshqa transport turini tanlang yoki bekat nomini tekshiring."
        )

    # Eng tez variant
    best = min(results, key=lambda x: x["time"])

    output = (
        f"✅ <b>Yo'l topildi!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"📍 <b>{from_stop}</b> → <b>{to_stop}</b>\n"
        f"🏙 Shahar: <b>{city}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
    )

    # Har bir variant
    for i, route in enumerate(results):
        is_best = route == best
        badge = "⚡ <b>ENG TEZ!</b>" if is_best else ""
        output += (
            f"{route['emoji']} <b>{route['label']}</b> {badge}\n"
            f"   ⏱ Vaqt: <b>{route['time']} daqiqa</b>\n"
            f"   🚏 Bekatlar: <b>{route['stops']} ta</b>\n"
            f"   💰 Narx: <b>{route['cost']:,} so'm</b>\n"
            f"   📌 Yo'l: <i>{route['path']}</i>\n\n"
        )

    output += (
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"🏆 <b>Tavsiya:</b> {best['emoji']} {best['label']}\n"
        f"⏱ Atiga <b>{best['time']} daqiqa!</b> 🚀\n\n"
        f"💡 <i>Yaxshi sayohat!</i> 😊"
    )

    return output


def find_nearest_stop(lat, lon):
    """GPS orqali eng yaqin bekatni topish"""

    # Toshkent metro bekatlarining taxminiy koordinatalari
    METRO_STOPS_COORDS = {
        "Chilonzor": (41.2995, 69.2401),
        "Mirzo Ulug'bek": (41.3118, 69.2627),
        "Beruniy": (41.3234, 69.2789),
        "Hamza": (41.3367, 69.2934),
        "Pakhtakor": (41.3445, 69.3067),
        "Oybek": (41.3512, 69.3201),
        "Kosmonavtlar": (41.3589, 69.3334),
        "Milliy Bog'": (41.3634, 69.3456),
        "Bunyodkor": (41.3556, 69.3589),
        "Novza": (41.3489, 69.3712),
        "Amir Temur Xiyoboni": (41.3423, 69.2845),
        "Mustaqillik": (41.3378, 69.3023),
        "Yunusobod": (41.3312, 69.3178),
        "Yunusobod": (41.3512, 69.3401),
        "Pushkin": (41.3289, 69.2967),
    }

    # Barcha shaharlardan bekatlar
    BUS_STOPS_COORDS = {
        "Chorsu": (41.3289, 69.2345),
        "Hamza (avtobus)": (41.3367, 69.2934),
        "Yunusobod bozori": (41.3612, 69.3401),
        "Sergeli": (41.2678, 69.2312),
        "Shayhontohur": (41.3134, 69.2712),
    }

    def haversine(lat1, lon1, lat2, lon2):
        R = 6371000  # metr
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    # Eng yaqin metro bekat
    nearest_metro = None
    min_metro_dist = float('inf')
    for stop, (slat, slon) in METRO_STOPS_COORDS.items():
        d = haversine(lat, lon, slat, slon)
        if d < min_metro_dist:
            min_metro_dist = d
            nearest_metro = stop

    # Eng yaqin avtobus bekat
    nearest_bus = None
    min_bus_dist = float('inf')
    for stop, (slat, slon) in BUS_STOPS_COORDS.items():
        d = haversine(lat, lon, slat, slon)
        if d < min_bus_dist:
            min_bus_dist = d
            nearest_bus = stop

    metro_dist_m = int(min_metro_dist)
    bus_dist_m = int(min_bus_dist)
    metro_walk_min = max(1, metro_dist_m // 80)
    bus_walk_min = max(1, bus_dist_m // 80)

    result = (
        f"📍 <b>Eng yaqin bekatlar topildi!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
        f"🚇 <b>Eng yaqin METRO:</b>\n"
        f"   📌 <b>{nearest_metro}</b>\n"
        f"   📏 Masofa: <b>{metro_dist_m:,} metr</b>\n"
        f"   🚶 Piyoda: <b>{metro_walk_min} daqiqa</b>\n\n"
        f"🚌 <b>Eng yaqin AVTOBUS:</b>\n"
        f"   📌 <b>{nearest_bus}</b>\n"
        f"   📏 Masofa: <b>{bus_dist_m:,} metr</b>\n"
        f"   🚶 Piyoda: <b>{bus_walk_min} daqiqa</b>\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
    )

    if metro_dist_m < bus_dist_m:
        result += f"💡 <b>Tavsiya:</b> 🚇 Metro yaqinroq! ({metro_walk_min} daqiqa yurish)"
    else:
        result += f"💡 <b>Tavsiya:</b> 🚌 Avtobus yaqinroq! ({bus_walk_min} daqiqa yurish)"

    return result
