import sqlite3
import time
from datetime import datetime
from zoneinfo import ZoneInfo
import telebot
from google.oauth2 import service_account
from googleapiclient.discovery import build
import threading

# ---------------------------
# Настройки (в коде)
# ---------------------------

BOT_TOKEN = "8452637493:AAFxwvTvfAIfxd44cJzapWPkeCby9iRUtOo"

GOOGLE_CREDENTIALS = {
    "type": "service_account",
    "project_id": "logical-factor-456806-u1",
    "private_key_id": "e85741d2d9427539c71889328c7ef073d0206496",
    "private_key": """-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDQ4Lpu+I39n2qu
nRwEW1RBrAPx2yp407vXNJ5VOx4bb8CFZvYcY8K7DbG6oYZZvPJraWm1rcYis2sQ
PDc0zcgwAP+PEH0fy+waZZ2mgHqxhx75KRO3WgZ87yzgfoGr6seHvpvaJguCtTUa
7fMrJdPwhOyxpWn8YkjqHAjZOU1boEWi75hUBTiqY/4ZAUNJuvwhLCL2R2XK1tgQ
MtL5DidI9UE3AJ81ccPfDLxEnpCNl5qvVfMZciBragPw9Eh2AO5fAnM+BtyLcMXJ
ZxrYaM8XJyiBzyk9eMYXr8kme35ll5L4CrO6h4W7gPLFxxjxkhBM0x2QB68wWV6Q
roGmtVKzAgMBAAECggEABLZ3/mD6ndT8TIxG7DeTTcKvzsPUetLBfjg1tP6XI09W
LKxcs9nxtClkRS23y6EzvFtYgzzfJ5FHbR+urzD6v0/byZfkUCoDCGVv39MuRtXM
S8WIKFmOTpX8O+R0Jd4vj6SBUl62tnBC489SmTqf7uFQ5daG7vwuC6TY85hot78k
4t9rRYeb8dkN5F0eRcmNcGJfUDFxZJTzo7d5omyu3BX64Ign4EOUZtxJ2h8B2ciX
syT5M4NM8EHPUr+8rVctfh4HWNf/wPzQj49WmrgC95lBzT1IDB/hCrQH8ZfFmbYB
tY0b9GM2D+qv6fIxbSlMq2t81VbivYr2Rbnh7FczwQKBgQDtQ4AWEccs1Pj5tf+s
51w3Il3E3jZW4l/V8O/bUcNEisz0LBzIqC7iJUDJ0jzwnzKGugDE/+EX3Nnnyz/Q
68we8KzDc7PXR0UsbwYRGMHSPFOjE1izoSE69UFDrwNI3rdPTNuj9iY+g+fyASaz
kBcdTKD6dM525n2M7JQ4EMdQaQKBgQDhX2H60rXTt+23gLmSMBPhg81EBtqJXRgY
ZdIVkH/8sccRDSKOOgXTON6FiRXqH9U9Uu/IN0ICK4TfG/ELyFO2vOcXoc9Wz/XG
w22XIJ0AJ20EbBUNuIRa52HUIeCwE4ZWcXKq3MMw+hCbUf8mAw6Ziqv537c+cmwg
Acvc7/4muwKBgQDKKjPfmjJebvHexEcg6tpWWEAR2U3v5l/Gic+2zwpVQve0Lkow
Z63bH+b+kNdAKEYDKkYxld4UWSiLK1IrEGATFPwAZnwcuSul2swOkUvFeYXCdF+m
X2tTM1ry8xMXaj5DobedE8YuinJ+cKCra+FmI78e6ZxrD6Z3B7abtyA90QKBgHvN
asRfNZTtJ7+zDb2ZfYJXZc3luezVX+QfIs3HyBbnDcR3I7FffE2wosRWLtyiyf/a
7G9es3r/rwjkj4B6dkoe8Q9RStWUfZ3HQw9O0hAAmGliehpEbyiEjH/8cDIpN5WK
0oO7q9netHquC2w1J7L+s0QbOc0rC+x1MCjZCRL7AoGBAKhlAeg4aiVLX+m8FbeQ
dh+5M3KZE9Vh3vJyfZPex6etiwkNORCIlNckKBw8ZFjJTQ7QbDuG/ibJsW9Mrww5
K2pfseLy6U0i7r0wg4v0D6uzssiiXGoxXRqhlBlrGKF4NV3mSdgvYSOdEKD4a83r
4x2tgdWOpwlItRbKFOWMBsi7
-----END PRIVATE KEY-----""",
    "client_email": "magnit-hr-bot@logical-factor-456806-u1.iam.gserviceaccount.com",
    "client_id": "108394275385686439180",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/magnit-hr-bot%40logical-factor-456806-u1.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

bot = telebot.TeleBot(BOT_TOKEN)
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
credentials = service_account.Credentials.from_service_account_info(GOOGLE_CREDENTIALS, scopes=SCOPES)
calendar_service = build("calendar", "v3", credentials=credentials)

CALENDAR_ID = "primary"
ADMIN_CHAT_ID = 8452637493

# ---------------------------
# SQLite база
# ---------------------------
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    chat_id TEXT PRIMARY KEY,
    username TEXT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS sent_confirmations (
    event_id TEXT PRIMARY KEY
)
""")
conn.commit()

# ---------------------------
# /start команда
# ---------------------------
@bot.message_handler(commands=["start"])
def start(message):
    chat_id = message.chat.id
    username = message.from_user.username
    cursor.execute(
        "INSERT OR IGNORE INTO users (chat_id, username) VALUES (?, ?)",
        (chat_id, username),
    )
    conn.commit()
    bot.send_message(chat_id, f"Привет, @{username}! Ты зарегистрирован для уведомлений о встречах MAGNIT TECH HR-interview.")

# ---------------------------
# Проверка календаря и уведомления
# ---------------------------
def check_new_events():
    now = datetime.utcnow().isoformat() + "Z"
    events = calendar_service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=now,
        maxResults=50,
        singleEvents=True,
        orderBy="startTime"
    ).execute().get("items", [])

    for event in events:
        event_id = event["id"]
        cursor.execute("SELECT 1 FROM sent_confirmations WHERE event_id=?", (event_id,))
        if cursor.fetchone():
            continue

        description = event.get("description", "")
        if "Telegram:" not in description:
            continue

        username = description.split("Telegram:")[-1].strip().replace("@", "")
        cursor.execute("SELECT chat_id FROM users WHERE username=?", (username,))
        user = cursor.fetchone()
        if not user:
            continue

        chat_id = user[0]
        start_str = event["start"].get("dateTime")
        if not start_str:
            continue

        start_dt = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
        start_msk = start_dt.astimezone(ZoneInfo("Europe/Moscow"))
        date_str = start_msk.strftime("%d.%m.%Y")
        time_str = start_msk.strftime("%H:%M")

        link = event.get("location") or event.get("hangoutLink") or "ссылка не указана"

        bot.send_message(chat_id, f"@{username} ты забронировал встречу на {date_str} в {time_str} по МСК\nСсылка на встречу: {link}")
        bot.send_message(ADMIN_CHAT_ID, f"Новая встреча с @{username} на {date_str} {time_str} МСК. Ссылка: {link}")

        cursor.execute("INSERT INTO sent_confirmations VALUES (?)", (event_id,))
        conn.commit()

# ---------------------------
# Главный цикл
# ---------------------------
def main_loop():
    while True:
        try:
            check_new_events()
            time.sleep(60)
        except Exception as e:
            print("Ошибка:", e)
            time.sleep(60)

threading.Thread(target=main_loop, daemon=True).start()
bot.polling(none_stop=True)
