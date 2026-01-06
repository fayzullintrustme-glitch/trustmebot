import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)


BOT_TOKEN = os.getenv("BOT_TOKEN")  # Бот возьмёт токен из настроек хостинга
ADMIN_ID = int(os.getenv("869137283"))  # На случай, если не указан

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не указан в переменных окружения!")

import os
# Состояния разговора
NAME, PHONE, POSITION, COMPANY = range(4)

# Тексты объяснения сервиса
DESCRIPTIONS = {
    'ru': (
        "🔏 *TrustMe.uz* — это удобный сервис для онлайн-подписи контрактов прямо с телефона.\n\n"
        "Всё просто: выбираете шаблон, отправляете ссылку клиенту, он подписывает через SMS, WhatsApp или Face ID за пару минут.\n\n"
        "Как помогает бизнесу:\n"
        "• Экономит время — никаких встреч и курьеров\n"
        "• Увеличивает продажи — сделки закрываются здесь и сейчас\n"
        "• Автоматизирует процессы — интеграция с CRM и 1C\n"
        "• Безопасно и легально — сертифицировано в Узбекистане\n\n"
        "Тарифы от 250 000 сум в месяц (50 подписей). Более 3200 бизнесов уже используют!\n"
        "Хотите попробовать бесплатно?"
    ),
    'uz': (
        "🔏 *TrustMe.uz* — shartnomalarni telefoningizda onlayn imzolash uchun qulay xizmat.\n\n"
        "Oddiy: namuna tanlang, havola yuboring, mijoz SMS, WhatsApp yoki Face ID orqali bir necha daqiqada imzolaydi.\n\n"
        "Biznesga qanday yordam beradi:\n"
        "• Vaqt va resurslarni tejaydi\n"
        "• Savdoni oshiradi — tez shartnoma tuzish\n"
        "• Jarayonlarni avtomatlashtiradi — CRM bilan integratsiya\n"
        "• Xavfsiz va qonuniy\n\n"
        "Tariflar 250 000 so‘mdan (50 ta imzo). 3200+ biznes ishlatmoqda!\n"
        "Bepul sinab ko‘rmoqchimisiz?"
    ),
    'en': (
        "🔏 *TrustMe.uz* — convenient service for online contract signing right from your phone.\n\n"
        "Simple: choose a template, send a link, client signs via SMS, WhatsApp or Face ID in minutes.\n\n"
        "How it helps business:\n"
        "• Saves time — no meetings or couriers\n"
        "• Increases sales — close deals instantly\n"
        "• Automates processes — CRM integration\n"
        "• Secure and legal in Uzbekistan\n\n"
        "Plans from 250,000 UZS/month (50 signatures). Trusted by 3200+ businesses!"
    )
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang_code = user.language_code if user.language_code in ['ru', 'uz', 'en'] else 'ru'
    context.user_data['lang'] = lang_code

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🇷🇺 Русский", callback_data='lang_ru')],
        [InlineKeyboardButton("🇺🇿 O‘zbekcha", callback_data='lang_uz')],
        [InlineKeyboardButton("🇬🇧 English", callback_data='lang_en')],
    ])

    await update.message.reply_text(
        "Привет! Я бот TrustMe.uz 👋\nВыберите язык / Tilni tanlang / Choose language:",
        reply_markup=keyboard
    )
    return ConversationHandler.END

async def choose_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = query.data.split('_')[1]
    context.user_data['lang'] = lang

    desc = DESCRIPTIONS[lang]
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "Оставить заявку" if lang == 'ru' else "Ariza qoldirish" if lang == 'uz' else "Leave a request",
            callback_data='lead'
        )]
    ])

    await query.edit_message_text(desc, parse_mode='Markdown', reply_markup=keyboard)

async def start_lead(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get('lang', 'ru')

    texts = {
        'ru': "Отлично! Давайте оставим заявку. Как вас зовут?",
        'uz': "Ajoyib! Ariza qoldiramiz. Ismingiz nima?",
        'en': "Great! Let's leave a request. What's your name?"
    }
    await query.edit_message_text(texts[lang])
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text.strip()
    lang = context.user_data.get('lang', 'ru')

    texts = {
        'ru': "Спасибо! Теперь номер телефона (например, +998901234567):",
        'uz': "Rahmat! Endi telefon raqamingiz:",
        'en': "Thanks! Now your phone number:"
    }
    await update.message.reply_text(texts[lang])
    return PHONE

# Убрана вся валидация — принимаем любой текст
async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text.strip()
    lang = context.user_data.get('lang', 'ru')

    texts = {
        'ru': "Отлично! Ваша должность в компании?",
        'uz': "Zo‘r! Kompaniyadagi lavozimingiz?",
        'en': "Great! Your position in the company?"
    }
    await update.message.reply_text(texts[lang])
    return POSITION

async def get_position(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['position'] = update.message.text.strip()
    lang = context.user_data.get('lang', 'ru')

    texts = {
        'ru': "И последнее — название вашей компании?",
        'uz': "Va oxirgisi — kompaniya nomingiz?",
        'en': "And finally — your company name?"
    }
    await update.message.reply_text(texts[lang])
    return COMPANY

async def get_company(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['company'] = update.message.text.strip()
    lang = context.user_data.get('lang', 'ru')
    user = update.effective_user

    # Сообщение для админа
    admin_message = (
        f"🆕 Новая заявка с TrustMe.uz бота!\n\n"
        f"Имя: {context.user_data['name']}\n"
        f"Телефон: {context.user_data['phone']}\n"
        f"Должность: {context.user_data['position']}\n"
        f"Компания: {context.user_data['company']}\n\n"
        f"Пользователь: @{user.username if user.username else 'нет'} (ID: {user.id})"
    )

    # Отправляем вам в Telegram
    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_message)
    except Exception as e:
        logging.error(f"Ошибка отправки админу: {e}")

    # Ответ пользователю
    thanks_texts = {
        'ru': "Спасибо! Ваша заявка принята. Скоро свяжемся с вами 😊",
        'uz': "Rahmat! Arizangiz qabul qilindi. Tez orada bog‘lanamiz 😊",
        'en': "Thank you! Your request is received. We'll contact you soon 😊"
    }
    await update.message.reply_text(thanks_texts[lang])
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get('lang', 'ru')
    cancel_texts = {
        'ru': "Диалог отменён.",
        'uz': "Suhbat bekor qilindi.",
        'en': "Conversation cancelled."
    }
    await update.message.reply_text(cancel_texts[lang])
    return ConversationHandler.END

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            CallbackQueryHandler(choose_language, pattern='^lang_'),
            CallbackQueryHandler(start_lead, pattern='^lead$')
        ],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            POSITION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_position)],
            COMPANY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_company)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)

    print("Бот TrustMe.uz запущен и готов к работе!")
    application.run_polling()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
