# O'zbekiston shaharlari va transport ma'lumotlari

CITIES = {
    "Toshkent": {
        "emoji": "🏙",
        "transport_types": ["metro", "avtobus", "marshrutka"],
        "has_metro": True,
        "stops": [
            "Chilonzor", "Yunusobod", "Mirzo Ulug'bek", "Sergeli",
            "Shayhontohur", "Yakkasaroy", "Hamza", "Oybek",
            "Kosmonavtlar", "Tinchlik", "Bunyodkor", "Novza",
            "Ming O'rik", "Chorsu", "Alisher Navoiy", "Pakhtakor",
            "Mustaqillik", "Amir Temur Xiyoboni", "Milliy Bog'",
            "O'zbekiston", "Bodomzor", "Do'stlik", "Olmachi",
            "Pushkin", "Sobir Rahimov", "Akademgorodok",
            "Beruniy", "Abay", "Dushanbe Ko'chasi"
        ],
        "metro_lines": {
            "1-liniya (Chilonzor)": ["Oybek", "Pakhtakor", "Hamza", "Beruniy", "Mirzo Ulug'bek", "Chilonzor"],
            "2-liniya (O'zbekiston)": ["Oybek", "Kosmonavtlar", "Milliy Bog'", "Bunyodkor", "Novza"],
            "3-liniya (Yunusobod)": ["Amir Temur Xiyoboni", "Pushkin", "Mustakillik", "Yunusobod"]
        },
        "bus_routes": {
            "11": ["Chilonzor", "Shayhontohur", "Chorsu"],
            "15": ["Mirzo Ulug'bek", "Oybek", "Yunusobod"],
            "27": ["Sergeli", "Hamza", "Tinchlik"],
            "45": ["Novza", "Bunyodkor", "Akademgorodok"],
            "67": ["Olmachi", "Do'stlik", "Bodomzor"],
        }
    },

    "Samarqand": {
        "emoji": "🏛",
        "transport_types": ["avtobus", "marshrutka"],
        "has_metro": False,
        "stops": [
            "Registon", "Siyob Bozori", "Universitetlar", "Xorazm Ko'chasi",
            "Darg'om", "Bog'ishamol", "Aeroport", "Temir yo'l stantsiyasi",
            "Markaz", "Afrosiyob", "Bulung'ur ko'chasi", "Qo'shmas",
            "Eski shahar", "Ibn Sino", "Spitamen"
        ],
        "bus_routes": {
            "1": ["Registon", "Universitetlar", "Aeroport"],
            "4": ["Siyob Bozori", "Markaz", "Temir yo'l stantsiyasi"],
            "7": ["Afrosiyob", "Ibn Sino", "Darg'om"],
            "12": ["Eski shahar", "Registon", "Bog'ishamol"],
        }
    },

    "Namangan": {
        "emoji": "🌿",
        "transport_types": ["avtobus", "marshrutka"],
        "has_metro": False,
        "stops": [
            "Markaz", "Yangi shahar", "Kosonsoy ko'chasi", "Uychi",
            "Buvayda", "Tojiobod", "Aeroport", "Temir yo'l",
            "Namangan-2", "Olmachi", "Buvayda bozori", "Poytaxt"
        ],
        "bus_routes": {
            "2": ["Markaz", "Yangi shahar", "Aeroport"],
            "5": ["Uychi", "Kosonsoy ko'chasi", "Temir yo'l"],
            "9": ["Buvayda", "Markaz", "Olmachi"],
        }
    },

    "Andijon": {
        "emoji": "🌾",
        "transport_types": ["avtobus", "marshrutka"],
        "has_metro": False,
        "stops": [
            "Markaz", "Bobur xiyoboni", "Andijon-1", "Shahrixon",
            "Xo'jaobod", "Yangiqo'rg'on", "Aeroport", "Dehqonobod",
            "Asaka yo'nalishi", "Bozorlar", "Ulug'bek ko'chasi"
        ],
        "bus_routes": {
            "3": ["Markaz", "Bobur xiyoboni", "Aeroport"],
            "6": ["Shahrixon", "Markaz", "Andijon-1"],
            "11": ["Xo'jaobod", "Yangiqo'rg'on", "Dehqonobod"],
        }
    },

    "Farg'ona": {
        "emoji": "🍇",
        "transport_types": ["avtobus", "marshrutka"],
        "has_metro": False,
        "stops": [
            "Markaz", "Farg'ona-1", "Farg'ona-2", "Quvasoy",
            "Marg'ilon", "Rishton yo'nalishi", "Aeroport",
            "Bog'dod ko'chasi", "Kommunistlar xiyoboni", "Yangi turar joy"
        ],
        "bus_routes": {
            "1": ["Markaz", "Marg'ilon", "Quvasoy"],
            "8": ["Farg'ona-1", "Aeroport", "Rishton yo'nalishi"],
            "14": ["Yangi turar joy", "Markaz", "Farg'ona-2"],
        }
    },

    "Buxoro": {
        "emoji": "🕌",
        "transport_types": ["avtobus", "marshrutka"],
        "has_metro": False,
        "stops": [
            "Ark qal'a", "Lyabi Hovuz", "Kalon masjid", "Buxoro-1",
            "Yangi Buxoro", "Kogon", "Aeroport", "Markaz",
            "Karvon saroy", "Qo'shma", "G'ijduvon yo'nalishi"
        ],
        "bus_routes": {
            "2": ["Markaz", "Ark qal'a", "Aeroport"],
            "5": ["Kogon", "Yangi Buxoro", "Buxoro-1"],
            "10": ["G'ijduvon yo'nalishi", "Markaz", "Karvon saroy"],
        }
    },

    "Qarshi": {
        "emoji": "🏜",
        "transport_types": ["avtobus", "marshrutka"],
        "has_metro": False,
        "stops": [
            "Markaz", "Qarshi-1", "Shahrisabz yo'nalishi",
            "Yangi shahar", "Aeroport", "G'uzor ko'chasi",
            "Kasbi yo'nalishi", "Bozor"
        ],
        "bus_routes": {
            "3": ["Markaz", "Aeroport", "Yangi shahar"],
            "7": ["Bozor", "Qarshi-1", "G'uzor ko'chasi"],
        }
    },

    "Nukus": {
        "emoji": "🏝",
        "transport_types": ["avtobus", "marshrutka"],
        "has_metro": False,
        "stops": [
            "Markaz", "Nukus-1", "Aeroport", "Yangi Nukus",
            "Berdaq ko'chasi", "Qorao'zak yo'nalishi", "Bozor",
            "Xalqobod", "Chimboy yo'nalishi"
        ],
        "bus_routes": {
            "1": ["Markaz", "Aeroport", "Nukus-1"],
            "4": ["Yangi Nukus", "Berdaq ko'chasi", "Bozor"],
        }
    },

    "Urganch": {
        "emoji": "🌊",
        "transport_types": ["avtobus", "marshrutka"],
        "has_metro": False,
        "stops": [
            "Markaz", "Urganch-1", "Xiva yo'nalishi", "Aeroport",
            "Yangi turar joy", "Bozor", "Ko'hna Urganch yo'nalishi",
            "Shovot", "Gurlan yo'nalishi"
        ],
        "bus_routes": {
            "2": ["Markaz", "Xiva yo'nalishi", "Aeroport"],
            "6": ["Bozor", "Urganch-1", "Shovot"],
        }
    },

    "Termiz": {
        "emoji": "🌞",
        "transport_types": ["avtobus", "marshrutka"],
        "has_metro": False,
        "stops": [
            "Markaz", "Termiz-1", "Aeroport", "Denov yo'nalishi",
            "Sherobod yo'nalishi", "Yangi shahar", "Bozor",
            "Surxondaryo ko'chasi"
        ],
        "bus_routes": {
            "1": ["Markaz", "Aeroport", "Yangi shahar"],
            "5": ["Bozor", "Termiz-1", "Denov yo'nalishi"],
        }
    },

    "Jizzax": {
        "emoji": "🌄",
        "transport_types": ["avtobus", "marshrutka"],
        "has_metro": False,
        "stops": [
            "Markaz", "Jizzax-1", "Yangiobod", "Baxmal yo'nalishi",
            "Zomin yo'nalishi", "Aeroport", "Bozor", "Yangi shahar"
        ],
        "bus_routes": {
            "3": ["Markaz", "Yangiobod", "Bozor"],
            "7": ["Baxmal yo'nalishi", "Jizzax-1", "Yangi shahar"],
        }
    },

    "Navoiy": {
        "emoji": "⚗️",
        "transport_types": ["avtobus", "marshrutka"],
        "has_metro": False,
        "stops": [
            "Markaz", "Navoiy-1", "Karmana", "Zarafshon yo'nalishi",
            "Uchquduq yo'nalishi", "Sanoat zona", "Bozor", "Yangi shahar"
        ],
        "bus_routes": {
            "2": ["Markaz", "Sanoat zona", "Bozor"],
            "6": ["Navoiy-1", "Karmana", "Zarafshon yo'nalishi"],
        }
    },

    "Guliston": {
        "emoji": "🌸",
        "transport_types": ["avtobus", "marshrutka"],
        "has_metro": False,
        "stops": [
            "Markaz", "Guliston-1", "Yangiyer yo'nalishi",
            "Sirdaryo ko'chasi", "Bozor", "Yangi turar joy",
            "Boyovut yo'nalishi"
        ],
        "bus_routes": {
            "1": ["Markaz", "Bozor", "Yangiyer yo'nalishi"],
            "4": ["Guliston-1", "Sirdaryo ko'chasi", "Boyovut yo'nalishi"],
        }
    },

    "Toshkent vil.": {
        "emoji": "🏡",
        "transport_types": ["avtobus", "marshrutka"],
        "has_metro": False,
        "stops": [
            "Nurafshon", "Chirchiq", "Ohangaron", "Angren",
            "Bekobod", "Yangiyo'l", "Qibray", "Zangiota",
            "Bo'ka", "Parkent", "Piskent", "Toytepa"
        ],
        "bus_routes": {
            "101": ["Nurafshon", "Chirchiq", "Ohangaron"],
            "105": ["Yangiyo'l", "Qibray", "Zangiota"],
            "110": ["Bekobod", "Angren", "Parkent"],
        }
    }
}


def get_all_cities():
    return list(CITIES.keys())


def get_city_info(city_name):
    return CITIES.get(city_name, None)


def city_has_metro(city_name):
    city = CITIES.get(city_name)
    if city:
        return city.get("has_metro", False)
    return False
