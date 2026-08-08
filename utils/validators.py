# =============================================
#  utils/validators.py — Validatsiya funksiyalari
# =============================================

import re


def is_valid_full_name(text: str) -> bool:
    """
    Ism Sharif validatsiyasi:
    - Kamida 2 ta so'z bo'lishi kerak.
    - Faqat ism-familiya.
    - Raqam bo'lmasin.
    - Lotin yozuvi, Kirill yozuvi, Arab yozuvi va boshqa harflarni qabul qiladi.
    """
    text = text.strip()
    if not text:
        return False

    # Raqam bo'lmasligi kerak
    for char in text:
        if char.isdigit():
            return False

    # So'zlarni ajratamiz
    words = text.split()
    if len(words) < 2:
        return False

    # Har bir so'zda faqat harflar, apostroflar va tire bo'lishi kerak
    for word in words:
        # Apostrof (', ʼ, ʻ, `) va tirelarni olib tashlaymiz
        clean_word = re.sub(r"['ʼʻ`\-]", "", word)
        if not clean_word:
            return False
        
        # Qolgan barcha belgilar Unicode harf bo'lishi shart (Lotin, Kirill, Arab va hk)
        for char in clean_word:
            if not char.isalpha():
                return False

    return True


def is_valid_group(text: str) -> bool:
    """
    Guruh nomi validatsiyasi:
    - Bo'sh bo'lmasin
    - Kamida 2 ta belgi bo'lsin
    """
    text = text.strip()
    return len(text) >= 2


def is_valid_book(text: str) -> bool:
    """
    Kitob nomi validatsiyasi:
    - Bo'sh bo'lmasin
    - Kamida 2 ta harf bo'lsin
    """
    text = text.strip()
    if not text:
        return False
    # Kamida 2 ta harf bo'lishi kerak
    letter_count = sum(1 for char in text if char.isalpha())
    return letter_count >= 2
