# =============================================
#  main.py — Botni ishga tushirish
# =============================================

import asyncio
import logging

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


# ── Global Xatolik Handler (Error Handler) ──────────────────────────────────────
async def errors_handler(event: ErrorEvent) -> None:
    """Bot faoliyatida yuz beradigan kutilmagan xatoliklarni ushlaydi va loglaydi."""
    log.error("Kutilmagan xatolik yuz berdi: %s", event.exception, exc_info=True)
    
    # Foydalanuvchiga xabar berishga harakat qilamiz
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
