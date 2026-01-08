from __future__ import annotations

from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.i18n import get_text
from bot.state_store import user_languages
from data.config import ADMIN_IDS
from data.constants import CHANNELS
from data.users import PLAN_PRO, PLAN_PRO_PLUS, PLAN_UNLIMITED


def subscription_keyboard(user_id: int | None = None):
    lang = user_languages.get(user_id, "uz") if user_id else "uz"
    subscribed_text = {"uz": "✅ Obuna bo'ldim", "en": "✅ I subscribed", "ru": "✅ Я подписался"}
    kb = InlineKeyboardBuilder()
    for channel in CHANNELS:
        channel_name = channel.lstrip("@")
        channel_display = channel_name.replace("_", " ").title()
        kb.button(text=f"📢 {channel_display}", url=f"https://t.me/{channel_name}")
    kb.button(text=subscribed_text.get(lang, subscribed_text["uz"]), callback_data="check_subscription")
    kb.adjust(1)
    return kb.as_markup()


def language_select_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="🇺🇿 O'zbek", callback_data="lang_uz")
    kb.button(text="🇬🇧 English", callback_data="lang_en")
    kb.button(text="🇷🇺 Русский", callback_data="lang_ru")
    kb.adjust(3)
    return kb.as_markup()


def main_menu_keyboard(user_id: int):
    kb = InlineKeyboardBuilder()

    kb.button(text=get_text(user_id, "profile"), callback_data="menu_profile")
    kb.button(text=get_text(user_id, "history"), callback_data="menu_history")

    kb.button(text=get_text(user_id, "menu_image_gen"), callback_data="menu_image")
    kb.button(text=get_text(user_id, "video_generation"), callback_data="menu_video")

    kb.button(text=get_text(user_id, "help_button"), callback_data="menu_help")
    kb.button(text=get_text(user_id, "language"), callback_data="menu_language")

    kb.adjust(2, 2, 2)

    kb2 = InlineKeyboardBuilder()
    kb2.button(text=get_text(user_id, "buy_premium"), callback_data="menu_premium")
    kb2.button(text=get_text(user_id, "link_contact"), url="https://t.me/shoxa_devv")
    kb2.adjust(1)

    if user_id in ADMIN_IDS:
        kb2.button(text=get_text(user_id, "admin_panel"), callback_data="admin_panel")

    kb.attach(kb2)
    return kb.as_markup()


def image_size_keyboard(user_id: int):
    kb = InlineKeyboardBuilder()
    kb.button(text=get_text(user_id, "size_1_1"), callback_data="size_1024x1024")
    kb.button(text=get_text(user_id, "size_3_4"), callback_data="size_1024x1792")
    kb.button(text=get_text(user_id, "size_16_9"), callback_data="size_1792x1024")
    kb.button(text=get_text(user_id, "back"), callback_data="back_to_main")
    kb.adjust(2)
    return kb.as_markup()


def admin_menu_keyboard(user_id: int):
    kb = InlineKeyboardBuilder()
    kb.button(text="🎁 Premium Hadya", callback_data="admin_gift_start")
    kb.button(text="🗑 Premium O'chirish", callback_data="admin_remove_premium_start")
    kb.button(text="⛔ Bloklash", callback_data="admin_block_start")
    kb.button(text="✅ Blokdan chiqarish", callback_data="admin_unblock_start")
    kb.button(text="📊 Bot Statistikasi", callback_data="admin_stats")
    kb.button(text="💰 API Usage", callback_data="admin_api")
    kb.button(text="❌ Yopish", callback_data="admin_cancel")
    kb.adjust(1)
    return kb.as_markup()


def admin_gift_keyboard(target_uid: int):
    kb = InlineKeyboardBuilder()
    kb.button(text="Pro", callback_data=f"gift_plan_{PLAN_PRO}_{target_uid}")
    kb.button(text="Pro+", callback_data=f"gift_plan_{PLAN_PRO_PLUS}_{target_uid}")
    kb.button(text="Limit Tanlash", callback_data=f"gift_plan_custom_{target_uid}")
    kb.button(text="Bekor qilish", callback_data="admin_cancel")
    kb.adjust(1)
    return kb.as_markup()


def admin_duration_keyboard(target_uid: int, plan: str):
    kb = InlineKeyboardBuilder()
    kb.button(text="1 Oy", callback_data=f"gift_dur_30_{plan}_{target_uid}")
    kb.button(text="3 Oy", callback_data=f"gift_dur_90_{plan}_{target_uid}")
    kb.button(text="1 Yil", callback_data=f"gift_dur_365_{plan}_{target_uid}")
    kb.button(text="Bekor qilish", callback_data="admin_cancel")
    kb.adjust(1)
    return kb.as_markup()


def profile_keyboard(user_id: int):
    kb = InlineKeyboardBuilder()
    kb.button(text=get_text(user_id, "buy_premium"), callback_data="menu_premium")
    kb.button(text=get_text(user_id, "back"), callback_data="back_to_main")
    kb.adjust(1)
    return kb.as_markup()


def premium_keyboard(user_id: int):
    kb = InlineKeyboardBuilder()
    kb.button(text=get_text(user_id, "plan_pro"), callback_data=f"buy_{PLAN_PRO}")
    kb.button(text=get_text(user_id, "plan_pro_plus"), callback_data=f"buy_{PLAN_PRO_PLUS}")
    kb.button(text=get_text(user_id, "plan_unlimited"), callback_data=f"buy_{PLAN_UNLIMITED}")
    kb.button(text=get_text(user_id, "back"), callback_data="back_to_main")
    kb.adjust(1)
    return kb.as_markup()


def back_button(user_id: int):
    kb = InlineKeyboardBuilder()
    kb.button(text=get_text(user_id, "back"), callback_data="back_to_main")
    return kb.as_markup()


def video_quality_keyboard(user_id: int):
    kb = InlineKeyboardBuilder()
    kb.button(text=get_text(user_id, "quality_480p"), callback_data="video_quality_480p")
    kb.button(text=get_text(user_id, "quality_720p"), callback_data="video_quality_720p")
    kb.button(text=get_text(user_id, "quality_1080p"), callback_data="video_quality_1080p")
    kb.button(text=get_text(user_id, "quality_4k"), callback_data="video_quality_4k")
    kb.button(text=get_text(user_id, "back"), callback_data="back_to_main")
    kb.adjust(1)
    return kb.as_markup()

