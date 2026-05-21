import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = os.getenv("DB_PATH", "kartagramma.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()

    # Foydalanuvchilar jadvali
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id     INTEGER PRIMARY KEY,
            username    TEXT,
            first_name  TEXT,
            last_name   TEXT,
            full_name   TEXT,
            age         INTEGER,
            joined_at   TEXT,
            last_active TEXT,
            is_blocked  INTEGER DEFAULT 0
        )
    """)

    # Premium obunalar
    c.execute("""
        CREATE TABLE IF NOT EXISTS premium (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER,
            plan        TEXT,
            price       INTEGER,
            started_at  TEXT,
            expires_at  TEXT,
            is_active   INTEGER DEFAULT 1,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    """)

    # Faollik logi
    c.execute("""
        CREATE TABLE IF NOT EXISTS activity_log (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER,
            action     TEXT,
            logged_at  TEXT
        )
    """)

    # To'lovlar
    c.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER,
            amount     INTEGER,
            plan       TEXT,
            status     TEXT DEFAULT 'pending',
            paid_at    TEXT
        )
    """)

    conn.commit()
    conn.close()


# ── Foydalanuvchi ─────────────────────────────────────────────────────────────

def upsert_user(user_id, username, first_name, last_name):
    conn = get_conn()
    now = datetime.now().isoformat()
    conn.execute("""
        INSERT INTO users (user_id, username, first_name, last_name, joined_at, last_active)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            username=excluded.username,
            first_name=excluded.first_name,
            last_name=excluded.last_name,
            last_active=excluded.last_active
    """, (user_id, username or "", first_name or "", last_name or "", now, now))
    conn.commit()
    conn.close()


def update_profile(user_id, full_name, age):
    conn = get_conn()
    conn.execute("""
        UPDATE users SET full_name=?, age=? WHERE user_id=?
    """, (full_name, age, user_id))
    conn.commit()
    conn.close()


def get_user(user_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_last_active(user_id):
    conn = get_conn()
    conn.execute("UPDATE users SET last_active=? WHERE user_id=?",
                 (datetime.now().isoformat(), user_id))
    conn.commit()
    conn.close()


def is_registered(user_id):
    user = get_user(user_id)
    return user and user.get("full_name")


# ── Premium ───────────────────────────────────────────────────────────────────

PLANS = {
    "oylik": {"price": 15000, "days": 30, "label": "Oylik — 15,000 so'm"},
    "3oylik": {"price": 35000, "days": 90, "label": "3 oylik — 35,000 so'm"},
    "yillik": {"price": 99000, "days": 365, "label": "Yillik — 99,000 so'm"},
}


def activate_premium(user_id, plan):
    conn = get_conn()
    now = datetime.now()
    days = PLANS[plan]["days"]
    expires = (now + timedelta(days=days)).isoformat()
    price = PLANS[plan]["price"]

    # Eski premiumni o'chirish
    conn.execute("UPDATE premium SET is_active=0 WHERE user_id=?", (user_id,))

    conn.execute("""
        INSERT INTO premium (user_id, plan, price, started_at, expires_at, is_active)
        VALUES (?, ?, ?, ?, ?, 1)
    """, (user_id, plan, price, now.isoformat(), expires))

    conn.execute("""
        INSERT INTO payments (user_id, amount, plan, status, paid_at)
        VALUES (?, ?, ?, 'paid', ?)
    """, (user_id, price, plan, now.isoformat()))

    conn.commit()
    conn.close()


def is_premium(user_id):
    conn = get_conn()
    row = conn.execute("""
        SELECT * FROM premium
        WHERE user_id=? AND is_active=1 AND expires_at > ?
    """, (user_id, datetime.now().isoformat())).fetchone()
    conn.close()
    return dict(row) if row else None


def get_premium_info(user_id):
    return is_premium(user_id)


# ── Faollik ───────────────────────────────────────────────────────────────────

def log_action(user_id, action):
    conn = get_conn()
    conn.execute("""
        INSERT INTO activity_log (user_id, action, logged_at)
        VALUES (?, ?, ?)
    """, (user_id, action, datetime.now().isoformat()))
    conn.commit()
    conn.close()


# ── Admin statistika ──────────────────────────────────────────────────────────

def get_stats():
    conn = get_conn()
    now = datetime.now()
    today = now.date().isoformat()
    week_ago = (now - timedelta(days=7)).isoformat()
    month_ago = (now - timedelta(days=30)).isoformat()

    total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    registered = conn.execute("SELECT COUNT(*) FROM users WHERE full_name IS NOT NULL").fetchone()[0]
    active_premium = conn.execute("""
        SELECT COUNT(*) FROM premium WHERE is_active=1 AND expires_at > ?
    """, (now.isoformat(),)).fetchone()[0]
    today_joins = conn.execute("""
        SELECT COUNT(*) FROM users WHERE joined_at LIKE ?
    """, (f"{today}%",)).fetchone()[0]
    week_active = conn.execute("""
        SELECT COUNT(DISTINCT user_id) FROM activity_log WHERE logged_at > ?
    """, (week_ago,)).fetchone()[0]
    month_revenue = conn.execute("""
        SELECT COALESCE(SUM(amount), 0) FROM payments
        WHERE status='paid' AND paid_at > ?
    """, (month_ago,)).fetchone()[0]
    total_revenue = conn.execute("""
        SELECT COALESCE(SUM(amount), 0) FROM payments WHERE status='paid'
    """).fetchone()[0]

    conn.close()
    return {
        "total_users": total_users,
        "registered": registered,
        "active_premium": active_premium,
        "today_joins": today_joins,
        "week_active": week_active,
        "month_revenue": month_revenue,
        "total_revenue": total_revenue,
    }


def get_all_users(limit=50, offset=0):
    conn = get_conn()
    rows = conn.execute("""
        SELECT u.user_id, u.username, u.full_name, u.age, u.joined_at,
               CASE WHEN p.is_active=1 AND p.expires_at > datetime('now') THEN 1 ELSE 0 END as is_premium
        FROM users u
        LEFT JOIN premium p ON u.user_id = p.user_id
        ORDER BY u.joined_at DESC
        LIMIT ? OFFSET ?
    """, (limit, offset)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_recent_activity(limit=20):
    conn = get_conn()
    rows = conn.execute("""
        SELECT a.user_id, u.full_name, u.username, a.action, a.logged_at
        FROM activity_log a
        LEFT JOIN users u ON a.user_id = u.user_id
        ORDER BY a.logged_at DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]
