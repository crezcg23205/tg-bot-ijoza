# =============================================
#  config.py — Bot sozlamalari
# =============================================

import os
from dotenv import load_dotenv

# .env faylini yuklash
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "8983534361:AAHSyvU0syOPv-AUvZz1ZveWcI7XJAt-fHc")

# Admin Telegram ID lari — alohida o'zgaruvchilar sifatida
ADMIN_ID_1 = int(os.getenv("ADMIN_ID_1", "5725671264"))
ADMIN_ID_2 = int(os.getenv("ADMIN_ID_2", "642479837"))
ADMIN_IDS = [ADMIN_ID_1, ADMIN_ID_2]

# Ma'lumotlar bazasi fayli
DB_PATH = os.getenv("DB_PATH", "certificate_bot.db")

# PDF fayl nomi
PDF_FILENAME = os.getenv("PDF_FILENAME", "sertifikat_malumotlar.pdf")
