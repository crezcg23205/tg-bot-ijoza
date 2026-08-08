# =============================================
#  handlers/admin.py — Admin handlerlari
# =============================================

import logging
from typing import Callable, Dict, Any, Awaitable

from aiogram import Router, F, BaseMiddleware
from aiogram.filters import Command
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    TelegramObject,
)

from config import ADMIN_IDS
from database import get_all_users, get_stats, clear_all_users

log = logging.getLogger(__name__)
admin_router = Router()


# ── Admin tekshiruvi uchun Middleware ─────────────────────────────────────────
class AdminMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        user = data.get("event_from_user")
        if not user or user.id not in ADMIN_IDS:
            if isinstance(event, Message):
                await event.answer("⛔ Sizda bu buyruqni ishlatish huquqi yo'q.")
            elif isinstance(event, CallbackQuery):
                await event.answer("⛔ Sizda admin huquqi yo'q.", show_alert=True)
            return
        return await handler(event, data)


# Middleware-larni routerga ulash
admin_router.message.middleware(AdminMiddleware())
admin_router.callback_query.middleware(AdminMiddleware())


# ── /admin ─────────────────────────────────────────────────────────────────────
@admin_router.message(Command("admin"))
async def cmd_admin(message: Message) -> None:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📋 Ro'yxatni ko'rish", callback_data="admin_royxat"),
                InlineKeyboardButton(text="📊 Statistika",        callback_data="admin_stats"),
            ],
            [
                InlineKeyboardButton(text="🗑️ Bazani tozalash",   callback_data="admin_clear_confirm"),
            ]
        ]
    )
    await message.answer(
        "👋 <b>Admin boshqaruv paneliga xush kelibsiz!</b>\n\n"
        "Kerakli amalni tanlang:",
        reply_markup=keyboard,
        parse_mode="HTML",
    )


# ── Ro'yxatni SMS xabar sifatida yuborish ─────────────────────────────────────
async def handle_royxat(message: Message) -> None:
    rows = await get_all_users()

    if not rows:
        await message.answer("📭 Hozircha hech qanday ma'lumot yo'q.")
        return

    erkaklar = [r for r in rows if r.get("gender") == "Erkak"]
    ayollar  = [r for r in rows if r.get("gender") == "Ayol"]

    # ── ERKAK O'QUVCHILAR ──────────────────────────────────────────────────────
    erkak_header = (
        f"👨 <b>ERKAK O'QUVCHILAR</b> — {len(erkaklar)} nafar\n"
        f"{'─' * 30}\n\n"
    )

    if erkaklar:
        erkak_lines = []
        for i, r in enumerate(erkaklar, 1):
            erkak_lines.append(
                f"<b>{i}.</b>\n"
                f"👤 Ism Sharif: <b>{r['full_name']}</b>\n"
                f"👨 Jinsi: <b>Erkak</b>\n"
                f"🏫 Guruh: <b>{r['group_name']}</b>\n"
                f"📖 Kitob: <b>{r['book_name']}</b>\n"
                f"✔️ Test: <b>Topshirildi</b>"
            )
        erkak_body = "\n\n".join(erkak_lines)
    else:
        erkak_body = "<i>Erkak o'quvchilar ro'yxatdan o'tmagan</i>"

    # ── AYOL O'QUVCHILAR ───────────────────────────────────────────────────────
    ayol_header = (
        f"\n\n👩 <b>AYOL O'QUVCHILAR</b> — {len(ayollar)} nafar\n"
        f"{'─' * 30}\n\n"
    )

    if ayollar:
        ayol_lines = []
        for i, r in enumerate(ayollar, 1):
            ayol_lines.append(
                f"<b>{i}.</b>\n"
                f"👤 Ism Sharif: <b>{r['full_name']}</b>\n"
                f"👩 Jinsi: <b>Ayol</b>\n"
                f"🏫 Guruh: <b>{r['group_name']}</b>\n"
                f"📖 Kitob: <b>{r['book_name']}</b>\n"
                f"✔️ Test: <b>Topshirildi</b>"
            )
        ayol_body = "\n\n".join(ayol_lines)
    else:
        ayol_body = "<i>Ayol o'quvchilar ro'yxatdan o'tmagan</i>"

    # Telegram xabar maksimal 4096 belgi — bo'laklarga bo'lamiz
    full_text = erkak_header + erkak_body + ayol_header + ayol_body

    # Xabarni yuborishdan oldin sarlavha
    await message.answer(
        f"📋 <b>O'QUVCHILAR RO'YXATI</b>\n"
        f"👥 Jami: <b>{len(rows)}</b> nafar "
        f"(👨 {len(erkaklar)} erkak + 👩 {len(ayollar)} ayol)",
        parse_mode="HTML",
    )

    # 4096 chegarasidan o'tmasligi uchun bo'laklarga bo'lib yuboramiz
    chunk_size = 4000
    chunks = []

    # Erkaklar xabari
    erkak_full = erkak_header + erkak_body
    if len(erkak_full) <= chunk_size:
        chunks.append(erkak_full)
    else:
        # Har bir o'quvchini alohida yuboramiz
        chunks.append(f"👨 <b>ERKAK O'QUVCHILAR</b> — {len(erkaklar)} nafar\n{'─'*30}")
        for i, r in enumerate(erkaklar, 1):
            chunks.append(
                f"<b>{i}.</b>\n"
                f"👤 Ism Sharif: <b>{r['full_name']}</b>\n"
                f"👨 Jinsi: <b>Erkak</b>\n"
                f"🏫 Guruh: <b>{r['group_name']}</b>\n"
                f"📖 Kitob: <b>{r['book_name']}</b>\n"
                f"✔️ Test: <b>Topshirildi</b>"
            )

    # Ayollar xabari
    ayol_full = f"👩 <b>AYOL O'QUVCHILAR</b> — {len(ayollar)} nafar\n{'─'*30}\n\n" + ayol_body
    if len(ayol_full) <= chunk_size:
        chunks.append(ayol_full)
    else:
        chunks.append(f"👩 <b>AYOL O'QUVCHILAR</b> — {len(ayollar)} nafar\n{'─'*30}")
        for i, r in enumerate(ayollar, 1):
            chunks.append(
                f"<b>{i}.</b>\n"
                f"👤 Ism Sharif: <b>{r['full_name']}</b>\n"
                f"👩 Jinsi: <b>Ayol</b>\n"
                f"🏫 Guruh: <b>{r['group_name']}</b>\n"
                f"📖 Kitob: <b>{r['book_name']}</b>\n"
                f"✔️ Test: <b>Topshirildi</b>"
            )

    for chunk in chunks:
        await message.answer(chunk, parse_mode="HTML")


@admin_router.message(Command("malumot"))
async def cmd_malumot(message: Message) -> None:
    await handle_royxat(message)


@admin_router.callback_query(F.data == "admin_royxat")
async def callback_admin_royxat(callback: CallbackQuery) -> None:
    await callback.answer()
    await handle_royxat(callback.message)


# ── /statistika ───────────────────────────────────────────────────────────────
async def handle_statistics_show(message: Message) -> None:
    stats = await get_stats()

    books_text = ""
    if stats["books"]:
        for book, count in stats["books"].items():
            books_text += f"  📖 {book}: <b>{count}</b> ta\n"
    else:
        books_text = "  <i>Ma'lumot mavjud emas</i>\n"

    groups_text = ""
    if stats["groups"]:
        for group, count in stats["groups"].items():
            groups_text += f"  🏫 {group}: <b>{count}</b> ta\n"
    else:
        groups_text = "  <i>Ma'lumot mavjud emas</i>\n"

    msg_text = (
        f"📊 <b>Statistika:</b>\n\n"
        f"👥 Jami o'quvchilar: <b>{stats['total']}</b>\n"
        f"👨 Erkaklar: <b>{stats['men']}</b>\n"
        f"👩 Ayollar: <b>{stats['women']}</b>\n\n"
        f"📚 <b>Kitoblar bo'yicha:</b>\n{books_text}\n"
        f"🏫 <b>Guruhlar bo'yicha:</b>\n{groups_text}"
    )
    await message.answer(msg_text, parse_mode="HTML")


@admin_router.message(Command("statistika"))
async def cmd_statistika(message: Message) -> None:
    await handle_statistics_show(message)


@admin_router.callback_query(F.data == "admin_stats")
async def callback_admin_stats(callback: CallbackQuery) -> None:
    await callback.answer()
    await handle_statistics_show(callback.message)


# ── /yangilash ────────────────────────────────────────────────────────────────
@admin_router.message(Command("yangilash"))
async def cmd_yangilash(message: Message) -> None:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Ha, barcha ma'lumotlarni o'chir",
                    callback_data="admin_clear_yes"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="❌ Yo'q, bekor qil",
                    callback_data="admin_clear_no"
                ),
            ]
        ]
    )
    await message.answer(
        "⚠️ <b>Diqqat! Bu amalni bekor qilib bo'lmaydi!</b>\n\n"
        "🗑️ Bazadagi <b>barcha o'quvchilar</b> ma'lumotlari o'chiriladi va "
        "ular yangidan <b>/start</b> bosib ro'yxatdan o'tishlari kerak bo'ladi.\n\n"
        "Davom etasizmi?",
        reply_markup=keyboard,
        parse_mode="HTML",
    )


# ── Tasdiqlash: Ha ────────────────────────────────────────────────────────────
@admin_router.callback_query(F.data == "admin_clear_yes")
async def callback_clear_yes(callback: CallbackQuery) -> None:
    await callback.answer()
    try:
        count = await clear_all_users()
        await callback.message.edit_text(
            f"✅ <b>Baza muvaffaqiyatli tozalandi!</b>\n\n"
            f"🗑️ Jami <b>{count}</b> nafar o'quvchi ma'lumotlari o'chirildi.\n\n"
            f"Endi o'quvchilar botga qaytib <b>/start</b> bosib yangidan "
            f"ro'yxatdan o'tishlari mumkin.",
            parse_mode="HTML",
        )
        log.info("Admin %s barcha ma'lumotlarni o'chirdi (%d ta).",
                 callback.from_user.id, count)
    except Exception as e:
        log.error("Bazani tozalashda xatolik: %s", e, exc_info=True)
        await callback.message.edit_text(
            f"❌ Xatolik yuz berdi:\n<code>{e}</code>",
            parse_mode="HTML",
        )


# ── Tasdiqlash: Yo'q ──────────────────────────────────────────────────────────
@admin_router.callback_query(F.data == "admin_clear_no")
async def callback_clear_no(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.edit_text("✅ Bekor qilindi. Ma'lumotlar o'chirilmadi.")


# ── /admin panelidan Tasdiqlash ───────────────────────────────────────────────
@admin_router.callback_query(F.data == "admin_clear_confirm")
async def callback_clear_confirm(callback: CallbackQuery) -> None:
    await callback.answer()
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Ha, barcha ma'lumotlarni o'chir",
                    callback_data="admin_clear_yes"
                ),
                InlineKeyboardButton(
                    text="❌ Bekor qil",
                    callback_data="admin_clear_no"
                ),
            ]
        ]
    )
    await callback.message.answer(
        "⚠️ <b>Diqqat! Bu amalni bekor qilib bo'lmaydi!</b>\n\n"
        "🗑️ Bazadagi <b>barcha o'quvchilar</b> ma'lumotlari o'chiriladi.\n\n"
        "Davom etasizmi?",
        reply_markup=keyboard,
        parse_mode="HTML",
    )
