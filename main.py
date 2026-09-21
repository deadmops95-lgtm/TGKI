import os
import random
from google import genai
import telebot

# --- НАСТРОЙКИ ---
TELEGRAM_BOT_TOKEN = "8627701569:AAF0TnYVULYXcPRKEqYg2xoe676Bwfiwg9s"
CHANNEL_ID = "-1004499803511"

# Ваш ключ доступа
API_KEY = "AQ.Ab8RN6Lkv85q7CQ38jakUL8TrGtcnCOEk0NlkUHn4uWWPJNF-Q"

# Инициализация клиентов
client = genai.Client(api_key=API_KEY)
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Рубрики вашей концепции
RUBRICS = [
    ("🟣 ФАКТ", "Малоизвестный, но подтвержденный факт из канона аниме."),
    ("🔵 СЕКРЕТ", "Скрытая деталь или пасхалка, которую большинство зрителей пропустило."),
    ("🟠 ПЕРСОНАЖ", "Глубокий разбор мотивации или эволюции персонажа."),
    ("🔴 ЧТО ЕСЛИ?", "Фанатская гипотеза или альтернативный сценарий (обязательно указать, что это теория!).")
]

@bot.message_handler(commands=['post'])
def anime_factory_pipeline(message):
    try:
        user_input = message.text.replace('/post', '').strip()
        bot.reply_to(message, "⚙️ **Anime Factory запущен на Bothost:** Researcher ищет тему, Creator пишет текст, Editor проверяет...")

        rubric_name, rubric_desc = random.choice(RUBRICS)
        
        # 1. Этап Researcher: выбор темы (если не задана вручную)
        if not user_input:
            topic_prompt = f"Придумай крутую, интересную тему для аниме из популярных сериалов (Naruto, One Piece, Bleach, Jujutsu Kaisen и др.) для рубрики {rubric_name}."
            topic_res = client.models.generate_content(model="gemini-2.5-flash", contents=topic_prompt)
            anime_topic = topic_res.text.strip()
        else:
            anime_topic = user_input

        # 2. Этап Creator & Editor: генерация поста по жестким правилам
        system_prompt = f"""
        Ты — система из двух ИИ-агентов для аниме-медиа (Creator и Editor).
        
        Твоя задача — создать пост для Telegram-канала по строгим правилам.
        Рубрика: {rubric_name} ({rubric_desc})
        Тема: {anime_topic}

        ПРАВИЛА (Editor следит за их выполнением):
        1. Короткие предложения, сильный первый абзац (HOOK), минимум воды, разговорный русский язык.
        2. Структура: HOOK -> Основная информация -> Неожиданная деталь -> Вывод -> CTA (призыв к действию, не повторяющийся).
        3. Если есть сюжетные повороты, обязательно в самом начале поставь плашку: ⚠️ СПОЙЛЕРЫ.
        4. Если это рубрика 'ЧТО ЕСЛИ?', явно обозначь, что это фанатская теория.
        5. Не используй длинные цитаты, пиши своими словами. Динамично и понятно.
        
        Выдай на выходе готовый текст поста для Telegram.
        """

        generation_response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=system_prompt,
        )
        
        final_post = f"{rubric_name}\n\n{generation_response.text}"
        
        # 3. Публикация в канал
        bot.send_message(CHANNEL_ID, final_post)
        bot.send_message(message.chat.id, f"✅ **Материал успешно опубликован в канал!**\n\n📌 **Тема:** {anime_topic}\n📌 **Рубрика:** {rubric_name}")
        
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка в конвейере: {e}")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        prompt = f"Ты — главный редактор аниме-медиа. Ответь пользователю на сообщение: {message.text}"
        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {e}")

print("Anime Factory 24/7 успешно запущена!")
bot.infinity_polling()
