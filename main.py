import random
import telebot
import vertexai
from vertexai.generative_models import GenerativeModel
from google.oauth2 import credentials

# --- НАСТРОЙКИ ---
TELEGRAM_BOT_TOKEN = "8627701569:AAF0TnYVULYXcPRKEqYg2xoe676Bwfiwg9s"
CHANNEL_ID = "-1004499803511"

# Ваш токен Google Cloud / Vertex AI
AQ_TOKEN = "AQ.Ab8RN6Lkv85q7CQ38jakUL8TrGtcnCOEk0NlkUHn4uWWPJNF-Q"
PROJECT_ID = "581192983007"  # ID вашего проекта из консоли Google Cloud
LOCATION = "us-central1"     # Стандартный рабочий регион

# Создаем учетные данные OAuth из вашего токена и инициализируем Vertex AI
creds = credentials.Credentials(token=AQ_TOKEN)
vertexai.init(project=PROJECT_ID, location=LOCATION, credentials=creds)

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Рубрики конвейера
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
        bot.reply_to(message, "⚙️ **Anime Factory запущен через Vertex AI:** Конвейер обрабатывает запрос...")

        rubric_name, rubric_desc = random.choice(RUBRICS)
        
        # Используем модель через Vertex AI SDK
        model = GenerativeModel("gemini-1.5-flash")

        if not user_input:
            topic_prompt = f"Придумай крутую, интересную тему для аниме из популярных сериалов (Naruto, One Piece, Bleach, Jujutsu Kaisen и др.) для рубрики {rubric_name}."
            topic_res = model.generate_content(topic_prompt)
            anime_topic = topic_res.text.strip()
        else:
            anime_topic = user_input

        system_prompt = f"""
        Ты — система из двух ИИ-агентов для аниме-медиа (Creator и Editor).
        
        Твоя задача — создать пост для Telegram-канала по строгим правилам.
        Рубрика: {rubric_name} ({rubric_desc})
        Тема: {anime_topic}

        ПРАВИЛА (Editor следит за их выполнением):
        1. Короткие предложения, сильный первый абзац (HOOK), минимум воды, разговорный русский язык.
        2. Структура: HOOK -> Основная информация -> Неожиданная деталь -> Вывод -> CTA (призыв к действию).
        3. Если есть сюжетные повороты, обязательно в самом начале поставь плашку: ⚠️ СПОЙЛЕРЫ.
        4. Если это рубрика 'ЧТО ЕСЛИ?', явно обозначь, что это фанатская теория.
        5. Не используй длинные цитаты, пиши своими словами. Динамично и понятно.
        
        Выдай на выходе готовый текст поста для Telegram.
        """

        generation_response = model.generate_content(system_prompt)
        final_post = f"{rubric_name}\n\n{generation_response.text}"
        
        bot.send_message(CHANNEL_ID, final_post)
        bot.send_message(message.chat.id, f"✅ **Материал успешно опубликован в канал!**\n\n📌 **Тема:** {anime_topic}\n📌 **Рубрика:** {rubric_name}")
        
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка в конвейере Vertex: {e}")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        model = GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(f"Ты — главный редактор аниме-медиа. Ответь пользователю: {message.text}")
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {e}")

print("Anime Factory 24/7 успешно запущен через Vertex AI!")
bot.infinity_polling()
