"""
Simple i18n layer: translations + get_text(user_id, key).

Legacy behavior:
- language is cached in-memory (`bot.state_store.user_languages`)
- if not in cache, tries to load from `user_manager`
- default language: uz
"""

from __future__ import annotations

from bot.state_store import user_languages
from data.users import user_manager


# NOTE: kept as-is from legacy `main.py`
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
        "image_prompt_request": '🎨 Rasm uchun tavsif yozing:\n\nMasalan: "Kosmosdagi mushuk"',
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
        "payment_warning": "⚠️ According to Telegram rules, you can only pay via Stars. If you cannot pay via Stars, contact admin: @shoxa_devv",
        "blocked_msg": "⛔ You have been blocked by admin.",
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
        "image_prompt_request": '🎨 Enter image description:\n\nExample: "Cat in space"',
        "image_size_select": "📏 Select image size:",
        "size_1_1": "1:1 (Square)",
        "size_3_4": "3:4 (Portrait)",
        "size_4_3": "4:3 (Album)",
        "size_16_9": "16:9 (Wide)",
        "image_limit_reached": "⚠️ Image generation limit reached!\nBuy Premium to increase limits.",
        "video_unavailable": "⚠️ Video generation service is temporarily unavailable.",
        "admin_panel": "Admin Panel 🎁",
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
        "payment_warning": "⚠️ Согласно правилам Telegram, оплата возможна только через Stars. Если вы не можете оплатить через Stars, свяжитесь с админом: @shoxa_devv",
        "blocked_msg": "⛔ Вы заблокированы администратором.",
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
        "image_prompt_request": '🎨 Опишите изображение:\n\nНапример: "Кот в космосе"',
        "image_size_select": "📏 Выберите размер:",
        "size_1_1": "1:1 (Квадрат)",
        "size_3_4": "3:4 (Портрет)",
        "size_4_3": "4:3 (Альбом)",
        "size_16_9": "16:9 (Широкий)",
        "image_limit_reached": "⚠️ Лимит на создание изображений исчерпан!\nКупите Premium для увеличения.",
        "video_unavailable": "⚠️ Сервис создания видео временно недоступен.",
        "admin_panel": "Admin Panel 🎁",
    },
}


def get_text(user_id: int, key: str) -> str:
    """Return translation by user's language (with cache + persisted language)."""
    if user_id in user_languages:
        lang = user_languages[user_id]
    else:
        lang = user_manager.get_language(user_id)
        if lang:
            user_languages[user_id] = lang
        else:
            lang = "uz"
    return TRANSLATIONS.get(lang, TRANSLATIONS["uz"]).get(key, key)

