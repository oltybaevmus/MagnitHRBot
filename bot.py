import os
import sqlite3
import time
from datetime import datetime, timedelta
import telebot
from google.oauth2 import service_account
from googleapiclient.discovery import build
import json

# Telegram bot token из переменной окружения
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

# Google Calendar credentials (JSON как переменная окружения)
GOOGLE_CREDENTIALS = json.loads(os.environ.get('GOOGLE_CREDENTIALS_JSON'))

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
credentials = service_account.Credentials.from_service_account_info(GOOGLE_CREDENTIALS, scopes=SCOPES)
calendar_service = build('calendar', 'v3', credentials=credentials)

# Название календаря (можно поменять на свой)
CALENDAR_ID = 'primary'

# SQLite база для пользователей
conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    chat_id TEXT PRIMARY KEY,
    username TEXT
)
''')
conn.commit()

# /start команда
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    username = message.from_user.username
    cursor.execute('INSERT OR IGNORE INTO users (chat_id, username) VALUES (?, ?)', (chat_id, username))
    conn.commit()
    bot.send_message(chat_id, f"Привет, {username}! Ты зарегистрирован для уведомлений о встречах MAGNIT TECH HR-interview.")

# Admin chat_id
admin_chat_id = 8452637493  # <- сюда вставлен твой Telegram chat_id

# Функция проверки календаря и отправки уведомлений
def check_calendar():
    now = datetime.utcnow().isoformat() + 'Z'
    events_result = calendar_service.events().list(calendarId=CALENDAR_ID,
                                                   timeMin=now,
                                                   maxResults=50,
                                                   singleEvents=True,
                                                   orderBy='startTime').execute()
    events = events_result.get('items', [])

    for event in events:
        start_time_str = event['start'].get('dateTime', event['start'].get('date'))
        start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
        summary = event.get('summary', 'HR Interview')
        description = event.get('description', '')

        # Ищем Telegram username в описании события
        if 'Telegram username:' in description:
            username_line = [line for line in description.splitlines() if 'Telegram username:' in line][0]
            telegram_username = username_line.split(':')[-1].strip()
            
            cursor.execute('SELECT chat_id FROM users WHERE username=?', (telegram_username,))
            result = cursor.fetchone()
            if result:
                chat_id = result[0]
                # Отправка уведомления кандидату за 30 минут до события
                if 0 <= (start_time - datetime.utcnow()).total_seconds() <= 1800:
                    bot.send_message(chat_id, f"Напоминание: ваша встреча '{summary}' начнется через 30 минут.")
                # Отправка уведомления администратору за 15 минут
                if 0 <= (start_time - datetime.utcnow()).total_seconds() <= 900:
                    bot.send_message(admin_chat_id, f"Напоминание: встреча с {telegram_username} через 15 минут.")

# Главный цикл
while True:
    try:
        check_calendar()
        time.sleep(60)  # Проверка календаря каждую минуту
    except Exception as e:
        print("Ошибка:", e)
        time.sleep(60)

bot.polling(none_stop=True)
