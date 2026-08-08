# =============================================
#  main.py — Botni ishga tushirish
#  Render uchun: aiohttp health-check server
# =============================================

import asyncio
import logging
import os

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ErrorEvent

from config import BOT_TOKEN
from database import init_db
from handlers import user_router, admin_router

# ── Loglash sozlamasi ──────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)


# ── Render health-check uchun oddiy HTTP server ────────────────────────────────
async def health_check(request: web.Request) -> web.Response:
    return web.Response(text="OK", status=200)


async def run_web_server() -> None:
    """Render health-check uchun minimal HTTP server (PORT dan port oladi)."""
    port = int(os.environ.get("PORT", 10000))
    app = web.Application()
    app.router.add_get("/", health_check)
    app.router.add_get("/health", health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    log.info("Health-check server port %d da ishga tushdi.", port)


# ── Global Xatolik Handler ─────────────────────────────────────────────────────
async def errors_handler(event: ErrorEvent) -> None:
    """Bot faoliyatida yuz beradigan kutilmagan xatoliklarni ushlaydi."""
    log.error("Kutilmagan xatolik yuz berdi: %s", event.exception, exc_info=True)
    try:
        if event.update.message:
            await event.update.message.answer(
                "⚠️ Tizimda kutilmagan xatolik yuz berdi. Iltimos keyinroq qayta urinib ko'ring."
            )
        elif event.update.callback_query and event.update.callback_query.message:
            await event.update.callback_query.message.answer(
                "⚠️ Tizimda kutilmagan xatolik yuz berdi. Iltimos keyinroq qayta urinib ko'ring."
            )
    except Exception as e:
        log.error("Xatolik haqida xabar yuborishda muammo: %s", e)


async def main() -> None:
    # Ma'lumotlar bazasini ishga tushirish
    await init_db()
    log.info("Ma'lumotlar bazasi tayyor.")

    # Render health-check server ni ishga tushirish (bot bilan parallel)
    await run_web_server()

    # Bot va Dispatcher
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Routerlarni ro'yxatga olish
    dp.include_router(admin_router)   # Admin routeri avval (prioritet)
    dp.include_router(user_router)

    # Global xatolik handlerini ulash
    dp.errors.register(errors_handler)

    log.info("Bot ishga tushmoqda...")

    try:
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types(),
        )
    finally:
        await bot.session.close()
        log.info("Bot to'xtatildi.")


if __name__ == "__main__":
    asyncio.run(main())
