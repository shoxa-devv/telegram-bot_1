import asyncio
import json
import os
import re
import requests
from datetime import datetime
from aiogram import Bot, Dispatcher, F, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from data import BOT_TOKEN, ADMIN_IDS
import stats
# Add explicit admin ID requested
if 1897652450 not in ADMIN_IDS:
    ADMIN_IDS.append(1897652450)
from chatgpt import (
    chatgpt_text,
    speech_to_text,
    text_to_image,
    image_to_anime,
    transform_image_with_instruction,
    format_history,
    load_history,
)
from users import user_manager, PLAN_FREE, PLAN_PRO, PLAN_PRO_PLUS, PLAN_UNLIMITED, PRICES, LIMITS

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# VIP Foydalanuvchilar (limitsiz)
VIP_USERS = [1897652450]

# Majburiy obuna kanallari
CHANNELS = ["python_programmerr", "shoxa_drop", "shoxa_cs2"]

# Bot nickname (reklama uchun)
BOT_NICKNAME = "@ozbekchatgptbot"

# Foydalanuvchi tillarini saqlash
user_languages = {}  # user_id -> "uz", "en", "ru"

HISTORY_PATH = "history.json"
MAX_HISTORY = 50

# Ko'p tilli xabarlar
TRANSLATIONS = {
    "uz": {
        "welcome": "👋 Assalomu alaykum! Men GPT asosidagi botman.",
        "subscribe_msg": "📢 Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:",
        "subscribe_after": "Obuna bo'lgach, '✅ Obuna bo'ldim' tugmasini bosing.",
        "subscribe_success": "✅ Rahmat! Obuna bo'ldingiz.",
        "subscribe_fail": "❌ Hali kanalga obuna bo'lmadingiz!",
        "select_language": "🌐 Iltimos, tilni tanlang:",
        "language_selected": "✅ Til tanlandi!",
        "bot_features": "✨ Bot imkoniyatlari:\n\n📝 Matn va ovozga javob beraman\n🎤 Ovozli xabarlarni yozuvga aylantiraman va javob beraman\n🎨 Tasvir yaratish - oddiy matn yozib rasm yaratishingiz mumkin (masalan: 'rasm yarat qush' yoki 'tasvir yarat olma')\n🌐 Ko'p tilli qo'llab-quvvatlash - O'zbek, Ingliz va Rus tillarida ishlaydi\n📜 Chat tarixi - so'rovlaringiz va javoblaringiz saqlanadi",
        "roles": "Rollar 👤",
        "history": "Tarix 🫥",
        "back": "Orqaga",
        "main_menu": "Asosiy menyu.",
        "main_menu_button": "🏠 Asosiy Menyu",
        "thinking": "Javob o'ylaniyapti 😊",
        "image_help": "Tasvir yaratish uchun: /image Sizning tavsifi",
        "access_denied": "Kirish mumkin emas.",
        "language": "Til 🌐",
        "currency": "Valyuta 💱",
        "profile": "Profil 👤",
        "link_contact": "Bog'lanish 📞",
        "referral_new": "🎉 Tabriklaymiz! Siz yangi foydalanuvchini taklif qildingiz va sizga +3 ta doimiy limit qo'shildi! 🚀",
        "profile_info": "👤 **Sizning Profilingiz**\n\n🆔 ID: {user_id}\n📊 Tarif: {plan}\n👥 Taklif qilganlar: {referrals}\n⚖️ Kunlik limit: {limit}\n🖼 Rasm limiti: {image_limit}\n⏳ Qolgan so'rovlar: {remaining}\n\n🔗 Sizning referal havolangiz:\n<code>{link}</code>\n\n(Har bir taklif uchun +3 limit oling!)",
        "limit_reached": "⚠️ Kunlik limit tugadi!\n\nSiz 24 soat ichida faqat 10 ta bepul so'rov yubora olasiz. Davom ettirish uchun Premium sotib oling.",
        "buy_premium": "💎 Premium sotib olish",
        "premium_plans": "💎 Premium tariflar:\n\nBarcha limitlar Telegram Stars orqali to'lanadi.",
        "plan_pro": "Pro (100 ta so'rov, 100 ⭐️)",
        "plan_pro_plus": "Pro+ (250 ta so'rov, 250 ⭐️)",
        "plan_unlimited": "Unlimited (Cheksiz, 1000 ⭐️)",
        "premium_success": "✅ Tabriklaymiz! Siz Premium obunaga ega bo'ldingiz! 🎉",
        "currency_enter": "Valyuta kodini kiriting (masalan: USD, EUR, RUB, UZS) yoki konvertatsiya qiling (masalan: 1000000 uzs to usd):",
        "currency_result": "Valyuta kurslari",
        "currency_error": "Xatolik: Valyuta kodi topilmadi yoki noto'g'ri.",
        "currency_conversion": "💱 Konvertatsiya natijasi:",
        "currency_conversion_error": "Xatolik: Konvertatsiya formati noto'g'ri. Format: 1000000 uzs to usd",
        "currency_invalid_format": "Noto'g'ri format. Masalan: 1000000 uzs to usd yoki USD",
        "ad_text": "🤖 Aqlli bot bilan suhbat qiling",
        "group_ad_text": "🤖 Aqlli bot bilan suhbat qiling",
        "admin_panel": "Admin Panel 🎁",
        "admin_gift_title": "🎁 Admin Panel\n\nFoydalanuvchi nomini yuboring (masalan: @username):",
        "gift_success_admin": "✅ Foydalanuvchiga {plan} sovg'a qilindi!",
        "gift_success_user": "🎁 Tabriklaymiz! Admin sizga {plan} obunasini sovg'a qildi! 🎉",
        "user_not_found": "❌ Foydalanuvchi topilmadi.",
        "payment_warning": "⚠️ Telegram qoidalari bo'yicha faqat Stars orqali to'lov qilishingiz mumkin. Agar Stars orqali to'lov qilolmasangiz, adminga murojaat qiling: @shoxa_devv",
        "blocked_msg": "⛔ Admin tomonidan bloklandingiz.",
        "user_blocked": "⛔ Foydalanuvchi {user_id} bloklandi.",
        "user_unblocked": "✅ Foydalanuvchi {user_id} blokdan chiqarildi.",
        "user_not_blocked": "ℹ️ Foydalanuvchi {user_id} bloklanmagan.",
        "premium_removed": "🗑 Foydalanuvchi {user_id} premium obunasi o'chirildi.",
        "enter_id_block": "⛔ Bloklash uchun foydalanuvchi ID sini kiriting:",
        "enter_id_unblock": "✅ Blokdan chiqarish uchun foydalanuvchi ID sini kiriting:",
        "enter_id_remove_premium": "🗑 Premiumini o'chirish uchun foydalanuvchi ID sini kiriting:",
        "invited_by": "👋 Sizni foydalanuvchi ID: {referrer_id} taklif qildi",
        "limit_too_high": "⚠️ Maksimal savollar limiti 1000 ta.",
        "enter_limit": "🔢 Kunlik limitni kiriting (maks 1000):",
        "custom_limit_set": "✅ Limit o'rnatildi: {limit} ta so'rov.",
        "restart_success": "🔄 Bot qayta ishga tushirildi!\n\n✅ Joriy suhbat tozalandi\n💎 Premium statusingiz saqlab qolindi\n📜 Tarixingiz saqlab qolindi",
        "video_generation": "Video yaratish 🎬",
        "video_prompt": "📹 Yaratmoqchi bo'lgan videoyingizni batafsil tasvirlang:\n\nMasalan: 'Dengiz bo'yida quyosh botishi, to'lqinlar tinchgina suzib keladi'",
        "video_quality_select": "🎬 Video sifatini tanlang:",
        "video_generating": "⏳ Video yaratilmoqda... Bu bir necha daqiqa vaqt olishi mumkin.",
        "video_success": "✅ Video muvaffaqiyatli yaratildi!",
        "video_error": "❌ Video yaratishda xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.",
        "quality_480p": "480p (Standart)",
        "quality_720p": "720p (HD)",
        "quality_1080p": "1080p (Full HD)",
        "quality_4k": "4K (Ultra HD)",
        "help_command": "ℹ️ **Yordam**",
        "help_text": (
            "📚 **Botdan foydalanish qo'llanmasi**\n\n"
            "👋 **Salom!** Men sun'iy intellektga asoslangan ko'p funksiyali botman.\n\n"
            "🤖 **Chat va Suhbat**:\n"
            "• Menga xohlagan mavzuda yozishingiz mumkin.\n"
            "• **Ovozli xabar**: Menga ovozli xabar yuborsangiz, men uni tushunib, matn yoki ovoz orqali javob qaytaraman.\n\n"
            "🎨 **Rasm Yaratish**:\n"
            "• Asosiy menyudan **'Rasm yaratish 🎨'** tugmasini bosing.\n"
            "• Rasm uchun tavsif yozing (masalan: 'Dengiz bo'yidagi uy').\n"
            "• Kerakli o'lchamni tanlang: **1:1** (Kvadrat), **3:4** (Portret) yoki **16:9** (Keng ekran).\n"
            "• ⚠️ **Limitlar**: Tekin foydalanuvchilar kuniga **3 ta** rasm yaratishi mumkin. Premium foydalanuvchilarda rasm limiti matn limitining 50% ini tashkil qiladi.\n\n"
            "🎬 **Video Yaratish**:\n"
            "• **'Video yaratish 🎬'** tugmasini bosing.\n"
            "• Video g'oyasini yozing.\n"
            "• Sifatni tanlang (480p dan 4K gacha).\n"
            "• *Eslatma*: Video yaratish biroz vaqt olishi mumkin.\n\n"
            "� **Premium Obuna**:\n"
            "• Limitlaringizni oshirish uchun **'Premium sotib olish 💎'** tugmasini bosing.\n"
            "• To'lov Telegram Stars orqali amalga oshiriladi.\n\n"
            "📞 **Yordam va Aloqa**:\n"
            "• Agar muammoga duch kelsangiz, **'Bog'lanish 📞'** tugmasi orqali adminga yozishingiz mumkin."
        ),
        "help_button": "Yordam 🆘",
        "menu_image_gen": "Rasm yaratish 🎨",
        "image_prompt_request": "🎨 Rasm uchun tavsif yozing:\n\nMasalan: \"Kosmosdagi mushuk\"",
        "image_size_select": "📏 Rasm o'lchamini tanlang:",
        "size_1_1": "1:1 (Kvadrat)",
        "size_3_4": "3:4 (Portret)",
        "size_4_3": "4:3 (Albomm)",
        "size_16_9": "16:9 (Keng ekran)",
        "image_limit_reached": "⚠️ Rasm yaratish limiti tugadi!\nPremium olib limitni oshiring.",
        "video_unavailable": "⚠️ Video yaratish xizmati vaqtincha ishlamayapti. Tez orada tuzatiladi!",
    },
    "en": {
        "welcome": "👋 Hello! I'm a GPT-based bot.",
        "subscribe_msg": "📢 To use the bot, please subscribe to the following channels:",
        "subscribe_after": "After subscribing, click the '✅ I subscribed' button.",
        "subscribe_success": "✅ Thank you! You have subscribed.",
        "subscribe_fail": "❌ You haven't subscribed to the channel yet!",
        "select_language": "🌐 Please select a language:",
        "language_selected": "✅ Language selected!",
        "bot_features": "✨ Bot features:\n\n📝 I respond to text and voice messages\n🎤 I convert voice messages to text and respond\n🎨 Image generation - you can create images by simply typing text\n🌐 Multi-language support\n📜 Chat history - your requests and responses are saved",
        "roles": "Roles 👤",
        "history": "History 🫥",
        "back": "Back",
        "main_menu": "Main menu.",
        "main_menu_button": "🏠 Main Menu",
        "thinking": "Thinking of a response 😊",
        "image_help": "To create an image: /image Your description",
        "access_denied": "Access denied.",
        "language": "Language 🌐",
        "currency": "Currency 💱",
        "profile": "Profile 👤",
        "link_contact": "Contact 📞",
        "referral_new": "🎉 Congratulations! You have invited a new user and received +3 permanent limit! 🚀",
        "profile_info": "👤 **Your Profile**\n\n🆔 ID: {user_id}\n📊 Plan: {plan}\n👥 Referrals: {referrals}\n⚖️ Daily Limit: {limit}\n🖼 Image Limit: {image_limit}\n⏳ Remaining Requests: {remaining}\n\n🔗 Your Referral Link:\n<code>{link}</code>\n\n(Get +3 limit for each referral!)",
        "limit_reached": "⚠️ Daily limit reached!\n\nYou can send only 10 free requests in 24 hours. Buy Premium to continue.",
        "buy_premium": "💎 Buy Premium",
        "premium_plans": "💎 Premium Plans:\n\nAll limits are paid via Telegram Stars.",
        "plan_pro": "Pro (100 requests, 100 ⭐️)",
        "plan_pro_plus": "Pro+ (250 requests, 250 ⭐️)",
        "plan_unlimited": "Unlimited (Unlimited, 1000 ⭐️)",
        "premium_success": "✅ Congratulations! You have a Premium subscription! 🎉",
        "currency_enter": "Enter currency code (e.g., USD, EUR, RUB, UZS) or convert (e.g., 1000000 uzs to usd):",
        "currency_result": "Currency rates",
        "currency_error": "Error: Currency code not found or invalid.",
        "currency_conversion": "💱 Conversion result:",
        "currency_conversion_error": "Error: Invalid conversion format. Format: 1000000 uzs to usd",
        "currency_invalid_format": "Invalid format. Example: 1000000 uzs to usd or USD",
        "ad_text": "🤖 Chat with smart AI bot",
        "group_ad_text": "🤖 Chat with smart AI bot",
        "admin_panel": "Admin Panel 🎁",
        "admin_gift_title": "🎁 Admin Panel\n\nSend username to gift (e.g., @username):",
        "gift_success_admin": "✅ Gifted {plan} to user!",
        "gift_success_user": "🎁 Congratulations! Admin gifted you {plan} subscription! 🎉",
        "user_not_found": "❌ User not found.",
        "payment_warning": "⚠️ According to Telegram rules, you can only pay via Stars. If you cannot pay via Stars, contact admin: @shoxa_devv",
        "blocked_msg": "⛔ You have been blocked by admin.",
        "user_blocked": "⛔ User {user_id} has been blocked.",
        "user_unblocked": "✅ User {user_id} has been unblocked.",
        "user_not_blocked": "ℹ️ User {user_id} is not blocked.",
        "premium_removed": "🗑 Premium subscription removed for user {user_id}.",
        "enter_id_block": "⛔ Enter user ID to block:",
        "enter_id_unblock": "✅ Enter user ID to unblock:",
        "enter_id_remove_premium": "🗑 Enter user ID to remove Premium:",
        "invited_by": "👋 You were invited by user ID: {referrer_id}",
        "limit_too_high": "⚠️ Max limit is 1000 requests.",
        "enter_limit": "🔢 Enter daily limit (max 1000):",
        "custom_limit_set": "✅ Limit set to: {limit} requests.",
        "restart_success": "🔄 Bot restarted!\n\n✅ Current chat cleared\n💎 Premium status preserved\n📜 History preserved",
        "video_generation": "Video Generation 🎬",
        "video_prompt": "📹 Describe the video you want to create in detail:\n\nExample: 'Sunset on the beach, waves gently rolling in'",
        "video_quality_select": "🎬 Select video quality:",
        "video_generating": "⏳ Generating video... This may take a few minutes.",
        "video_success": "✅ Video generated successfully!",
        "video_error": "❌ Error generating video. Please try again.",
        "quality_480p": "480p (Standard)",
        "quality_720p": "720p (HD)",
        "quality_1080p": "1080p (Full HD)",
        "quality_4k": "4K (Ultra HD)",
        "help_command": "ℹ️ **Help**",
        "help_text": (
            "📚 **Bot User Guide**\n\n"
            "👋 **Hello!** I am a multi-functional AI bot.\n\n"
            "🤖 **Chat & Conversation**:\n"
            "• You can chat with me on any topic.\n"
            "• **Voice Messages**: Send me a voice message, and I will understand and reply.\n\n"
            "🎨 **Image Generation**:\n"
            "• Click **'Generate Image 🎨'** in the main menu.\n"
            "• Describe the image (e.g., 'House by the sea').\n"
            "• Select size: **1:1** (Square), **3:4** (Portrait), or **16:9** (Wide).\n"
            "• ⚠️ **Limits**: Free users can generate **3 images** per day. Premium users get an image limit equal to 50% of their text limit.\n\n"
            "🎬 **Video Generation**:\n"
            "• Click **'Video Generation 🎬'**.\n"
            "• Describe your video idea.\n"
            "• Select quality (480p to 4K).\n"
            "• *Note*: Video generation may take some time.\n\n"
            "💎 **Premium Subscription**:\n"
            "• Click **'Buy Premium 💎'** to increase your limits.\n"
            "• Payments are made via Telegram Stars.\n\n"
            "📞 **Support**:\n"
            "• If you have issues, click **'Contact 📞'** to reach the admin."
        ),
        "help_button": "Help 🆘",
        "menu_image_gen": "Generate Image 🎨",
        "image_prompt_request": "🎨 Enter image description:\n\nExample: \"Cat in space\"",
        "image_size_select": "📏 Select image size:",
        "size_1_1": "1:1 (Square)",
        "size_3_4": "3:4 (Portrait)",
        "size_4_3": "4:3 (Album)",
        "size_16_9": "16:9 (Wide)",
        "image_limit_reached": "⚠️ Image generation limit reached!\nBuy Premium to increase limits.",
        "video_unavailable": "⚠️ Video generation service is temporarily unavailable.",
    },
    "ru": {
        "welcome": "👋 Привет! Я бот на основе GPT.",
        "subscribe_msg": "📢 Чтобы использовать бота, пожалуйста, подпишитесь на следующие каналы:",
        "subscribe_after": "После подписки нажмите кнопку '✅ Я подписался'.",
        "subscribe_success": "✅ Спасибо! Вы подписались.",
        "subscribe_fail": "❌ Вы еще не подписались на канал!",
        "select_language": "🌐 Пожалуйста, выберите язык:",
        "language_selected": "✅ Язык выбран!",
        "bot_features": "✨ Возможности бота:\n\n📝 Я отвечаю на текстовые и голосовые сообщения\n🎤 Я преобразую голосовые сообщения в текст и отвечаю\n🎨 Создание изображений - вы можете создавать изображения, просто написав текст\n🌐 Многоязычная поддержка\n📜 История чата - ваши запросы и ответы сохраняются",
        "roles": "Роли 👤",
        "history": "История 🫥",
        "back": "Назад",
        "main_menu": "Главное меню.",
        "main_menu_button": "🏠 Главное Меню",
        "thinking": "Думаю над ответом 😊",
        "image_help": "Чтобы создать изображение: /image Ваше описание",
        "access_denied": "Доступ запрещен.",
        "language": "Язык 🌐",
        "currency": "Валюта 💱",
        "profile": "Профиль 👤",
        "link_contact": "Связь 📞",
        "referral_new": "🎉 Поздравляем! Вы пригласили нового пользователя и получили +3 к постоянному лимиту! 🚀",
        "profile_info": "👤 **Ваш Профиль**\n\n🆔 ID: {user_id}\n📊 Тариф: {plan}\n👥 Приглашено: {referrals}\n⚖️ Дневной лимит: {limit}\n🖼 Лимит изображений: {image_limit}\n⏳ Осталось запросов: {remaining}\n\n🔗 Ваша реферальная ссылка:\n<code>{link}</code>\n\n(Получайте +3 лимита за каждое приглашение!)",
        "limit_reached": "⚠️ Дневной лимит исчерпан!\n\nВы можете отправить только 10 бесплатных запросов в 24 часа. Купите Premium для продолжения.",
        "buy_premium": "💎 Купить Premium",
        "premium_plans": "💎 Premium Планы:\n\nВсе лимиты оплачиваются через Telegram Stars.",
        "plan_pro": "Pro (100 запросов, 100 ⭐️)",
        "plan_pro_plus": "Pro+ (250 запросов, 250 ⭐️)",
        "plan_unlimited": "Unlimited (Безлимит, 1000 ⭐️)",
        "premium_success": "✅ Поздравляем! У вас теперь Premium подписка! 🎉",
        "currency_enter": "Введите код валюты (например: USD, EUR, RUB, UZS) или конвертируйте (например: 1000000 uzs to usd):",
        "currency_result": "Курсы валют",
        "currency_error": "Ошибка: Код валюты не найден или неверен.",
        "currency_conversion": "💱 Результат конвертации:",
        "currency_conversion_error": "Ошибка: Неверный формат конвертации. Формат: 1000000 uzs to usd",
        "currency_invalid_format": "Неверный формат. Пример: 1000000 uzs to usd или USD",
        "ad_text": "🤖 Общайтесь с умным ботом",
        "group_ad_text": "🤖 Общайтесь с умным ботом",
        "admin_panel": "Admin Panel 🎁",
        "admin_gift_title": "🎁 Admin Panel\n\nОтправьте юзернейм для подарка (например: @username):",
        "gift_success_admin": "✅ Подарил {plan} пользователю!",
        "gift_success_user": "🎁 Поздравляем! Админ подарил вам подписку {plan}! 🎉",
        "user_not_found": "❌ Пользователь не найден.",
        "payment_warning": "⚠️ Согласно правилам Telegram, оплата возможна только через Stars. Если вы не можете оплатить через Stars, свяжитесь с админом: @shoxa_devv",
        "blocked_msg": "⛔ Вы заблокированы администратором.",
        "user_blocked": "⛔ Пользователь {user_id} заблокирован.",
        "user_unblocked": "✅ Пользователь {user_id} разблокирован.",
        "user_not_blocked": "ℹ️ Пользователь {user_id} не был заблокирован.",
        "premium_removed": "🗑 Premium подписка удалена у пользователя {user_id}.",
        "enter_id_block": "⛔ Введите ID пользователя для блокировки:",
        "enter_id_unblock": "✅ Введите ID пользователя для разблокировки:",
        "enter_id_remove_premium": "🗑 Введите ID пользователя для удаления Premium:",
        "invited_by": "👋 Вас пригласил пользователь ID: {referrer_id}",
        "limit_too_high": "⚠️ Максимальный лимит: 1000 запросов.",
        "enter_limit": "🔢 Введите дневной лимит (макс 1000):",
        "custom_limit_set": "✅ Установлен лимит: {limit} запросов.",
        "restart_success": "🔄 Бот перезапущен!\n\n✅ Текущий чат очищен\n💎 Premium статус сохранён\n📜 История сохранена",
        "video_generation": "Создание видео 🎬",
        "video_prompt": "📹 Подробно опишите видео, которое хотите создать:\n\nНапример: 'Закат на пляже, волны мягко накатывают на берег'",
        "video_quality_select": "🎬 Выберите качество видео:",
        "video_generating": "⏳ Создаём видео... Это может занять несколько минут.",
        "video_success": "✅ Видео успешно создано!",
        "video_error": "❌ Ошибка при создании видео. Пожалуйста, попробуйте снова.",
        "quality_480p": "480p (Стандарт)",
        "quality_720p": "720p (HD)",
        "quality_1080p": "1080p (Full HD)",
        "quality_4k": "4K (Ultra HD)",
        "help_command": "ℹ️ **Помощь**",
        "help_text": (
            "📚 **Руководство пользователя**\n\n"
            "👋 **Привет!** Я многофункциональный ИИ-бот.\n\n"
            "🤖 **Чат и Общение**:\n"
            "• Вы можете общаться со мной на любую тему.\n"
            "• **Голосовые сообщения**: Отправьте мне голосовое сообщение, и я отвечу текстом или голосом.\n\n"
            "🎨 **Создание Изображений**:\n"
            "• Нажмите **'Создать изображение 🎨'** в главном меню.\n"
            "• Опишите изображение (например, 'Дом у моря').\n"
            "• Выберите размер: **1:1** (Квадрат), **3:4** (Портрет) или **16:9** (Широкий).\n"
            "• ⚠️ **Лимиты**: Бесплатные пользователи могут создавать **3 изображения** в день. У Premium пользователей лимит изображений составляет 50% от текстового лимита.\n\n"
            "🎬 **Создание Видео**:\n"
            "• Нажмите **'Создание видео 🎬'**.\n"
            "• Опишите идею видео.\n"
            "• Выберите качество (от 480p до 4K).\n"
            "• *Примечание*: Создание видео может занять некоторое время.\n\n"
            "💎 **Premium Подписка**:\n"
            "• Нажмите **'Купить Premium 💎'**, чтобы увеличить лимиты.\n"
            "• Оплата производится через Telegram Stars.\n\n"
            "📞 **Поддержка**:\n"
            "• Если возникли проблемы, нажмите **'Связь 📞'**, чтобы написать админу."
        ),
        "help_button": "Помощь 🆘",
        "menu_image_gen": "Создать изображение 🎨",
        "image_prompt_request": "🎨 Опишите изображение:\n\nНапример: \"Кот в космосе\"",
        "image_size_select": "📏 Выберите размер:",
        "size_1_1": "1:1 (Квадрат)",
        "size_3_4": "3:4 (Портрет)",
        "size_4_3": "4:3 (Альбом)",
        "size_16_9": "16:9 (Широкий)",
        "image_limit_reached": "⚠️ Лимит на создание изображений исчерпан!\nКупите Premium для увеличения.",
        "video_unavailable": "⚠️ Сервис создания видео временно недоступен.",
    }
}


def get_text(user_id: int, key: str) -> str:
    """Foydalanuvchi tiliga mos xabarni qaytaradi"""
    # Check cache first
    if user_id in user_languages:
        lang = user_languages[user_id]
    else:
        # Check DB
        lang = user_manager.get_language(user_id)
        if lang:
            user_languages[user_id] = lang
        else:
            lang = "uz" # Default
            
    return TRANSLATIONS.get(lang, TRANSLATIONS["uz"]).get(key, key)




def is_admin(chat_id: int) -> bool:
    return chat_id in ADMIN_IDS

def detect_language(text: str) -> str:
    """Matn tilini aniqlash (uz, en, ru)"""
    if not text:
        return "uz"
    text_lower = text.lower()
    cyrillic_chars = sum(1 for char in text if 'а' <= char.lower() <= 'я' or char.lower() == 'ё')
    if cyrillic_chars > len(text) * 0.3:
        return "ru"
    english_words = ['the', 'is', 'are', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'this', 'that', 'what', 'where', 'when', 'why', 'how', 'can', 'will', 'would', 'should', 'could', 'may', 'might']
    english_count = sum(1 for word in english_words if word in text_lower)
    if english_count > 2:
        return "en"
    return "uz"

def is_image_request(text: str, lang: str) -> bool:
    """Matnda tasvir yaratish so'ralganini aniqlash"""
    if not text:
        return False
    text_lower = text.lower()
    image_keywords = {
        "uz": ["rasm", "tasvir", "surat", "rasm yarat", "tasvir yarat", "surat yarat", "rasm chiz", "tasvir chiz"],
        "en": ["image", "picture", "draw", "create image", "generate image", "make image", "draw picture", "create picture"],
        "ru": ["изображение", "картинка", "рисунок", "создать изображение", "нарисовать", "создать картинку", "нарисовать картинку"]
    }
    keywords = image_keywords.get(lang, image_keywords["uz"])
    return any(keyword in text_lower for keyword in keywords)

def normalize_channel(channel: str) -> str:
    """Kanal nomini normalize qilish (@ qo'shish)"""
    if channel.startswith("@"):
        return channel
    return f"@{channel}"

def get_currency_rates(base_currency: str) -> dict:
    """Valyuta kurslarini olish (free API)"""
    try:
        url = f"https://api.exchangerate-api.com/v4/latest/{base_currency.upper()}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("rates", {})
        return {}
    except Exception as e:
        print(f"Valyuta kurslari olishda xatolik: {e}")
        return {}

def format_currency_rates(rates: dict, base_currency: str, user_id: int) -> str:
    """Valyuta kurslarini formatlash"""
    if not rates:
        return get_text(user_id, "currency_error")
    major_currencies = ["USD", "EUR", "GBP", "JPY", "CNY", "RUB", "UZS", "KZT", "TRY", "AED", "SAR", "INR"]
    user_lang = user_languages.get(user_id, "uz")
    result = f"💱 1 {base_currency.upper()} = \n\n"
    for currency in major_currencies:
        if currency != base_currency.upper() and currency in rates:
            rate = rates[currency]
            result += f"• {currency}: {rate:.4f}\n"
    other_currencies = [c for c in sorted(rates.keys()) if c not in major_currencies and c != base_currency.upper()]
    if other_currencies:
        if user_lang == "uz":
            result += f"\n... va {len(other_currencies)} ta boshqa valyuta"
        elif user_lang == "ru":
            result += f"\n... и {len(other_currencies)} других валют"
        else:
            result += f"\n... and {len(other_currencies)} other currencies"
    return result

def parse_conversion_request(text: str) -> tuple:
    """Konvertatsiya so'rovini parse qilish"""
    text_original = text.strip()
    text = text_original.upper()
    number_match = re.search(r'[\d,.\s]+', text)
    if not number_match:
        return (None, None, None)
    amount_str = number_match.group(0).replace(',', '').replace(' ', '')
    try:
        amount = float(amount_str)
    except ValueError:
        return (None, None, None)
    to_match = re.search(r'\b(?:TO|IN|В|К|КО)\b', text)
    if not to_match:
        return (None, None, None)
    to_pos = to_match.start()
    before_to = text[:to_pos].strip()
    after_to = text[to_match.end():].strip()
    from_match = re.search(r'\b([A-Z]{3})\b', before_to)
    if not from_match:
        return (None, None, None)
    from_currency = from_match.group(1)
    to_match_curr = re.search(r'\b([A-Z]{3})\b', after_to)
    if not to_match_curr:
        return (None, None, None)
    to_currency = to_match_curr.group(1)
    if from_currency and to_currency:
        return (amount, from_currency, to_currency)
    return (None, None, None)

def convert_currency(amount: float, from_currency: str, to_currency: str, user_id: int) -> str:
    """Valyuta konvertatsiyasini hisoblash"""
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
                result += f"\n\n(1 {to_currency.upper()} = {reverse_rates[from_currency.upper()]:,.4f} {from_currency.upper()})"
            return result
        else:
            return get_text(user_id, "currency_error")
    except Exception as e:
        print(f"Konvertatsiya xatolik: {e}")
        return get_text(user_id, "currency_conversion_error")

async def check_subscription(user_id: int) -> bool:
    """Barcha kanallarga obuna bo'lganligini tekshiradi"""
    for channel in CHANNELS:
        try:
            normalized_channel = normalize_channel(channel)
            member = await bot.get_chat_member(normalized_channel, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except Exception:
            return False
    return True

def subscription_keyboard(user_id: int = None):
    """Majburiy obuna uchun inline keyboard"""
    lang = user_languages.get(user_id, "uz") if user_id else "uz"
    subscribed_text = {
        "uz": "✅ Obuna bo'ldim",
        "en": "✅ I subscribed",
        "ru": "✅ Я подписался"
    }
    kb = InlineKeyboardBuilder()
    for channel in CHANNELS:
        channel_name = channel.lstrip("@")
        channel_display = channel_name.replace("_", " ").title()
        kb.button(text=f"📢 {channel_display}", url=f"https://t.me/{channel_name}")
    kb.button(text=subscribed_text.get(lang, subscribed_text["uz"]), callback_data="check_subscription")
    kb.adjust(1)
    return kb.as_markup()

def language_select_keyboard():
    """Til tanlash uchun inline keyboard"""
    kb = InlineKeyboardBuilder()
    kb.button(text="🇺🇿 O'zbek", callback_data="lang_uz")
    kb.button(text="🇬🇧 English", callback_data="lang_en")
    kb.button(text="🇷🇺 Русский", callback_data="lang_ru")
    kb.adjust(3)
    return kb.as_markup()


# Admin States
ADMIN_STATES = {} # admin_id -> {"state": str, "target_uid": int}
USER_STATES = {} # user_id -> {"state": str, "video_description": str, "video_quality": str}

def main_menu_keyboard(user_id: int):
    """Asosiy menyu (inline)"""
    kb = InlineKeyboardBuilder()
    
    # 2-column layout for main features
    kb.button(text=get_text(user_id, "profile"), callback_data="menu_profile")
    kb.button(text=get_text(user_id, "history"), callback_data="menu_history")
    
    kb.button(text=get_text(user_id, "menu_image_gen"), callback_data="menu_image")
    kb.button(text=get_text(user_id, "video_generation"), callback_data="menu_video")
    
    kb.button(text=get_text(user_id, "help_button"), callback_data="menu_help")
    kb.button(text=get_text(user_id, "language"), callback_data="menu_language")
    
    kb.adjust(2, 2, 2)
    
    # Premium and Contact at bottom (full width)
    kb2 = InlineKeyboardBuilder()
    kb2.button(text=get_text(user_id, "buy_premium"), callback_data="menu_premium")
    kb2.button(text=get_text(user_id, "link_contact"), url="https://t.me/shoxa_devv")
    
    kb2.adjust(1)
    
    # Admin Panel (if admin)
    if user_id in ADMIN_IDS:
        kb2.button(text=get_text(user_id, "admin_panel"), callback_data="admin_panel")
        
    kb.attach(kb2)
    
    return kb.as_markup()

def image_size_keyboard(user_id: int):
    """Rasm o'lchamini tanlash klaviaturasi"""
    kb = InlineKeyboardBuilder()
    kb.button(text=get_text(user_id, "size_1_1"), callback_data="size_1024x1024")
    kb.button(text=get_text(user_id, "size_3_4"), callback_data="size_1024x1792") # Approx 9:16 is DALL-E 3 portrait
    kb.button(text=get_text(user_id, "size_16_9"), callback_data="size_1792x1024")
    kb.button(text=get_text(user_id, "back"), callback_data="back_to_main")
    kb.adjust(2)
    return kb.as_markup()

def admin_menu_keyboard(user_id: int):
    """Admin panel menyusi"""
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
    """Profil uchun keyboard"""
    kb = InlineKeyboardBuilder()
    kb.button(text=get_text(user_id, "buy_premium"), callback_data="menu_premium")
    kb.button(text=get_text(user_id, "back"), callback_data="back_to_main")
    kb.adjust(1)
    return kb.as_markup()

def premium_keyboard(user_id: int):
    """Premium tariflar inline keyboard"""
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

def get_main_menu_reply_kb(user_id: int):
    """Asosiy menyuga qaytish uchun Reply Keyboard"""
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    button_text = get_text(user_id, "main_menu_button")
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=button_text)]],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    return kb

# Helper function removed


def save_history(history):
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def video_quality_keyboard(user_id: int):
    """Video sifatini tanlash klaviaturasi"""
    kb = InlineKeyboardBuilder()
    kb.button(text=get_text(user_id, "quality_480p"), callback_data="video_quality_480p")
    kb.button(text=get_text(user_id, "quality_720p"), callback_data="video_quality_720p")
    kb.button(text=get_text(user_id, "quality_1080p"), callback_data="video_quality_1080p")
    kb.button(text=get_text(user_id, "quality_4k"), callback_data="video_quality_4k")
    kb.button(text=get_text(user_id, "back"), callback_data="back_to_main")
    kb.adjust(1)
    return kb.as_markup()

def append_history(user_id: int, entry: dict):
    history = load_history()
    key = str(user_id)
    user_history = history.get(key, [])
    user_history.append(entry)
    history[key] = user_history[-MAX_HISTORY:]
    save_history(history)

@dp.callback_query(F.data == "check_subscription")
async def check_subscription_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    if await check_subscription(user_id):
        await callback.answer(get_text(user_id, "subscribe_success"), show_alert=True)
        await callback.message.delete()
        # Agar til tanlanmagan bo'lsa, til tanlashni ko'rsatish
        if user_id not in user_languages:
            await callback.message.answer(
                get_text(user_id, "select_language"),
                reply_markup=language_select_keyboard()
            )
        else:
            await callback.message.answer(
                f"{get_text(user_id, 'welcome')}\n\n{get_text(user_id, 'bot_features')}",
                reply_markup=main_menu_keyboard(user_id),
            )
    else:
        await callback.answer(get_text(user_id, "subscribe_fail"), show_alert=True)

def restart_bot(cmd):
    if cmd == "/start":
        print("")
        os.execv(sys.executable, ['python'] + sys.argv)
    else:
        print("Buyruq noto‘g‘ri")



@dp.callback_query(F.data.startswith("lang_"))
async def language_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    lang_code = callback.data.split("_")[1]  # lang_uz -> uz

    user_languages[user_id] = lang_code
    await callback.answer(get_text(user_id, "language_selected"), show_alert=True)
    # Asosiy menyuga qaytish
    await callback.message.edit_text(
        f"{get_text(user_id, 'welcome')}\n\n{get_text(user_id, 'bot_features')}",
        reply_markup=main_menu_keyboard(user_id),
    )

@dp.callback_query(
    F.data.startswith("menu_") | 
    F.data.startswith("gift_plan_") | 
    F.data.startswith("gift_dur_") |
    F.data.startswith("admin_") |
    (F.data.in_({"back_to_main", "admin_panel"}))
)
async def menu_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    
    # Check block
    if user_manager.is_blocked(user_id):
        await callback.answer(get_text(user_id, "blocked_msg"), show_alert=True)
        return

    action = callback.data

    if action == "back_to_main":
        await callback.message.edit_text(
            f"{get_text(user_id, 'welcome')}\n\n{get_text(user_id, 'bot_features')}",
            reply_markup=main_menu_keyboard(user_id)
        )
    elif action == "menu_history":
        history = format_history(user_id)
        # Check if history is too long, maybe trim? limit is handled in chatgpt.py
        await callback.message.edit_text(
            f"{get_text(user_id, 'history')}:\n\n{history}",
            reply_markup=back_button(user_id)
        )
    elif action == "menu_language":
        await callback.message.edit_text(
            get_text(user_id, "select_language"),
            reply_markup=language_select_keyboard()
        )
    elif action == "menu_profile":
        user_info = user_manager.get_user(user_id)
        if "custom_limit" in user_info:
            limit = user_info["custom_limit"]
        else:
            limit = LIMITS.get(user_info.get("plan", PLAN_FREE), 10)
            
        if not isinstance(limit, (int, float)):
             limit = 10 # Fallback

        extra = user_info.get("referral_count", 0) * 3
        total_limit = limit + extra
        if limit == float('inf'):
            total_limit_str = "♾"
        else:
            total_limit_str = str(total_limit)

        
        remaining = user_manager.get_remaining_limit(user_id)
        if remaining > 900000:
            remaining_str = "♾"
        else:
            remaining_str = str(remaining)
            
        bot_username = (await bot.get_me()).username
        ref_link = f"https://t.me/{bot_username}?start={user_id}"
        
        # Show Expiry
        plan_name = user_info.get("plan", PLAN_FREE).title()
        expiry = user_info.get("subscription_end")
        if expiry:
            try:
                exp_date = datetime.fromisoformat(expiry)
                import math
                if exp_date.year > 3000: # Lifetime check
                     plan_name += " (Abadiy)"
                else: 
                     days_left = (exp_date - datetime.now()).days
                     plan_name += f" ({days_left} kun qoldi)"
            except:
                pass
        
        # Calculate image limit string
        if limit == float('inf'):
            image_limit_str = "♾"
        else:
            # Replicate users.py check_image_limit logic approximately for display
            if user_info.get("plan") == PLAN_UNLIMITED:
                image_limit_str = "♾"
            elif user_info.get("plan") == PLAN_FREE:
                image_limit_str = "3"
            else:
                 # Premium: 50%
                 if "custom_limit" in user_info:
                     base = user_info["custom_limit"]
                 else:
                     base = LIMITS.get(user_info.get("plan", PLAN_FREE), 100)
                 if not isinstance(base, (int, float)): base = 100
                 image_limit_str = str(int(base * 0.5))

        text = get_text(user_id, "profile_info").format(
            user_id=user_id,
            plan=plan_name,
            referrals=user_info.get("referral_count", 0),
            limit=total_limit_str,
            image_limit=image_limit_str,
            remaining=remaining_str,
            link=ref_link
        )
        await callback.message.edit_text(text, reply_markup=profile_keyboard(user_id), parse_mode="HTML")
    elif action == "menu_premium":
        text = f"{get_text(user_id, 'premium_plans')}\n\n{get_text(user_id, 'payment_warning')}"
        await callback.message.edit_text(
             text,
             reply_markup=premium_keyboard(user_id)
        )
    elif action == "menu_video":
        # Check API Token availability first
        if not os.getenv("REPLICATE_API_TOKEN"):
             await callback.answer(get_text(user_id, "video_unavailable"), show_alert=True)
             return
             
        # Start video generation flow
        USER_STATES[user_id] = {"state": "waiting_video_description"}
        
        await callback.message.delete()
        await callback.message.answer(
            get_text(user_id, "video_prompt"),
            reply_markup=get_main_menu_reply_kb(user_id) 
        )
    elif action == "menu_image":
        # Start image generation flow
        # Check limit first
        if not user_manager.check_image_limit(user_id):
            kb = InlineKeyboardBuilder()
            kb.button(text=get_text(user_id, "buy_premium"), callback_data="menu_premium")
            await callback.message.edit_text(get_text(user_id, "image_limit_reached"), reply_markup=kb.as_markup())
            return
            
        USER_STATES[user_id] = {"state": "waiting_image_prompt"}
        await callback.message.delete()
        await callback.message.answer(
            get_text(user_id, "image_prompt_request"),
            reply_markup=get_main_menu_reply_kb(user_id)
        )
    elif action == "menu_help":
        await callback.message.edit_text(
            get_text(user_id, "help_text"),
            reply_markup=back_button(user_id),
            parse_mode="Markdown"
        )
    elif action == "admin_panel":
        if user_id not in ADMIN_IDS:
             return
        # Dynamic check if ID added later manually to specific list (if implemented),
        # currently ADMIN_IDS is imported from data.py which loads .env
        await callback.message.edit_text("⚙️ Admin Paneliga xush kelibsiz!", reply_markup=admin_menu_keyboard(user_id))
        
    elif action == "admin_stats":
        if user_id not in ADMIN_IDS: return
        # Count users
        total_users = len(user_manager.users)
        # Active today
        today = datetime.now().date().isoformat()
        active_today = sum(1 for u in user_manager.users.values() if u.get("usage_date") == today)
        
        text = (
            f"📊 **Bot Statistikasi**\n\n"
            f"👤 Jami foydalanuvchilar: {total_users}\n"
            f"🔥 Bugun faol: {active_today}\n"
        )
        kb = InlineKeyboardBuilder()
        kb.button(text="Orqaga", callback_data="admin_panel")
        await callback.message.edit_text(text, reply_markup=kb.as_markup())
        
    elif action == "admin_api":
        if user_id not in ADMIN_IDS: return
        text = stats.get_stats_text()
        kb = InlineKeyboardBuilder()
        kb.button(text="Orqaga", callback_data="admin_panel")
        await callback.message.edit_text(text, reply_markup=kb.as_markup())

    elif action == "admin_gift_start":
        if user_id not in ADMIN_IDS: return
        ADMIN_STATES[user_id] = {"state": "waiting_gift_id"}
        kb = InlineKeyboardBuilder()
        kb.button(text="Bekor qilish", callback_data="admin_cancel")
        await callback.message.edit_text(
            "Iltimos, hadya qilmoqchi bo'lgan odamingizni telegram akkaunt chat idsini kiriting:",
            reply_markup=kb.as_markup()
        )
        
    elif action == "admin_block_start":
        if user_id not in ADMIN_IDS: return
        ADMIN_STATES[user_id] = {"state": "waiting_block_id"}
        kb = InlineKeyboardBuilder()
        kb.button(text="Bekor qilish", callback_data="admin_cancel")
        await callback.message.edit_text(get_text(user_id, "enter_id_block"), reply_markup=kb.as_markup())
        
    elif action == "admin_unblock_start":
        if user_id not in ADMIN_IDS: return
        ADMIN_STATES[user_id] = {"state": "waiting_unblock_id"}
        kb = InlineKeyboardBuilder()
        kb.button(text="Bekor qilish", callback_data="admin_cancel")
        await callback.message.edit_text(get_text(user_id, "enter_id_unblock"), reply_markup=kb.as_markup())

    elif action == "admin_remove_premium_start":
        if user_id not in ADMIN_IDS: return
        ADMIN_STATES[user_id] = {"state": "waiting_remove_premium_id"}
        kb = InlineKeyboardBuilder()
        kb.button(text="Bekor qilish", callback_data="admin_cancel")
        await callback.message.edit_text(get_text(user_id, "enter_id_remove_premium"), reply_markup=kb.as_markup())

    elif action == "admin_cancel":
        if user_id in ADMIN_STATES:
            del ADMIN_STATES[user_id]
        await callback.message.edit_text("Bekor qilindi.", reply_markup=main_menu_keyboard(user_id))
        
    elif action.startswith("gift_plan_"):
        # gift_plan_PLAN_UID
        parts = action.split("_")
        target_uid = int(parts[-1])
        plan_parts = parts[2:-1] 
        plan = "_".join(plan_parts)
        
        if plan == "custom":
            ADMIN_STATES[user_id] = {"state": "waiting_custom_limit", "target_uid": target_uid}
            kb = InlineKeyboardBuilder()
            kb.button(text="Bekor qilish", callback_data="admin_cancel")
            await callback.message.edit_text(get_text(user_id, "enter_limit"), reply_markup=kb.as_markup())
            return

        # Direct set plan with default duration (30 days)
        duration = 30
        custom_limit = None
        
        user_manager.set_plan(target_uid, plan, duration, custom_limit)
        dur_text = f"{duration} kun"
        
        await callback.message.edit_text(
            f"✅ Bajarildi!\nID: {target_uid}\nPlan: {plan.upper()}\nMuddat: {dur_text}",
            reply_markup=main_menu_keyboard(user_id)
        )
        
        # Notify User
        try:
            await bot.send_message(
                target_uid, 
                f"🎁 Tabriklaymiz! Admin sizga {plan.upper()} obunasini {dur_text} muddatga hadya qildi! 🎉"
            )
        except:
            pass
        
    elif action.startswith("gift_dur_"):
        # gift_dur_DAYS_PLAN_UID
        parts = action.split("_")
        # parts: ['gift', 'dur', '30', 'pro', '123456']
        duration = int(parts[2])
        # plan might be 'pro' or 'pro_plus' or 'custom'
        # target_uid is last
        target_uid = int(parts[-1])
        plan_parts = parts[3:-1]
        plan = "_".join(plan_parts)
        
        # Check if we have a stored custom limit in state logic? 
        # Actually for 'custom', the plan string in callback is 'custom'.
        # We need to pass the custom amount too? Or store in ADMIN_STATES?
        # But wait, the flow is: custom button -> enter number -> show duration keyboard -> select duration.
        # So we need to pass the amount in the duration callback data OR retrieve from state (but state might be lost or messy).
        # Better: When entering number, we ask usage logic. 
        # Let's adjust admin_input_handler for custom limit. It will show duration keyboard.
        # And that duration keyboard callback MUST include the limit.
        # Let's change duration keyboard signature?
        # Or encode limit in 'plan' part? e.g. 'custom-500'.
        
        custom_limit = None
        if plan.startswith("custom-"):
            custom_limit = int(plan.split("-")[1])
            plan = "custom"
        
        user_manager.set_plan(target_uid, plan, duration, custom_limit)
        
        dur_text = f"{duration} kun"
        
        await callback.message.edit_text(
            f"✅ Bajarildi!\nID: {target_uid}\nPlan: {plan}\nMuddat: {dur_text}\nLimit: {custom_limit if custom_limit else 'Standart'}",
            reply_markup=main_menu_keyboard(user_id)
        )
        
        # Notify User
        try:
            await bot.send_message(
                target_uid, 
                f"🎁 Tabriklaymiz! Admin sizga {plan.upper()} obunasini {dur_text} muddatga hadya qildi! 🎉"
            )
        except:
            pass
            
    await callback.answer()






@dp.callback_query(F.data.startswith("video_quality_"))
async def video_quality_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    quality = callback.data.split("_")[-1]  # Extract quality (480p, 720p, etc.)
    
    if user_id not in USER_STATES or USER_STATES[user_id].get("state") != "waiting_video_quality":
        await callback.answer("Xatolik: Avval video tavsifini yuboring", show_alert=True)
        return
    
    # Get video description from state
    video_description = USER_STATES[user_id].get("video_description", "")
    
    # Clear state
    del USER_STATES[user_id]
    
    # Check limit
    if not user_manager.check_limit(user_id):
        kb = InlineKeyboardBuilder()
        kb.button(text=get_text(user_id, "buy_premium"), callback_data="menu_premium")
        await callback.message.edit_text(get_text(user_id, "limit_reached"), reply_markup=kb.as_markup())
        return
    
    user_manager.increment_usage(user_id)
    
    # Show generating message
    status_msg = await callback.message.edit_text(get_text(user_id, "video_generating"))
    
    try:
        # Import video generator
        from video_generator import generate_video, download_video
        import os
        
        # Generate video (Run in thread to be non-blocking)
        video_url = await asyncio.to_thread(generate_video, video_description, quality)
        
        # Download video (Run in thread)
        os.makedirs("videos", exist_ok=True)
        video_path = f"videos/{user_id}_{quality}.mp4"
        await asyncio.to_thread(download_video, video_url, video_path)
        
        # Send video
        await callback.message.answer(get_text(user_id, "video_success"))
        
        from aiogram.types import FSInputFile, ReplyKeyboardRemove
        video_file = FSInputFile(video_path)
        
        await bot.send_video(
            callback.message.chat.id,
            video_file,
            caption=f"🎬 {video_description[:100]}...",
            reply_markup=ReplyKeyboardRemove()
        )
        
        # Clean up
        os.remove(video_path)
        
        # Show main menu
        await callback.message.answer(
            get_text(user_id, "main_menu"),
            reply_markup=main_menu_keyboard(user_id)
        )
        
    except Exception as e:
        await callback.message.answer(
            f"{get_text(user_id, 'video_error')}\n\nError: {str(e)}"
        )
        await callback.message.answer(
            get_text(user_id, "main_menu"),
            reply_markup=main_menu_keyboard(user_id)
        )
    
    await callback.answer()



@dp.message(lambda msg: msg.from_user.id in USER_STATES and USER_STATES[msg.from_user.id].get("state") == "waiting_video_description")
async def video_description_handler(msg: types.Message):
    user_id = msg.from_user.id
    video_description = msg.text.strip()
    
    if not video_description or len(video_description) < 10:
        await msg.answer("Iltimos, video tavsifini batafsil yozing (kamida 10 ta belgi)")
        return
    
    # Save description and move to quality selection
    USER_STATES[user_id] = {
        "state": "waiting_video_quality",
        "video_description": video_description
    }
    
    await msg.answer(
        get_text(user_id, "video_quality_select"),
        reply_markup=video_quality_keyboard(user_id)
    )

    await msg.answer(
        get_text(user_id, "video_quality_select"),
        reply_markup=video_quality_keyboard(user_id)
    )

@dp.message(lambda msg: msg.from_user.id in USER_STATES and USER_STATES[msg.from_user.id].get("state") == "waiting_image_prompt")
async def image_prompt_handler(msg: types.Message):
    user_id = msg.from_user.id
    prompt = msg.text.strip()
    
    if not prompt:
         await msg.answer("Matn kiriting!")
         return
         
    # Save prompt, ask for size
    USER_STATES[user_id] = {
        "state": "waiting_image_size",
        "image_prompt": prompt
    }
    
    await msg.answer(
        get_text(user_id, "image_size_select"),
        reply_markup=image_size_keyboard(user_id)
    )

@dp.callback_query(F.data.startswith("size_"))
async def image_size_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    size = callback.data.split("_", 1)[1] # 1024x1024
    
    if user_id not in USER_STATES or USER_STATES[user_id].get("state") != "waiting_image_size":
        await callback.answer("Error state", show_alert=True)
        return
        
    prompt = USER_STATES[user_id].get("image_prompt")
    del USER_STATES[user_id]
    
    # Check limit again
    if not user_manager.check_image_limit(user_id):
        kb = InlineKeyboardBuilder()
        kb.button(text=get_text(user_id, "buy_premium"), callback_data="menu_premium")
        await callback.message.edit_text(get_text(user_id, "image_limit_reached"), reply_markup=kb.as_markup())
        return

    user_manager.increment_image_usage(user_id)

    # Generate
    # Delete menu message or edit it?
    status_msg = await callback.message.edit_text(get_text(user_id, "thinking"))
    
    try:
        image_url = await asyncio.to_thread(text_to_image, prompt, size)
        
        # Send photo
        await callback.message.delete() # delete status
        
        # We need to use ReplyKeyboardRemove if we used reply keyboard?
        # Yes, we entered flow with reply keyboard.
        from aiogram.types import ReplyKeyboardRemove
        
        await bot.send_photo(
            callback.message.chat.id,
            image_url,
            caption=f"🎨 {prompt[:100]}...",
            reply_markup=ReplyKeyboardRemove()
        )
        
        # Save history
        append_history(
            user_id,
            {
                "ts": datetime.utcnow().isoformat(),
                "type": "image",
                "prompt": prompt,
                "response": image_url,
                "role": "Assistant",
                "size": size
            }
        )
        
        # Show main menu again
        await callback.message.answer(
            get_text(user_id, "main_menu"),
            reply_markup=main_menu_keyboard(user_id)
        )
        
    except Exception as e:
         await callback.message.edit_text(f"Xatolik: {str(e)}")
         await callback.message.answer("Menu", reply_markup=main_menu_keyboard(user_id))

@dp.message(lambda msg: msg.text in ["🏠 Asosiy Menyu", "🏠 Main Menu", "🏠 Главное Меню"])
async def main_menu_reply_button_handler(msg: types.Message):
    """Handle the Reply Button click to return to main menu"""
    user_id = msg.from_user.id
    
    # Clear any state
    if user_id in USER_STATES:
        del USER_STATES[user_id]
        
    # Remove Reply Keyboard and show Inline Main Menu
    from aiogram.types import ReplyKeyboardRemove
    await msg.answer(
        get_text(user_id, "main_menu"),
        reply_markup=ReplyKeyboardRemove()
    )
    await msg.answer(
        f"{get_text(user_id, 'welcome')}\n\n{get_text(user_id, 'bot_features')}",
        reply_markup=main_menu_keyboard(user_id)
    )


@dp.message(lambda msg: msg.from_user.id in ADMIN_STATES)
async def admin_input_handler(msg: types.Message):
    user_id = msg.from_user.id
    state_data = ADMIN_STATES[user_id]
    state = state_data.get("state")
    
    if state == "waiting_gift_id":
        try:
            target_uid = int(msg.text.strip())
            # Validate if plausible (simple check)
            if target_uid < 0: raise ValueError
            
            # Move to next step
            # We don't really need to store UID in state if we pass it in callback, 
            # but clearing state is good practice to avoid stuck state.
            # Actually, we will just show keyboard and clear state only when cancel or done.
            # Let's keep state open or just clear it? 
            # If we show keyboard, the interaction moves to buttons. 
            # Input is done. We can clear state or keep it until finished.
            # Let's clear 'waiting_gift_id' state as we are now 'waiting_gift_plan' (which is button driven).
            del ADMIN_STATES[user_id] 
            
            await msg.answer(
                f"Foydalanuvchi ID: {target_uid}\nQaysi planni bermoqchisiz?",
                reply_markup=admin_gift_keyboard(target_uid)
            )
        except ValueError:
            await msg.answer("Iltimos, to'g'ri raqamli ID kiriting.")
            
    elif state == "waiting_block_id":
        try:
            target_uid = int(msg.text.strip())
            user_manager.block_user(target_uid)
            del ADMIN_STATES[user_id]
            await msg.answer(get_text(user_id, "user_blocked").format(user_id=target_uid), reply_markup=admin_menu_keyboard(user_id))
        except ValueError:
            await msg.answer("Error ID.")
            
    elif state == "waiting_unblock_id":
        try:
            target_uid = int(msg.text.strip())
            if not user_manager.is_blocked(target_uid):
                await msg.answer(get_text(user_id, "user_not_blocked").format(user_id=target_uid))
            else:
                user_manager.unblock_user(target_uid)
                await msg.answer(get_text(user_id, "user_unblocked").format(user_id=target_uid), reply_markup=admin_menu_keyboard(user_id))
            del ADMIN_STATES[user_id]
        except ValueError:
             await msg.answer("Error ID.")

    elif state == "waiting_remove_premium_id":
        try:
            target_uid = int(msg.text.strip())
            user_manager.remove_premium(target_uid)
            del ADMIN_STATES[user_id]
            await msg.answer(get_text(user_id, "premium_removed").format(user_id=target_uid), reply_markup=admin_menu_keyboard(user_id))
        except ValueError:
             await msg.answer("Error ID.")

    elif state == "waiting_custom_limit":
        try:
            limit = int(msg.text.strip())
            if limit > 1000:
                await msg.answer(get_text(user_id, "limit_too_high"))
                return
            
            target_uid = state_data.get("target_uid")
            
            # Direct set custom limit with 30 days
            duration = 30
            plan = "custom"
            
            user_manager.set_plan(target_uid, plan, duration, limit)
            
            dur_text = f"{duration} kun"
            
            await msg.answer(
                f"✅ Bajarildi!\nID: {target_uid}\nPlan: {plan.upper()}\nLimit: {limit}\nMuddat: {dur_text}",
                reply_markup=admin_menu_keyboard(user_id)
            )
            
            # Notify User
            try:
                await bot.send_message(
                    target_uid, 
                    f"🎁 Tabriklaymiz! Admin sizga {plan.upper()} obunasini (Limit: {limit}) {dur_text} muddatga hadya qildi! 🎉"
                )
            except:
                pass
            
            del ADMIN_STATES[user_id] # Done
            
        except ValueError:
            await msg.answer("Raqam kiriting.")
             
    else:
        # Unknown state
        del ADMIN_STATES[user_id]

@dp.message(F.forward_from | F.forward_from_chat)
async def forwarded_message_handler(msg: types.Message):
    """Forward qilingan xabarlarga reklama qo'shish"""
    # Faqat forward qilingan xabarlarga javob berish
    if not (msg.forward_from or msg.forward_from_chat):
        return

    user_id = msg.from_user.id if msg.from_user else None
    # Forward qilingan xabarga reklama qo'shish
    ad_text = get_ad_text(user_id)
    await msg.reply(ad_text)

@dp.message()
async def message_handler(msg: types.Message):
    user_id = msg.from_user.id
    
    # Check block status first
    if user_manager.is_blocked(user_id):
        await msg.answer(get_text(user_id, "blocked_msg"))
        return

    user_lang = user_languages.get(user_id, "uz")

    # Til tanlanmagan bo'lsa, til tanlashni ko'rsatish
    if user_id not in user_languages:
        if not await check_subscription(user_id):
            await msg.answer(
                f"{get_text(user_id, 'subscribe_msg')}\n" + "\n".join([normalize_channel(ch) for ch in CHANNELS]),
                reply_markup=subscription_keyboard(user_id)
            )
            return
        await msg.answer(
            get_text(user_id, "select_language"),
            reply_markup=language_select_keyboard()
        )
        return

    # Obuna tekshirish
    if not await check_subscription(user_id):
        await msg.answer(
            f"{get_text(user_id, 'subscribe_msg')}\n" + "\n".join([normalize_channel(ch) for ch in CHANNELS]),
            reply_markup=subscription_keyboard(user_id)
        )
        return

    # Limitni tekshirish (faqat oddiy xabarlar uchun, commands bundan oldin o'tgan bo'lishi kerak edi,
    # lekin bu handler @dp.message() bo'lib hamma narsani ushlaydi.
    # Commands alohida handlerlarda bo'lishi kerak yoki bu yerda tekshirilishi kerak.
    # Biz commandlarni tepadagi handlerlarga o'tkazdik (masalan /start, /image).
    # Bu handler faqat text, voice, photo (boshqasi handlesiz)
    
    if not user_manager.check_limit(user_id):
        # Limit tugagan
        kb = InlineKeyboardBuilder()
        kb.button(text=get_text(user_id, "buy_premium"), callback_data="menu_premium")
        await msg.answer(get_text(user_id, "limit_reached"), reply_markup=kb.as_markup())
        return

    # Userning ishlatishini oshiramiz (so'rov qayta ishlangandan keyin oshirish to'g'riroq bo'lardi,
    # lekin oldindan oshirish spamni oldini olishga yordam beradi)
    user_manager.increment_usage(user_id)

    # Rol tanlandi deb tekshirish kerak emas endi
    
    # Oddiy xabar handlers


    # Oddiy xabar handler
    # role = user_roles.get(user_id, DEFAULT_ROLE) # Removed

    # Agar foydalanuvchi til tanlamagan bo'lsa, avtomatik aniqlash
    user_lang = user_languages.get(user_id)
    if not user_lang:
        user_lang = detect_language(msg.text)
        user_languages[user_id] = user_lang

    # Agar tasvir yaratish so'ralgan bo'lsa
    if is_image_request(msg.text, user_lang):
        # Matndan tasvir tavsifini ajratish
        image_prompt = msg.text
        # Tasvir yaratish so'zlarini olib tashlash
        image_keywords = {
            "uz": ["rasm yarat", "tasvir yarat", "surat yarat", "rasm chiz", "tasvir chiz", "rasm", "tasvir", "surat"],
            "en": ["create image", "generate image", "make image", "draw picture", "create picture", "image", "picture", "draw"],
            "ru": ["создать изображение", "нарисовать", "создать картинку", "нарисовать картинку", "изображение", "картинка", "рисунок"]
        }
        keywords = image_keywords.get(user_lang, image_keywords["uz"])
        for keyword in keywords:
            image_prompt = image_prompt.replace(keyword, "").strip()

        if not image_prompt:
            image_prompt = msg.text  # Agar hech narsa qolmasa, butun matnni ishlatish

        firstMessage = await bot.send_message(msg.chat.id, get_text(user_id, "thinking"))
        try:
            image = await text_to_image(image_prompt)
            await firstMessage.delete()
            await bot.send_photo(msg.chat.id, image, caption=None)
            append_history(
                user_id,
                {
                    "ts": datetime.utcnow().isoformat(),
                    "type": "image",
                    "prompt": image_prompt,
                    "response": image,
                    "role": "Assistant",
                },
            )
        except Exception as e:
            await firstMessage.delete()
            await bot.send_message(msg.chat.id, f"Xatolik: {str(e)}")
        return

    # Oddiy matn javobi
    firstMessage = await bot.send_message(msg.chat.id, get_text(user_id, "thinking"))
    response = chatgpt_text(user_id, msg.text, user_lang)
    await firstMessage.delete()
    # Javobni yuborish
    await bot.send_message(msg.chat.id, response)

    # Tarixga saqlash

    append_history(
        user_id,
        {
            "ts": datetime.utcnow().isoformat(),
            "type": "text",
            "prompt": msg.text,
            "response": response,
            "role": "Assistant",
        },
    )


@dp.message(F.text.regexp(r"^/start"))
async def start(message: types.Message):
    user_id = message.from_user.id
    
    # Check for referral
    args = message.text.split()
    if len(args) > 1 and args[1].isdigit():
        referrer_id = int(args[1])
        if referrer_id != user_id and user_manager.is_new_user(user_id):
            if user_manager.add_referral(user_id, referrer_id):
                try:
                    await bot.send_message(referrer_id, get_text(referrer_id, "referral_new"))
                except Exception:
                    pass # Bot might be blocked by referrer

    # /start yozilganda foydalanuvchi tilini o'chirish (qayta ishga tushirish)
    if user_id in user_languages:
        del user_languages[user_id]
        
    # Check block
    if user_manager.is_blocked(user_id):
        await message.answer(get_text(user_id, "blocked_msg"))
        return

    # Check if invited by someone
    ref_info = user_manager.get_referrer_info(user_id)
    if ref_info:
        # Just show a small notice
        # Note: We need referrer_id from ref_info, but ref_info is a dict of the referrer user.
        # Wait, get_referrer_info returns the user dict of the referrer.
        # I actually just want the referrer ID to show in message.
        # But users.py Logic:
        # referrer_id = self.users[uid].get("referred_by")
        # I can get it directly from user object if I want, but get_referrer_info abstracts it.
        # Let's check users.py again. 
        # get_referrer_info returns *dict*. I can't easily get ID back from dict unless I stored ID in dict or iterate.
        # Actually I stored "referred_by" in current user.
        curr_user = user_manager.get_user(user_id)
        r_id = curr_user.get("referred_by")
        if r_id:
             await message.answer(get_text(user_id, "invited_by").format(referrer_id=r_id))

    # Obuna tekshirish
    if not await check_subscription(user_id):
        await message.answer(
            f"{get_text(user_id, 'welcome')}\n\n"
            f"{get_text(user_id, 'subscribe_msg')}\n"
            f"{chr(10).join(CHANNELS)}\n\n"
            f"{get_text(user_id, 'subscribe_after')}",
            reply_markup=subscription_keyboard(user_id)
        )
        return

    # /start yozilganda: Agar til tanlangan bo'lsa, Bosh menyuga o'tish
    # Aks holda, til tanlashni so'rash
    if user_id in user_languages:
        await message.answer(
            f"{get_text(user_id, 'welcome')}\n\n{get_text(user_id, 'bot_features')}",
            reply_markup=main_menu_keyboard(user_id)
        )
    else:
        await message.answer(
            get_text(user_id, "select_language"),
            reply_markup=language_select_keyboard()
        )



@dp.message(F.text.regexp(r"^/restart"))
async def restart(message: types.Message):
    """Botni qayta ishga tushirish - joriy suhbatni tozalash, lekin premium va tarixni saqlash"""
    user_id = message.from_user.id
    
    # Check block
    if user_manager.is_blocked(user_id):
        await message.answer(get_text(user_id, "blocked_msg"))
        return
    
    # Faqat til sozlamalarini o'chirish (yangi foydalanuvchidek boshlanadi)
    # Premium va tarix saqlanib qoladi
    if user_id in user_languages:
        del user_languages[user_id]
    
    # Restart muvaffaqiyatli xabarini ko'rsatish
    await message.answer(get_text(user_id, "restart_success"))
    
    # Obuna tekshirish
    if not await check_subscription(user_id):
        await message.answer(
            f"{get_text(user_id, 'welcome')}\n\n"
            f"{get_text(user_id, 'subscribe_msg')}\n"
            f"{chr(10).join(CHANNELS)}\n\n"
            f"{get_text(user_id, 'subscribe_after')}",
            reply_markup=subscription_keyboard(user_id)
        )
        return
    
    # Asosiy menyuni ko'rsatish
    await message.answer(
        f"{get_text(user_id, 'welcome')}\n\n{get_text(user_id, 'bot_features')}",
        reply_markup=main_menu_keyboard(user_id)
    )



@dp.message(F.text.regexp(r"^/help"))
async def help_command(message: types.Message):
    """Yordam buyrug'i"""
    user_id = message.from_user.id
    await message.answer(
        get_text(user_id, "help_command"),
        parse_mode="Markdown"
    )
@dp.message(F.text.regexp(r"^/chatgpt"))
async def group_chatgpt_handler(message: types.Message):
    """Guruhda /chatgpt komandasi"""
    # Faqat guruhlarda ishlaydi
    if message.chat.type not in ["group", "supergroup"]:
        return

    user_id = message.from_user.id
    # Obuna tekshirish (guruhda majburiy emas, lekin tekshirish mumkin)

    # Savolni olish
    parts = (message.text or "").split(" ", 1)
    prompt = parts[1] if len(parts) > 1 else ""
    if not prompt:
        await message.reply("Savol yozing: /chatgpt Savolingiz")
        return

    # Limit tekshirish
    if not user_manager.check_limit(user_id):
        await message.reply(get_text(user_id, "limit_reached"))
        return
    user_manager.increment_usage(user_id)

    # Til aniqlash
    user_lang = user_languages.get(user_id)
    if not user_lang:
        user_lang = detect_language(prompt)
        user_languages[user_id] = user_lang

    # Javob berish
    firstMessage = await message.reply(get_text(user_id, "thinking"))
    try:
        response = chatgpt_text(user_id, prompt, user_lang)
        await firstMessage.delete()
        await message.reply(response)

        # Tarixga saqlash
        append_history(
            user_id,
            {
                "ts": datetime.utcnow().isoformat(),
                "type": "text",
                "prompt": prompt,
                "response": response,
                "role": "Assistant",
            },
        )
    except Exception as e:
        await firstMessage.delete()
        await message.reply(f"Xatolik: {str(e)}")

@dp.message(F.text.regexp(r"^/image"))
async def imageHandler(message: types.Message):
    user_id = message.from_user.id
    
    if user_manager.is_blocked(user_id):
        await message.answer(get_text(user_id, "blocked_msg"))
        return

    if not await check_subscription(user_id):
        await message.answer(
            f"{get_text(user_id, 'subscribe_msg')}\n" + "\n".join([normalize_channel(ch) for ch in CHANNELS]),
            reply_markup=subscription_keyboard(user_id)
        )
        return

    # Limit tekshirish
    if not user_manager.check_limit(user_id):
        kb = InlineKeyboardBuilder()
        kb.button(text=get_text(user_id, "buy_premium"), callback_data="menu_premium")
        await message.answer(get_text(user_id, "limit_reached"), reply_markup=kb.as_markup())
        return
    user_manager.increment_usage(user_id)

    parts = (message.text or "").split(" ", 1)
    prompt = parts[1] if len(parts) > 1 else ""
    if not prompt:
        await message.answer(get_text(user_id, "image_help"))
        return
    firstMessage = await bot.send_message(message.chat.id, get_text(user_id, "thinking"))
    try:
        image = await text_to_image(prompt)
        await firstMessage.delete()
        await bot.send_photo(message.chat.id, image, caption=None)
        append_history(
            message.from_user.id,
            {
                "ts": datetime.utcnow().isoformat(),
                "type": "image",
                "prompt": prompt,
                "response": image,
                "role": "Assistant",
            },
        )
    except Exception as e:
        await firstMessage.delete()
        await bot.send_message(message.chat.id, f"Xatolik: {str(e)}")


@dp.message(F.photo)
async def photoHandler(message: types.Message):
    """Rasm yuborilganda anime yoki multserial uslubida qayta ishlash"""
    user_id = message.from_user.id
    
    if user_manager.is_blocked(user_id):
        await message.answer(get_text(user_id, "blocked_msg"))
        return

    if not await check_subscription(user_id):
        await message.answer(
            f"{get_text(user_id, 'subscribe_msg')}\n" + "\n".join([normalize_channel(ch) for ch in CHANNELS]),
            reply_markup=subscription_keyboard(user_id)
        )
        return

    # Limit tekshirish
    if not user_manager.check_limit(user_id):
        kb = InlineKeyboardBuilder()
        kb.button(text=get_text(user_id, "buy_premium"), callback_data="menu_premium")
        await message.answer(get_text(user_id, "limit_reached"), reply_markup=kb.as_markup())
        return
    user_manager.increment_usage(user_id)

    # Rasm caption tekshirish — foydalanuvchi ko'rsatmasi
    caption = (message.caption or "").strip()
    if not caption:
        await message.reply("Rasm ustida nima qilish kerakligini yozing (masalan: anime uslubida, multserial qahramoni qilib ber).")
        return

    os.makedirs("images", exist_ok=True)

    # Eng katta rasmni olish
    photo = message.photo[-1]
    file_id = photo.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    save_path = f"images/{file_id}.jpg"
    await bot.download_file(file_path, save_path)

    firstMessage = await bot.send_message(message.chat.id, get_text(user_id, "thinking"))
    try:
        # Agar aniq anime/multserial so'zlari bo'lsa, shunga mos; bo'lmasa ko'rsatmani to'g'ridan-to'g'ri qo'llaymiz
        caption_lower = caption.lower()
        is_anime = any(word in caption_lower for word in ["anime", "аниме"])
        is_multserial = any(word in caption_lower for word in ["multserial", "мультсериал", "cartoon", "мультфильм", "qahramon", "персонаж"])

        if is_anime or is_multserial:
            style = "anime" if is_anime else "multserial"
            new_image = await image_to_anime(save_path, style)
        else:
            new_image = await transform_image_with_instruction(save_path, caption)

        await firstMessage.delete()
        await bot.send_photo(message.chat.id, new_image, caption=None)

        append_history(
            user_id,
            {
                "ts": datetime.utcnow().isoformat(),
                "type": "image_transform",
                "prompt": caption,
                "response": new_image,
                "role": "Assistant",
            },
        )
    except Exception as e:
        await firstMessage.delete()
        await bot.send_message(message.chat.id, f"Xatolik: {str(e)}")

@dp.message(F.voice)
async def audioHandler(message: types.Message):
    user_id = message.from_user.id
    
    if user_manager.is_blocked(user_id):
        await message.answer(get_text(user_id, "blocked_msg"))
        return

    if not await check_subscription(user_id):
        await message.answer(
            f"{get_text(user_id, 'subscribe_msg')}\n" + "\n".join([normalize_channel(ch) for ch in CHANNELS]),
            reply_markup=subscription_keyboard(user_id)
        )
        return

    # Limit tekshirish
    if not user_manager.check_limit(user_id):
        kb = InlineKeyboardBuilder()
        kb.button(text=get_text(user_id, "buy_premium"), callback_data="menu_premium")
        await message.answer(get_text(user_id, "limit_reached"), reply_markup=kb.as_markup())
        return
    user_manager.increment_usage(user_id)

    os.makedirs("voices", exist_ok=True)
    voice = message.voice
    file_id = voice.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    save_path = f"voices/{file_id}.ogg"
    await bot.download_file(file_path, save_path)

    prompt = speech_to_text(save_path)
    
    # Agar foydalanuvchi til tanlamagan bo'lsa, avtomatik aniqlash
    user_lang = user_languages.get(user_id)
    if not user_lang:
        user_lang = detect_language(prompt)
        user_languages[user_id] = user_lang

    firstMessage = await bot.send_message(message.chat.id, get_text(user_id, "thinking"))
    response = chatgpt_text(user_id, prompt, user_lang)
    await firstMessage.delete()
    await bot.send_message(message.chat.id, response)

    append_history(
        message.from_user.id,
        {
            "ts": datetime.utcnow().isoformat(),
            "type": "voice",
            "prompt": prompt,
            "response": response,
            "role": "Assistant",
        },
    )


@dp.callback_query(F.data.startswith("buy_"))
async def buy_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    plan = callback.data.split("_", 1)[1] # buy_pro -> pro
    
    # check plan validity
    if plan not in PRICES:
        await callback.answer("Plan not found", show_alert=True)
        return

    price = PRICES[plan]
    # Use LabeledPrice
    from aiogram.types import LabeledPrice
    prices = [LabeledPrice(label=f"{plan.replace('_', ' ').title()} Plan", amount=price)] # XTR uses amount directly (1 star = 1 amount? No, amount is usually smallest unit. But for Stars, amount is number of stars)
    # Correct: For XTR, amount is number of stars. 1 star = 1 amount.
    
    await bot.send_invoice(
        chat_id=callback.message.chat.id,
        title=f"Premium {plan.title()}",
        description=f"Purchase {plan.replace('_', ' ').title()} subscription",
        payload=f"sub_{user_id}_{plan}",
        provider_token="", # Empty for Stars
        currency="XTR",
        prices=prices,
        start_parameter=f"buy_{plan}"
    )
    await callback.answer()

@dp.pre_checkout_query()
async def pre_checkout_query(checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(checkout_query.id, ok=True)

@dp.message(F.successful_payment)
async def successful_payment(message: types.Message):
    user_id = message.from_user.id
    payment_info = message.successful_payment
    payload = payment_info.invoice_payload # sub_123_pro
    
    if payload.startswith("sub_"):
        parts = payload.split("_")
        if len(parts) >= 3:
            plan = "_".join(parts[2:])
            user_manager.set_plan(user_id, plan)
            
            # Send notification
            await message.answer(get_text(user_id, "premium_success"))
            
            # Also notify admin (requested: "stars @shoxa_devv akkuntiga kelsin" - stars go to bot owner automatically if setup correctly, 
            # effectively to the bot's balance. I can't force redirect stars to a user via code, 
            # they accumulate on the bot. The user can withdraw them from Fragment/BotFather).
            
            # Show updated menu
            await message.answer(
                f"{get_text(user_id, 'welcome')}\n\n{get_text(user_id, 'bot_features')}",
                reply_markup=main_menu_keyboard(user_id)
            )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())



