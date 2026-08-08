# =============================================
#  states/form.py — FSM holatlari
# =============================================

from aiogram.fsm.state import State, StatesGroup


class Form(StatesGroup):
    full_name = State()   # 1. Ism Sharif
    gender    = State()   # 2. Jinsi
    group     = State()   # 3. Guruh tartibi
    book      = State()   # 4. O'qilgan kitob
    test      = State()   # 5. Test tasdiqi


class AdminForm(StatesGroup):
    waiting_for_template = State()   # Sertifikat shablonini kutish
