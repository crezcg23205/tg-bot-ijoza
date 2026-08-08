"""
Barcha 26 o'quvchini bazaga kiritish skripti.
"""
import asyncio
import aiosqlite
from datetime import datetime

DB_PATH = "certificate_bot.db"

students = [
    # ── ERKAKLAR ──────────────────────────────────────────────
    (10001, "Xojiyev Muhammadyusuf",        "Erkak", "2-guruh", "Al Alim va Mutaallim"),
    (10002, "Salyamov Muhammadamin",         "Erkak", "2-guruh", "Al Alim val Mutaallim"),
    (10003, "أحرارجان بن نذيرجان",           "Erkak", "1-guruh", "Al alim val mutaalim"),
    (10004, "Kosutov Edilbek",               "Erkak", "1-guruh", "Al alim val muta'allim"),
    (10005, "Мамашукуров Неъматуллох",       "Erkak", "1-guruh", "Al olim Val mutaallim"),
    (10006, "جورابيك بن ظفر",               "Erkak", "1-guruh", "Al alim val mutaalim"),
    (10007, "عبدالرحيم بن شهرت",            "Erkak", "1-guruh", "Al a'lim Val muta'allim"),
    (10008, "أحرار بن أنوار",               "Erkak", "1-guruh", "AlAlim val mutaalim"),
    (10009, "Mirzaliyev Islomjon",           "Erkak", "1-guruh", "Alalim valmutaallim"),
    (10010, "محمد عمر بن وليجان",           "Erkak", "1-guruh", "Alalim va mutaallim"),
    (10011, "عباس بن رستم",                 "Erkak", "1-guruh", "Al'alim val muta'allim"),
    (10012, "عبيدالله عبد المليك",          "Erkak", "1-guruh", "Maxazul Ilm"),
    (10013, "Muhammad Yunus Mamasidiqov",    "Erkak", "1-guruh", "Vasilatut talab"),
    # ── AYOLLAR ───────────────────────────────────────────────
    (10014, "Robiya Ibrohimova",             "Ayol",  "1-guruh", "Al aalim val mutaalim"),
    (10015, "نادرة بنت عباس",               "Ayol",  "1-guruh", "Ala'lim val mutaallim"),
    (10016, "برجين آي بنت إختيار",          "Ayol",  "1-guruh", "Ala'lim val mutaallim"),
    (10017, "مفطونة بنت  جمال الدين",       "Ayol",  "2-guruh", "Alim va mutaalim"),
    (10018, "Dilnoza Hasanova",              "Ayol",  "1-guruh", "Ala'lim val mutaallim"),
    (10019, "Abrorjonova Roziyaxon",         "Ayol",  "2-guruh", "Al alim val mutaallim"),
    (10020, "نيلوفر بنت محمد",              "Ayol",  "1-guruh", "Ala'limu val mutaallim"),
    (10021, "سبينة بنت خير الله",           "Ayol",  "2-guruh", "Al alim val mutaallim"),
    (10022, "Soliha Abdurahimova",           "Ayol",  "1-guruh", "Al-alim val mutaallim"),
    (10023, "فريدة بنت حيتعلي",             "Ayol",  "2-guruh", "Ala'lim val mutaalim"),
    (10024, "No'manova Sarvinozxon",         "Ayol",  "1-guruh", "Qur'oni Karim ilmlari"),
    (10025, "Aliyeva Muxlisa",              "Ayol",  "1-guruh", "Daloilul xoyrot"),
    (10026, "صالحة بنت غيرات ابن محمد",    "Ayol",  "1-guruh", "Al-alim val mutaallim"),
]

async def insert_all():
    created_at = datetime.now().strftime("%d.%m.%Y %H:%M")

    async with aiosqlite.connect(DB_PATH) as db:
        # Jadval yaratish (agar yo'q bo'lsa)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL,
                full_name   TEXT    NOT NULL,
                gender      TEXT    NOT NULL,
                group_name  TEXT    NOT NULL,
                book_name   TEXT    NOT NULL,
                test_status TEXT    NOT NULL DEFAULT 'Test topshirdim',
                created_at  TEXT    NOT NULL
            )
        """)
        await db.commit()

        # Bazani tozalaymiz
        await db.execute("DELETE FROM users")
        await db.execute("DELETE FROM sqlite_sequence WHERE name='users'")
        await db.commit()

        inserted = 0
        for tg_id, full_name, gender, group_name, book_name in students:
            # Mavjudligini tekshiramiz
            async with db.execute(
                "SELECT id FROM users WHERE telegram_id = ?", (tg_id,)
            ) as cursor:
                existing = await cursor.fetchone()

            if not existing:
                await db.execute(
                    """INSERT INTO users
                       (telegram_id, full_name, gender, group_name, book_name, test_status, created_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (tg_id, full_name, gender, group_name, book_name, "Test topshirdim", created_at),
                )
                inserted += 1
            else:
                pass

        await db.commit()

        async with db.execute("SELECT COUNT(*) FROM users") as cur:
            total = (await cur.fetchone())[0]

    print(f"Inserted: {inserted} | Total in DB: {total}")

asyncio.run(insert_all())
