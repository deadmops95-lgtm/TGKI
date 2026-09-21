import os
import random
import google.generativeai as genai
import telebot

TELEGRAM_BOT_TOKEN = "8627701569:AAF0TnYVULYXcPRKEqYg2xoe676Bwfiwg9s"
CHANNEL_ID = "-1004499803511"

# Настройка стабильного клиента
API_KEY = "AQ.Ab8RN6Lkv85q7CQ38jakUL8TrGtcnCOEk0NlkUHn4uWWPJNF-Q"
genai.configure(api_key=API_KEY)

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
        bot.reply_to(message, "⚙️ **Anime Factory запущен на Bothost:** Обработка конвейера...")

        rubric_name, rubric_desc = random.choice(RUBRICS)
        model = genai.GenerativeModel('gemini-1.5-flash')

        if not user_input:
            topic_prompt = f"Придумай крутую, интересную тему для аниме из популярных сериалов для рубрики {rubric_name}."
            topic_res = model.generate_content(topic_prompt)
            anime_topic = topic_res.text.strip()
        else:
            anime_topic = user_input

        system_prompt = f"""
        Ты — система из двух ИИ-агентов для аниме-медиа (Creator и Editor).
        Рубрика: {rubric_name} ({rubric_desc})
        Тема: {anime_topic}
        Правила: короткие предложения, сильный первый абзац (HOOK), разговорный русский язык, в конце призыв к действию.
        Если есть спойлеры, поставь плашку: ⚠️ СПОЙЛЕРЫ.
        Выдай готовый текст поста для Telegram.
        """

        generation_response = model.generate_content(system_prompt)
        final_post = f"{rubric_name}\n\n{generation_response.text}"
        
        bot.send_message(CHANNEL_ID, final_post)
        bot.send_message(message.chat.id, f"✅ **Опубликовано!**\n\n📌 **Тема:** {anime_topic}")
        
    except Exception as e:
        bot.reply_to(message, `❌ Ошибка в конвейере: {e}`)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(f"Ответь пользователю: {message.text}")
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {e}")

print("Бот успешно запущен 24/7!")
bot.infinity_polling()
