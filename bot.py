import sqlite3
import time
import threading
from datetime import datetime
import telebot
from google.oauth2 import service_account
from googleapiclient.discovery import build

# ===========================
# TELEGRAM BOT
# ===========================
BOT_TOKEN = "8452637493:AAFxwvTvfAIfxd44cJzapWPkeCby9iRUtOo"
bot = telebot.TeleBot(BOT_TOKEN)

# ===========================
# GOOGLE CALENDAR
# ===========================
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

GOOGLE_CREDENTIALS = {
  "type": "service_account",
  "project_id": "logical-factor-456806-u1",
  "private_key_id": "e85741d2d9427539c71889328c7ef073d0206496",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDQ4Lpu+I39n2qu\nnRwEW1RBrAPx2yp407vXNJ5VOx4bb8CFZvYcY8K7DbG6oYZZvPJraWm1rcYis2sQ\nPDc0zcgwAP+PEH0fy+waZZ2mgHqxhx75KRO3WgZ87yzgfoGr6seHvpvaJguCtTUa\n7fMrJdPwhOyxpWn8YkjqHAjZOU1boEWi75hUBTiqY/4ZAUNJuvwhLCL2R2XK1tgQ\nMtL5DidI9UE3AJ81ccPfDLxEnpCNl5qvVfMZciBragPw9Eh2AO5fAnM+BtyLcMXJ\nZxrYaM8XJyiBzyk9eMYXr8kme35ll5L4CrO6h4W7gPLFxxjxkhBM0x2QB68wWV6Q\nroGmtVKzAgMBAAECggEABLZ3/mD6ndT8TIxG7DeTTcKvzsPUetLBfjg1tP6XI09W\nLKxcs9nxtClkRS23y6EzvFtYgzzfJ5FHbR+urzD6v0/byZfkUCoDCGVv39MuRtXM\nS8WIKFmOTpX8O+R0Jd4vj6SBUl62tnBC489SmTqf7uFQ5daG7vwuC6TY85hot78k\n4t9rRYeb8dkN5F0eRcmNcGJfUDFxZJTzo7d5omyu3BX64Ign4EOUZtxJ2h8B2ciX\nsyT5M4NM8EHPUr+8rVctfh4HWNf/wPzQj49WmrgC95lBzT1IDB/hCrQH8ZfFmbYB\ntY0b9GM2D+qv6fIxbSlMq2t81VbivYr2Rbnh7FczwQKBgQDtQ4AWEccs1Pj5tf+s\n51w3Il3E3jZW4l/V8O/bUcNEisz0LBzIqC7iJUDJ0jzwnzKGugDE/+EX3Nnnyz/Q\n68we8KzDc7PXR0UsbwYRGMHSPFOjE1izoSE69UFDrwNI3rdPTNuj9iY+g+fyASaz\nkBcdTKD6dM525n2M7JQ4EMdQaQKBgQDhX2H60rXTt+23gLmSMBPhg81EBtqJXRgY\nZdIVkH/8sccRDSKOOgXTON6FiRXqH9U9Uu/IN0ICK4TfG/ELyFO2vOcXoc9Wz/XG\nw22XIJ0AJ20EbBUNuIRa52HUIeCwE4ZWcXKq3MMw+hCbUf8mAw6Ziqv537c+cmwg\nAcvc7/4muwKBgQDKKjPfmjJebvHexEcg6tpWWEAR2U3v5l/Gic+2zwpVQve0Lkow\nZ63bH+b+kNdAKEYDKkYxld4UWSiLK1IrEGATFPwAZnwcuSul2swOkUvFeYXCdF+m\nX2tTM1ry8xMXaj5DobedE8YuinJ+cKCra+FmI78e6ZxrD6Z3B7abtyA90QKBgHvN\nasRfNZTtJ7+zDb2ZfYJXZc3luezVX+QfIs3HyBbnDcR3I7FffE2wosRWLtyiyf/a\n7G9es3r/rwjkj4B6dkoe8Q9RStWUfZ3HQw9O0hAAmGliehpEbyiEjH/8cDIpN5WK\n0oO7q9netHquC2w1J7L+s0QbOc0rC+x1MCjZCRL7AoGBAKhlAeg4aiVLX+m8FbeQ\ndh+5M3KZE9Vh3vJyfZPex6etiwkNORCIlNckKBw8ZFjJTQ7QbDuG/ibJsW9Mrww5\nK2pfseLy6U0i7r0wg4v0D6uzssiiXGoxXRqhlBlrGKF4NV3mSdgvYSOdEKD4a83r\n4x2tgdWOpwlItRbKFOWMBsi7\n-----END PRIVATE KEY-----\n",
  "client_email": "magnit-hr-bot@logical-factor-456806-u1.iam.gserviceaccount.com",
  "client_id": "108394275385686439180",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/magnit-hr-bot@logical-factor-456806-u1.iam.gserviceaccount.com"
}

credentials = service_account.Credentials.from_service_account_info(GOOGLE_CREDENTIALS, scopes=SCOPES)
calendar_service = build('calendar', 'v3', credentials=credentials)
CALENDAR_ID = 'primary'

# ===========================
# SQLITE DATABASE
# ===========================
conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    chat_id TEXT PRIMARY KEY,
    username TEXT
)
''')
conn.commit()

# ===========================
# CALENDLY LINK
# ===========================
CALENDLY_LINK = "https://calendly.com/oltybaevmus/magnit_tech"

# ===========================
# /start COMMAND
# ===========================
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    username = message.from_user.username
    cursor.execute('INSERT OR IGNORE INTO users (chat_id, username) VALUES (?, ?)', (chat_id, username))
    conn.commit()
    bot.send_message(chat_id, f"Привет, {username}! Ты зарегистрирован для уведомлений о встречах MAGNIT TECH HR-interview.")
    bot.send_message(chat_id, f"Чтобы записаться на интервью, используй эту ссылку:\n{CALENDLY_LINK}")

# ===========================
# /book COMMAND
# ===========================
@bot.message_handler(commands=['book'])
def book(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, f"Запишись на HR-интервью по этой ссылке:\n{CALENDLY_LINK}")

# ===========================
# ADMIN CHAT_ID
# ===========================
admin_chat_id = 8452637493

# ===========================
# CHECK CALENDAR FUNCTION
# ===========================
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

        if 'Telegram username:' in description:
            username_line = [line for line in description.splitlines() if 'Telegram username:' in line][0]
            telegram_username = username_line.split(':')[-1].strip()
            
            cursor.execute('SELECT chat_id FROM users WHERE username=?', (telegram_username,))
            result = cursor.fetchone()
            if result:
                chat_id = result[0]
                # Напоминание кандидату за 30 минут
                if 0 <= (start_time - datetime.utcnow()).total_seconds() <= 1800:
                    bot.send_message(chat_id, f"Напоминание: ваша встреча '{summary}' начнется через 30 минут.")
                # Напоминание админу за 15 минут
                if 0 <= (start_time - datetime.utcnow()).total_seconds() <= 900:
                    bot.send_message(admin_chat_id, f"Напоминание: встреча с {telegram_username} через 15 минут.")

# ===========================
# LOOP IN SEPARATE THREAD
# ===========================
def calendar_loop():
    while True:
        try:
            check_calendar()
            time.sleep(60)
        except Exception as e:
            print("Ошибка:", e)
            time.sleep(60)

threading.Thread(target=calendar_loop).start()

# ===========================
# START BOT
# ===========================
bot.polling(none_stop=True)
