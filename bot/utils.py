from __future__ import annotations

import os
import re
from typing import Tuple

import requests

from bot.i18n import get_text
from data.constants import BOT_NICKNAME, CHANNELS


def detect_language(text: str) -> str:
    """Detect language: uz/en/ru (very lightweight heuristic)."""
    if not text:
        return "uz"
    text_lower = text.lower()
    cyrillic_chars = sum(
        1 for char in text if ("а" <= char.lower() <= "я") or char.lower() == "ё"
    )
    if cyrillic_chars > len(text) * 0.3:
        return "ru"
    english_words = [
        "the",
        "is",
        "are",
        "and",
        "or",
        "but",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "with",
        "by",
        "from",
        "this",
        "that",
        "what",
        "where",
        "when",
        "why",
        "how",
        "can",
        "will",
        "would",
        "should",
        "could",
        "may",
        "might",
    ]
    english_count = sum(1 for word in english_words if word in text_lower)
    if english_count > 2:
        return "en"
    return "uz"


def is_bot_info_question(text: str, lang: str) -> str | None:
    """
    Check if question is about bot creator/author/name.
    Returns: "creator" if about creator, "name" if about name, None otherwise.
    """
    if not text:
        return None
    text_lower = text.lower()
    
    # Keywords for creator/author questions
    creator_keywords = {
        "uz": ["kim yaratdi", "kim qildi", "kim yaratgan", "kim qilgan", "yaratgan", "yaratdi", "qilgan", "qildi", 
               "kim tomonidan", "kim tomonidan yaratilgan", "yaratuvchi", "muallif", "avtor", "creator", "author"],
        "en": ["who created", "who made", "who built", "creator", "author", "made by", "created by", "built by"],
        "ru": ["кто создал", "кто сделал", "кто создал", "создатель", "автор", "создан", "сделал"],
    }
    
    # Keywords for name questions
    name_keywords = {
        "uz": ["isming", "ismingiz", "ismi", "ism", "name", "nomi", "nom"],
        "en": ["your name", "what is your name", "name", "what's your name", "whats your name"],
        "ru": ["твое имя", "твоё имя", "как тебя зовут", "имя", "как зовут"],
    }
    
    keywords_creator = creator_keywords.get(lang, creator_keywords["uz"])
    keywords_name = name_keywords.get(lang, name_keywords["uz"])
    
    # Check for creator questions
    if any(keyword in text_lower for keyword in keywords_creator):
        return "creator"
    
    # Check for name questions
    if any(keyword in text_lower for keyword in keywords_name):
        return "name"
    
    return None


def is_image_request(text: str, lang: str) -> bool:
    if not text:
        return False
    text_lower = text.lower()
    image_keywords = {
        "uz": [
            "rasm",
            "tasvir",
            "surat",
            "rasm yarat",
            "tasvir yarat",
            "surat yarat",
            "rasm chiz",
            "tasvir chiz",
        ],
        "en": [
            "image",
            "picture",
            "draw",
            "create image",
            "generate image",
            "make image",
            "draw picture",
            "create picture",
        ],
        "ru": [
            "изображение",
            "картинка",
            "рисунок",
            "создать изображение",
            "нарисовать",
            "создать картинку",
            "нарисовать картинку",
        ],
    }
    keywords = image_keywords.get(lang, image_keywords["uz"])
    return any(keyword in text_lower for keyword in keywords)


def normalize_channel(channel: str) -> str:
    return channel if channel.startswith("@") else f"@{channel}"


def get_ad_text(user_id: int | None) -> str:
    """
    Legacy helper used for forwarded messages.
    In old code it was called but never defined; now it's fixed.
    """
    if not user_id:
        return f"{BOT_NICKNAME}"
    return f"{get_text(user_id, 'ad_text')} {BOT_NICKNAME}"


async def check_subscription(bot, user_id: int) -> bool:
    """Check if user is subscribed to all CHANNELS."""
    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(normalize_channel(channel), user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except Exception:
            return False
    return True


def get_currency_rates(base_currency: str) -> dict:
    try:
        url = f"https://api.exchangerate-api.com/v4/latest/{base_currency.upper()}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("rates", {})
        return {}
    except Exception:
        return {}


def format_currency_rates(rates: dict, base_currency: str, user_id: int) -> str:
    if not rates:
        return get_text(user_id, "currency_error")
    major_currencies = [
        "USD",
        "EUR",
        "GBP",
        "JPY",
        "CNY",
        "RUB",
        "UZS",
        "KZT",
        "TRY",
        "AED",
        "SAR",
        "INR",
    ]
    result = f"💱 1 {base_currency.upper()} = \n\n"
    for currency in major_currencies:
        if currency != base_currency.upper() and currency in rates:
            rate = rates[currency]
            result += f"• {currency}: {rate:.4f}\n"
    other_currencies = [
        c for c in sorted(rates.keys()) if c not in major_currencies and c != base_currency.upper()
    ]
    if other_currencies:
        result += f"\n... and {len(other_currencies)} other currencies"
    return result


def parse_conversion_request(text: str) -> Tuple[float | None, str | None, str | None]:
    text_original = text.strip()
    text = text_original.upper()
    number_match = re.search(r"[\d,.\s]+", text)
    if not number_match:
        return (None, None, None)
    amount_str = number_match.group(0).replace(",", "").replace(" ", "")
    try:
        amount = float(amount_str)
    except ValueError:
        return (None, None, None)
    to_match = re.search(r"\b(?:TO|IN|В|К|КО)\b", text)
    if not to_match:
        return (None, None, None)
    to_pos = to_match.start()
    before_to = text[:to_pos].strip()
    after_to = text[to_match.end() :].strip()
    from_match = re.search(r"\b([A-Z]{3})\b", before_to)
    if not from_match:
        return (None, None, None)
    from_currency = from_match.group(1)
    to_match_curr = re.search(r"\b([A-Z]{3})\b", after_to)
    if not to_match_curr:
        return (None, None, None)
    to_currency = to_match_curr.group(1)
    return (amount, from_currency, to_currency)


def convert_currency(amount: float, from_currency: str, to_currency: str, user_id: int) -> str:
    try:
        rates = get_currency_rates(from_currency)
        if not rates:
            return get_text(user_id, "currency_error")
        if from_currency.upper() == to_currency.upper():
            return f"{amount:,.2f} {from_currency.upper()} = {amount:,.2f} {to_currency.upper()}"
        if to_currency.upper() in rates:
            converted_amount = amount * rates[to_currency.upper()]
            result = get_text(user_id, "currency_conversion")
            result += f"\n\n{amount:,.2f} {from_currency.upper()} = {converted_amount:,.2f} {to_currency.upper()}"
            reverse_rates = get_currency_rates(to_currency)
            if reverse_rates and from_currency.upper() in reverse_rates:
                result += (
                    f"\n\n(1 {to_currency.upper()} = {reverse_rates[from_currency.upper()]:,.4f} {from_currency.upper()})"
                )
            return result
        return get_text(user_id, "currency_error")
    except Exception:
        return get_text(user_id, "currency_conversion_error")


def is_video_available() -> bool:
    return bool(os.getenv("REPLICATE_API_TOKEN"))

