# 📜 Certificate Bot — O'rnatish va Ishga Tushirish Qo'llanmasi

Ushbu bot sertifikat uchun o'quvchilardan ma'lumot yig'ish (FSM orqali), ularni SQLite bazasida saqlash/yangilash va adminlar uchun chiroyli segmentlangan PDF hisobot va statistika tayyorlash vazifasini bajaradi.

## 📁 Loyiha tuzilmasi

```
certificate_bot/
├── main.py                  ← Botni ishga tushirish (polling)
├── config.py                ← Token va admin sozlamalari (load_dotenv)
├── .env                     ← Maxfiy ma'lumotlar (.env fayli)
├── requirements.txt         ← Kerakli kutubxonalar (aiogram, reportlab, aiosqlite, dotenv)
│
├── handlers/
│   ├── __init__.py
│   ├── user.py              ← Foydalanuvchi oqimi (FSM & jins tanlash)
│   └── admin.py             ← Admin buyruqlari (/admin, /malumot, /statistika)
│
├── database/
│   ├── __init__.py
│   └── db.py                ← SQLite (aiosqlite) operatsiyalari va migratsiya
│
├── states/
│   ├── __init__.py
│   └── form.py              ← FSM holatlari (full_name, gender, group, book, test)
│
└── utils/
    ├── __init__.py
    ├── validators.py         ← Ma'lumot validatsiyasi (Lotin, Kirill, Arab unicode)
    └── pdf_generator.py      ← A4 PDF yaratish (Erkak/Ayol o'quvchilar jadvali)
```

---

## ⚙️ O'rnatish bosqichlari

### 1. Python tekshirish
```bash
python --version   # Python 3.10+ bo'lishi tavsiya etiladi
```

### 2. Virtual muhit yaratish
```bash
python -m venv venv

# Windows-da faollashtirish:
venv\Scripts\activate

# Linux / macOS-da faollashtirish:
source venv/bin/activate
```

### 3. Kutubxonalarni o'rnatish
```bash
pip install -r requirements.txt
```

### 4. Sozlamalar — `.env`
Loyiha ildiz papkasida `.env` faylini yarating va quyidagi qiymatlarni kiriting:
```env
BOT_TOKEN=8983534361:AAHSyvU0syOPv-AUvZz1ZveWcI7XJAt-fHc
ADMIN_IDS=5725671264
DB_PATH=certificate_bot.db
PDF_FILENAME=sertifikat_malumotlar.pdf
```

> 💡 **ADMIN_IDS** vergul bilan ajratilgan bir nechta admin ID bo'lishi mumkin (masalan: `5725671264,987654321`).

### 5. Botni ishga tushirish
```bash
python main.py
```

---

## 🤖 Bot buyruqlari

### Foydalanuvchilar uchun:
| Buyruq | Vazifasi |
|--------|----------|
| `/start` | Sertifikat uchun ro'yxatdan o'tish yoki ma'lumotlarni yangilash |

### Adminlar uchun:
Admin buyruqlari faqat `.env` dagi `ADMIN_IDS` ro'yxatida mavjud bo'lgan ID egalariga ishlaydi (`AdminMiddleware` orqali himoyalangan):
| Buyruq | Vazifasi |
|--------|----------|
| `/admin` | Admin panelini ochish (`📄 PDF Hisobot` va `📊 Statistika` tugmalari bilan) |
| `/malumot` | Barcha ma'lumotlarni chiroyli A4 formatidagi PDF ko'rinishida yuborish |
| `/statistika` | Jami, erkaklar, ayollar, kitoblar va guruhlar bo'yicha batafsil statistika |

---

## 📋 Foydalanuvchi Ro'yxatdan o'tish Oqimi (FSM)

1. **Ism Sharif**: Kamida 2 ta so'zdan iborat bo'lishi kerak. Raqamlar yoki maxsus belgilar bo'lmasligi kerak. Lotin, Kirill va Arab harflarini to'liq qo'llab-quvvatlaydi.
2. **Jinsi**: Inline Keyboard orqali `👨 Erkak` yoki `👩 Ayol` tanlanadi.
3. **Guruh**: Kamida 2 ta belgidan iborat bo'lishi shart.
4. **Kitob**: Kamida 2 ta harfdan iborat bo'lishi kerak.
5. **Test**: Aynan `Test topshirdim` (katta-kichik harflar farqsiz) deb yozilishi lozim.

> ⚠️ Agar biror bosqichda ma'lumot noto'g'ri kiritilsa, bot xatolik xabarini va namunani yuboradi hamda foydalanuvchini o'sha bosqichda ushlab turadi.

---

## 📄 PDF Hisobot Tuzilishi

PDF hisoboti **A4 Portrait** (vertikal) formatda va o'ta professional ko'rinishda bo'lib, quyidagilarni o'z ichiga oladi:
* **Sarlavha**: `SERTIFIKAT UCHUN RO'YXAT`
* **Erkak o'quvchilar jadvali**: `№ | Ism Familiya | Guruh | Kitob`
* **Ayol o'quvchilar jadvali**: `№ | Ism Familiya | Guruh | Kitob`
* **Sahifa raqamlari**: Pastki o'ng burchakda avtomatik sahifa raqami.
* **Sana**: Hujjat yaratilgan sana va vaqt.
* **Unicode qo'llab-quvvatlashi**: Arial yoki DejaVu fontlaridan foydalangan holda Kirill va Arab harflarini to'liq render qiladi.
