# =============================================
#  utils/helpers.py — Matn yordamchi funksiyalari
# =============================================

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    _BIDI_AVAILABLE = True
except ImportError:
    _BIDI_AVAILABLE = False


def normalize_arabic(text: str) -> str:
    """
    Arab yozuvidagi matnni to'g'ri tartibda saqlash uchun normalize qiladi.
    
    Muammo: Telegram arab harflarini RTL (o'ngdan chapga) yuboradi, lekin
    Python stringda ular teskari tartibda saqlanadi.
    
    Yechim: arabic_reshaper + python-bidi orqali matnni to'g'ri holga keltirish.
    Agar kutubxona o'rnatilmagan bo'lsa — asl matnni qaytaradi.
    """
    if not text:
        return text

    # Arab harflari borligini tekshirish (Unicode U+0600 - U+06FF oralig'i)
    has_arabic = any('\u0600' <= ch <= '\u06FF' for ch in text)
    if not has_arabic:
        return text

    if not _BIDI_AVAILABLE:
        return text

    try:
        # 1. Harflarni to'g'ri shakllantirish (reshaping)
        reshaped = arabic_reshaper.reshape(text)
        # 2. BiDi algoritmini qo'llash (to'g'ri tartib)
        corrected = get_display(reshaped)
        return corrected
    except Exception:
        # Xato bo'lsa asl matnni qaytaramiz
        return text


def normalize_text(text: str) -> str:
    """
    Har qanday matnni normalize qiladi:
    - Bosh va oxirdagi bo'shliqlarni olib tashlaydi
    """
    return text.strip()
