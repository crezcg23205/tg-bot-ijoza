# =============================================
#  handlers/user.py — Foydalanuvchi handlerlari
# =============================================

import logging
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from states import Form
from database import save_user, get_user
from utils.validators import is_valid_full_name, is_valid_group, is_valid_book
from utils.helpers import normalize_text

log = logging.getLogger(__name__)
user_router = Router()

# ── Umumiy Ko'rsatmalar ────────────────────────────────────────────────────────
INSTRUCTIONS_MSG = (
    "Assalomu alaykum.\n\n"
    "Ijoza uchun quyidagi ma'lumotlarni kiriting.\n\n"
    "1. Ism va familiya\n"
    "   Namuna:\n"
    "   Zayd Falonchiyev\n\n"
    "2. Guruh tartibi\n"
    "   Foydalanuvchi o'qigan guruh nomi yoki raqamini kiritsin.\n"
    "   Namuna:\n"
    "   12-guruh\n\n"
    "3. O'qilgan kitob nomi\n"
    "   Namuna:\n"
    "   Maqosidus Savm\n\n"
    "4. Test topshirganligini tasdiqlash\n"
    "   Foydalanuvchi aynan:\n"
    "   \"Test topshirdim\"\n"
    "   deb yozishi kerak.\n\n"
    "Ma'lumotlarni ketma-ket yuboring."
)

# ── Xatolik xabari andoza ──────────────────────────────────────────────────────
VALIDATION_ERROR_MSG = (
    "❌ Kiritilgan ma'lumotda xatolik aniqlandi.\n\n"
    "Iltimos ma'lumotlarni qayta tekshirib, to'g'ri shaklda kiriting.\n\n"
    "Namuna:\n"
    "Ism Familiya\n"
    "12-guruh\n"
    "Maqosidus Savm\n"
    "Test topshirdim"
)


# ── /start ─────────────────────────────────────────────────────────────────────
@user_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    user_id = message.from_user.id
    
    # Avval bazada bor-yo'qligini tekshiramiz
    user_data = await get_user(user_id)
    if user_data:
        # User allaqachon ro'yxatdan o'tgan
        await message.answer(
            f"👋 <b>Siz allaqachon ro'yxatdan o'tgansiz!</b>\n\n"
            f"📋 <b>Sizning ma'lumotlaringiz:</b>\n"
            f"👤 Ism Sharif: <b>{user_data['full_name']}</b>\n"
            f"👨‍👩‍ Jinsi: <b>{user_data['gender']}</b>\n"
            f"🏫 Guruh: <b>{user_data['group_name']}</b>\n"
            f"📖 Kitob: <b>{user_data['book_name']}</b>\n"
            f"✔️ Test holati: <b>{user_data['test_status']}</b>\n"
            f"📅 Ro'yxatdan o'tilgan sana: <b>{user_data['created_at']}</b>\n\n"
            f"<i>Agar ma'lumotlarni yangilashni xohlasangiz, quyidagi tugmani bosing:</i>",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="🔄 Ma'lumotlarni yangilash",
                            callback_data="update_registration",
                        )
                    ]
                ]
            ),
            parse_mode="HTML",
        )
        return

    # Ro'yxatdan o'tmagan bo'lsa, start beramiz
    await message.answer(INSTRUCTIONS_MSG)
    await message.answer(
        "⬇️ Birinchi ma'lumotni yuboring. <b>Ism va familiyangizni</b> kiriting:\n"
        "<i>Namuna: Zayd Falonchiyev</i>",
        parse_mode="HTML",
    )
    await state.set_state(Form.full_name)


# ── Ro'yxatdan o'tishni yangilash Callback ─────────────────────────────────────
@user_router.callback_query(F.data == "update_registration")
async def process_update_reg_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.clear()
    
    # Start registration flow again
    await callback.message.answer(INSTRUCTIONS_MSG)
    await callback.message.answer(
        "⬇️ <b>Ism va familiyangizni</b> kiriting:\n"
        "<i>Namuna: Zayd Falonchiyev</i>",
        parse_mode="HTML",
    )
    await state.set_state(Form.full_name)

def is_four_lines_message(message: Message) -> bool:
    if not message.text:
        return False
    # Bo'sh bo'lmagan qatorlarni olamiz
    lines = [line.strip() for line in message.text.split("\n") if line.strip()]
    return len(lines) == 4


# ── 4 Qatorli xabarlarni birdaniga qabul qilish handler-i ──────────────────────
@user_router.message(is_four_lines_message)
async def process_four_lines_message(message: Message, state: FSMContext) -> None:
    text = message.text.strip()
    lines = [normalize_text(line) for line in text.split("\n") if line.strip()]
    
    # Har bir qatorni alohida validatsiya qilamiz
    if not is_valid_full_name(lines[0]):
        await message.answer(
            f"{VALIDATION_ERROR_MSG}\n\n"
            f"❌ <b>Ism va familiyada xatolik aniqlandi.</b>\n"
            f"📌 <i>Kamida 2 ta so'zdan iborat ism-familiya kiriting (raqamlar bo'lmasin).</i>",
            parse_mode="HTML"
        )
        return
        
    if not is_valid_group(lines[1]):
        await message.answer(
            f"{VALIDATION_ERROR_MSG}\n\n"
            f"❌ <b>Guruh tartibida xatolik aniqlandi.</b>\n"
            f"📌 <i>Kamida 2 ta belgidan iborat guruh nomini kiriting.</i>",
            parse_mode="HTML"
        )
        return
        
    if not is_valid_book(lines[2]):
        await message.answer(
            f"{VALIDATION_ERROR_MSG}\n\n"
            f"❌ <b>Kitob nomida xatolik aniqlandi.</b>\n"
            f"📌 <i>Kamida 2 ta harfdan iborat kitob nomini kiriting.</i>",
            parse_mode="HTML"
        )
        return
        
    if lines[3].lower() != "test topshirdim":
        await message.answer(
            f"{VALIDATION_ERROR_MSG}\n\n"
            f"❌ <b>Tasdiqlashda xatolik aniqlandi.</b>\n"
            f"📌 <i>To'rtinchi qatorda aynan <b>\"Test topshirdim\"</b> deb yozilishi kerak.</i>",
            parse_mode="HTML"
        )
        return

    # Barcha ma'lumotlar to'g'ri bo'lsa, holatga saqlaymiz
    await state.update_data(
        full_name=lines[0],
        group=lines[1],
        book=lines[2]
    )
    
    # Jinsini so'raymiz (chunki u matnda yo'q, lekin bazaga saqlash va hisobot uchun shart)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👨 Erkak", callback_data="gender_Erkak"),
                InlineKeyboardButton(text="👩 Ayol", callback_data="gender_Ayol"),
            ]
        ]
    )
    await message.answer(
        f"✅ <b>Barcha 4 ta ma'lumot qabul qilindi:</b>\n\n"
        f"👤 Ism Sharif: <b>{lines[0]}</b>\n"
        f"🏫 Guruh: <b>{lines[1]}</b>\n"
        f"📖 Kitob: <b>{lines[2]}</b>\n"
        f"✔️ Test: <b>Topshirildi</b>\n\n"
        f"Iltimos, oxirgi qadam sifatida jinsingizni tanlang:",
        reply_markup=keyboard,
        parse_mode="HTML",
    )
    await state.set_state(Form.gender)


# ── 1-bosqich: Ism Sharif ──────────────────────────────────────────────────────
@user_router.message(Form.full_name)
async def process_full_name(message: Message, state: FSMContext) -> None:
    text = normalize_text(message.text) if message.text else ""

    if not is_valid_full_name(text):
        await message.answer(
            f"{VALIDATION_ERROR_MSG}\n\n"
            f"⬇️ Iltimos, <b>ism va familiyangizni</b> qaytadan to'g'ri kiriting:\n"
            f"<i>Namuna: Zayd Falonchiyev</i>",
            parse_mode="HTML",
        )
        return

    await state.update_data(full_name=text)
    
    # Jinsini tanlash uchun InlineKeyboard yuboramiz
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👨 Erkak", callback_data="gender_Erkak"),
                InlineKeyboardButton(text="👩 Ayol", callback_data="gender_Ayol"),
            ]
        ]
    )
    await message.answer(
        f"✅ Ism qabul qilindi: <b>{text}</b>\n\n"
        "Jinsingizni tanlang:",
        reply_markup=keyboard,
        parse_mode="HTML",
    )
    await state.set_state(Form.gender)


# ── 2-bosqich: Jins Callback ───────────────────────────────────────────────────
@user_router.callback_query(Form.gender, F.data.startswith("gender_"))
async def process_gender_callback(callback: CallbackQuery, state: FSMContext) -> None:
    gender = callback.data.split("_")[1]  # 'Erkak' yoki 'Ayol'
    await state.update_data(gender=gender)
    await callback.answer()

    # Tanlangan jinsni tahrirlaymiz
    await callback.message.edit_text(
        f"✅ Jins tanlandi: <b>{gender}</b>",
        parse_mode="HTML",
    )

    # Keyingi bosqichni so'raymiz
    await callback.message.answer(
        "⬇️ Endi <b>guruh tartibini</b> (nomi yoki raqami) kiriting:\n"
        "<i>Namuna: 12-guruh</i>",
        parse_mode="HTML",
    )
    await state.set_state(Form.group)


# ── Jins bosqichida xabar yuborilsa (tutish) ────────────────────────────────────
@user_router.message(Form.gender)
async def process_gender_msg_fallback(message: Message) -> None:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👨 Erkak", callback_data="gender_Erkak"),
                InlineKeyboardButton(text="👩 Ayol", callback_data="gender_Ayol"),
            ]
        ]
    )
    await message.answer(
        "⚠️ Iltimos, jinsingizni quyidagi tugmalardan birini tanlash orqali belgilang:",
        reply_markup=keyboard,
    )


# ── 3-bosqich: Guruh ───────────────────────────────────────────────────────────
@user_router.message(Form.group)
async def process_group(message: Message, state: FSMContext) -> None:
    text = normalize_text(message.text) if message.text else ""

    if not is_valid_group(text):
        await message.answer(
            f"{VALIDATION_ERROR_MSG}\n\n"
            f"⬇️ Iltimos, <b>guruh tartibini</b> qaytadan kiriting:\n"
            f"<i>Namuna: 12-guruh</i>",
            parse_mode="HTML",
        )
        return

    await state.update_data(group=text)
    await message.answer(
        f"✅ Guruh qabul qilindi: <b>{text}</b>\n\n"
        "⬇️ Endi <b>o'qilgan kitob nomini</b> kiriting:\n"
        "<i>Namuna: Maqosidus Savm</i>",
        parse_mode="HTML",
    )
    await state.set_state(Form.book)


# ── 4-bosqich: Kitob nomi ──────────────────────────────────────────────────────
@user_router.message(Form.book)
async def process_book(message: Message, state: FSMContext) -> None:
    text = normalize_text(message.text) if message.text else ""

    if not is_valid_book(text):
        await message.answer(
            f"{VALIDATION_ERROR_MSG}\n\n"
            f"⬇️ Iltimos, <b>o'qilgan kitob nomini</b> qaytadan kiriting:\n"
            f"<i>Namuna: Maqosidus Savm</i>",
            parse_mode="HTML",
        )
        return

    await state.update_data(book=text)
    await message.answer(
        f"✅ Kitob nomi qabul qilindi: <b>{text}</b>\n\n"
        "⬇️ Oxirgi qadam! Test topshirganligingizni tasdiqlash uchun aynan quyidagi jumlani yozing:\n\n"
        "<b>Test topshirdim</b>",
        parse_mode="HTML",
    )
    await state.set_state(Form.test)


# ── 5-bosqich: Test tasdiqi ────────────────────────────────────────────────────
@user_router.message(Form.test)
async def process_test(message: Message, state: FSMContext) -> None:
    text = message.text.strip() if message.text else ""

    if text.lower() != "test topshirdim":
        await message.answer(
            f"{VALIDATION_ERROR_MSG}\n\n"
            f"⬇️ Iltimos, aynan <b>\"Test topshirdim\"</b> deb yozib tasdiqlang:",
            parse_mode="HTML",
        )
        return

    data = await state.get_data()
    try:
        await save_user(
            telegram_id=message.from_user.id,
            full_name=data["full_name"],
            gender=data["gender"],
            group_name=data["group"],
            book_name=data["book"],
            test_status="Test topshirdim",
        )
        log.info(
            "Muvaffaqiyatli saqlandi/yangilandi: %s (ID: %s)",
            data["full_name"],
            message.from_user.id,
        )
    except Exception as exc:
        log.error("Ma'lumotlarni saqlashda xatolik: %s", exc)
        await message.answer(
            "⚠️ Tizimda xatolik yuz berdi. Iltimos qaytadan urinib ko'ring: /start",
        )
        await state.clear()
        return

    await state.clear()
    await message.answer(
        "✅ <b>Ma'lumotlaringiz muvaffaqiyatli qabul qilindi!</b>\n\n"
        "🎓 Ijoza tayyorlash uchun navbatga qo'shildingiz.\n\n"
        "📋 <b>Qabul qilingan ma'lumotlar:</b>\n"
        f"👤 Ism Sharif: <b>{data['full_name']}</b>\n"
        f"👨‍👩‍ Jinsi: <b>{data['gender']}</b>\n"
        f"🏫 Guruh: <b>{data['group']}</b>\n"
        f"📖 Kitob: <b>{data['book']}</b>\n"
        f"✔️ Test: <b>Topshirildi</b>",
        parse_mode="HTML",
    )
