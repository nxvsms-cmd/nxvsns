import telebot
import requests
import json

NXV_API_KEY = "nxv_live_mv9kzuzr_gveqtihynsp6dqyu"
NXV_BASE_URL = "https://nxv-sms.vercel.app"
TELEGRAM_BOT_TOKEN = "8862493248:AAHEaG41gaSA2ro13dpoJg7l0DN7fqiIM9k"

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# একাধিক হেডার ফরম্যাট টেস্ট করবো
def get_headers(style="bearer"):
    if style == "bearer":
        return {"Authorization": f"Bearer {NXV_API_KEY}", "Content-Type": "application/json"}
    elif style == "raw":
        return {"Authorization": NXV_API_KEY, "Content-Type": "application/json"}
    elif style == "apikey":
        return {"X-API-Key": NXV_API_KEY, "Content-Type": "application/json"}


@bot.message_handler(commands=['test'])
def test_api(message):
    bot.reply_to(message, "🔍 API টেস্ট শুরু হচ্ছে... একটু অপেক্ষা করুন")
    
    results = []
    
    # ---------- টেস্ট ১: /balance (GET, Bearer) ----------
    results.append("═══ টেস্ট ১: /balance (GET + Bearer) ═══")
    try:
        r = requests.get(f"{NXV_BASE_URL}/balance", headers=get_headers("bearer"), timeout=15)
        results.append(f"Status: {r.status_code}")
        results.append(f"Body: {r.text[:300]}")
    except Exception as e:
        results.append(f"Exception: {e}")
    
    # ---------- টেস্ট ২: /balance (GET, raw key) ----------
    results.append("\n═══ টেস্ট ২: /balance (GET + raw key) ═══")
    try:
        r = requests.get(f"{NXV_BASE_URL}/balance", headers=get_headers("raw"), timeout=15)
        results.append(f"Status: {r.status_code}")
        results.append(f"Body: {r.text[:300]}")
    except Exception as e:
        results.append(f"Exception: {e}")
    
    # ---------- টেস্ট ৩: /balance (GET, X-API-Key) ----------
    results.append("\n═══ টেস্ট ৩: /balance (GET + X-API-Key) ═══")
    try:
        r = requests.get(f"{NXV_BASE_URL}/balance", headers=get_headers("apikey"), timeout=15)
        results.append(f"Status: {r.status_code}")
        results.append(f"Body: {r.text[:300]}")
    except Exception as e:
        results.append(f"Exception: {e}")
    
    # ---------- টেস্ট ৪: /get-number (GET) ----------
    results.append("\n═══ টেস্ট ৪: /get-number (GET) ═══")
    try:
        r = requests.get(f"{NXV_BASE_URL}/get-number", headers=get_headers("bearer"), timeout=15)
        results.append(f"Status: {r.status_code}")
        results.append(f"Body: {r.text[:300]}")
    except Exception as e:
        results.append(f"Exception: {e}")
    
    # ---------- টেস্ট ৫: /get-number (POST, empty JSON) ----------
    results.append("\n═══ টেস্ট ৫: /get-number (POST + {}) ═══")
    try:
        r = requests.post(f"{NXV_BASE_URL}/get-number", headers=get_headers("bearer"), json={}, timeout=15)
        results.append(f"Status: {r.status_code}")
        results.append(f"Body: {r.text[:300]}")
    except Exception as e:
        results.append(f"Exception: {e}")
    
    # ---------- টেস্ট ৬: key as query param ----------
    results.append("\n═══ টেস্ট ৬: /balance?api_key=... ═══")
    try:
        r = requests.get(f"{NXV_BASE_URL}/balance", params={"api_key": NXV_API_KEY}, timeout=15)
        results.append(f"Status: {r.status_code}")
        results.append(f"Body: {r.text[:300]}")
    except Exception as e:
        results.append(f"Exception: {e}")
    
    # সব ফলাফল একসাথে পাঠান (Telegram 4096 char limit)
    full_text = "\n".join(results)
    for i in range(0, len(full_text), 4000):
        bot.send_message(message.chat.id, f"```\n{full_text[i:i+4000]}\n```", parse_mode="Markdown")


if __name__ == "__main__":
    bot.infinity_polling()
