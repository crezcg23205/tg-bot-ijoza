# =============================================
#  database/db.py — SQLite (aiosqlite) bilan ishlash
# =============================================

import aiosqlite
import logging
from datetime import datetime
from config import DB_PATH

log = logging.getLogger(__name__)


async def init_db() -> None:
    """Jadval mavjud bo'lmasa yaratadi va migratsiyani amalga oshiradi."""
    async with aiosqlite.connect(DB_PATH) as db:
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
        
        # Jins ustunini tekshirish va agar mavjud bo'lmasa qo'shish (migration)
        try:
            async with db.execute("PRAGMA table_info(users)") as cursor:
                columns = await cursor.fetchall()
                column_names = [col[1] for col in columns]
                if "gender" not in column_names:
                    await db.execute("ALTER TABLE users ADD COLUMN gender TEXT DEFAULT 'Erkak'")
                    await db.commit()
                    log.info("Baza sxemasi yangilandi: 'gender' ustuni qo'shildi.")
        except Exception as e:
            log.warning("Migratsiyani tekshirishda xatolik: %s", e)


async def save_user(
    telegram_id: int,
    full_name: str,
    gender: str,
    group_name: str,
    book_name: str,
    test_status: str,
) -> None:
    """Yangi foydalanuvchi ma'lumotini saqlaydi yoki mavjud bo'lsa yangilaydi (UPDATE)."""
    created_at = datetime.now().strftime("%d.%m.%Y %H:%M")
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        # Avval foydalanuvchi mavjudligini tekshiramiz
        async with db.execute(
            "SELECT id FROM users WHERE telegram_id = ?",
            (telegram_id,),
        ) as cursor:
            row = await cursor.fetchone()
            
        if row:
            # Mavjud foydalanuvchi ma'lumotlarini yangilash
            await db.execute(
                """
                UPDATE users
                SET full_name = ?, gender = ?, group_name = ?, book_name = ?, test_status = ?, created_at = ?
                WHERE telegram_id = ?
                """,
                (full_name, gender, group_name, book_name, test_status, created_at, telegram_id),
            )
            log.info("Mavjud foydalanuvchi ma'lumotlari yangilandi: ID %s", telegram_id)
        else:
            # Yangi foydalanuvchi qo'shish
            await db.execute(
                """
                INSERT INTO users (telegram_id, full_name, gender, group_name, book_name, test_status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (telegram_id, full_name, gender, group_name, book_name, test_status, created_at),
            )
            log.info("Yangi foydalanuvchi qo'shildi: ID %s", telegram_id)
            
        await db.commit()


async def get_user(telegram_id: int) -> dict | None:
    """Muayyan foydalanuvchi ma'lumotlarini telegram_id orqali oladi."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM users WHERE telegram_id = ?",
            (telegram_id,),
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return dict(row)
            return None


async def get_all_users() -> list[dict]:
    """Barcha foydalanuvchilarni ro'yxatini qaytaradi."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users ORDER BY id ASC") as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


async def get_stats() -> dict:
    """Statistika ma'lumotlarini hisoblab qaytaradi."""
    async with aiosqlite.connect(DB_PATH) as db:
        # Jami ro'yxatdan o'tganlar soni
        async with db.execute("SELECT COUNT(*) FROM users") as cursor:
            row = await cursor.fetchone()
            total = row[0] if row else 0

        # Erkaklar soni
        async with db.execute("SELECT COUNT(*) FROM users WHERE gender = ?", ("Erkak",)) as cursor:
            row = await cursor.fetchone()
            men = row[0] if row else 0

        # Ayollar soni
        async with db.execute("SELECT COUNT(*) FROM users WHERE gender = ?", ("Ayol",)) as cursor:
            row = await cursor.fetchone()
            women = row[0] if row else 0

        # Kitoblar bo'yicha taqsimot
        async with db.execute(
            "SELECT book_name, COUNT(*) as cnt FROM users GROUP BY book_name ORDER BY cnt DESC"
        ) as cursor:
            rows = await cursor.fetchall()
            books = {r[0]: r[1] for r in rows}

        # Guruhlar bo'yicha taqsimot
        async with db.execute(
            "SELECT group_name, COUNT(*) as cnt FROM users GROUP BY group_name ORDER BY cnt DESC"
        ) as cursor:
            rows = await cursor.fetchall()
            groups = {r[0]: r[1] for r in rows}

    return {
        "total": total,
        "men": men,
        "women": women,
        "books": books,
        "groups": groups,
    }


async def clear_all_users() -> int:
    """Barcha foydalanuvchilar ma'lumotlarini o'chiradi. O'chirilgan qatorlar sonini qaytaradi."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cursor:
            row = await cursor.fetchone()
            count = row[0] if row else 0
        await db.execute("DELETE FROM users")
        # Auto-increment hisoblagichni ham tiklash
        await db.execute("DELETE FROM sqlite_sequence WHERE name='users'")
        await db.commit()
        log.info("Barcha foydalanuvchilar bazadan o'chirildi. Jami: %d", count)
        return count
