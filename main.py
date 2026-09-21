import random
import telebot
from google import genai
from google.genai import types

# --- НАСТРОЙКИ ---
TELEGRAM_BOT_TOKEN = "8974825461:AAELL0AnAwHEWyuZ4uQ6HU_Irh-ajLFt6wA"
CHANNEL_ID = "-1004499803511"

# Используем ваш токен через стандартный клиент с базовыми настройками
AQ_TOKEN = "AQ.Ab8RN6Lkv85q7CQ38jakUL8TrGtcnCOEk0NlkUHn4uWWPJNF-Q"

# Инициализируем клиент
client = genai.Client(api_key=AQ_TOKEN)
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

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
        bot.reply_to(message, "⚙️ **Anime Factory в работе:** Подключаюсь к модели...")

        rubric_name, rubric_desc = random.choice(RUBRICS)
        
        if not user_input:
            topic_prompt = f"Придумай крутую, интересную тему для аниме из популярных сериалов для рубрики {rubric_name}."
            # Указываем легкую модель и увеличиваем таймаут запроса если поддерживает клиент
            topic_res = client.models.generate_content(model="gemini-2.5-flash", contents=topic_prompt)
            anime_topic = topic_res.text.strip()
        else:
            anime_topic = user_input

        system_prompt = f"""
        Создай короткий и увлекательный пост для Telegram-канала об аниме.
        Рубрика: {rubric_name} ({rubric_desc})
        Тема: {anime_topic}
        Правила: короткие предложения, сильный первый абзац (HOOK), разговорный русский язык, в конце призыв к действию.
        Если есть спойлеры, поставь плашку: ⚠️ СПОЙЛЕРЫ.
        Выдай готовый текст поста для Telegram.
        """

        generation_response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=system_prompt,
        )
        
        final_post = f"{rubric_name}\n\n{generation_response.text}"
        
        bot.send_message(CHANNEL_ID, final_post)
        bot.send_message(message.chat.id, f"✅ **Опубликовано!**\n\n📌 **Тема:** {anime_topic}")
        
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка таймаута или сети: {e}")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        response = client.models.generate_content(model="gemini-2.5-flash", contents=message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {e}")

print("Бот запущен!")
bot.infinity_polling()
