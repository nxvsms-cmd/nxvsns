import telebot
import requests
import json

# ================= কনফিগারেশন =================
# আপনার নতুন রিসেট করা API Key এখানে বসান (কোডে হার্ডকোড করবেন না, এনভায়রনমেন্ট ভেরিয়েবল ব্যবহার করুন)
NXV_API_KEY = "YOUR_NEW_API_KEY_HERE"
NXV_BASE_URL = "https://nxv-sms.vercel.app"

# আপনার টেলিগ্রাম বটের টোকেন
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

# ==============================================

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# হেডার সেটআপ, নিশ্চিত করুন Authorization ফরম্যাট সঠিক
headers = {
    "Authorization": f"Bearer {NXV_API_KEY}",
    "Content-Type": "application/json"
}

# ১. /start কমান্ড হ্যান্ডলার
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.InlineKeyboardMarkup()
    # "এক নম্বর বাটন" তৈরি করুন
    get_btn = telebot.types.InlineKeyboardButton(
        text="📞 একটি নাম্বার পান", 
        callback_data="action_get_number"
    )
    markup.add(get_btn)
    
    bot.reply_to(
        message, 
        "স্বাগতম NXV SMS বটে!\nনিচের বাটনে ক্লিক করে একটি ভার্চুয়াল নাম্বার পান:", 
        reply_markup=markup
    )

# ২. বাটন ক্লিক ইভেন্ট হ্যান্ডলার (callback)
@bot.callback_query_handler(func=lambda call: call.data == "action_get_number")
def handle_get_number(call):
    # দ্রুত প্রতিক্রিয়া জানান, যাতে বাটন লোডিং অবস্থায় না থাকে
    bot.answer_callback_query(call.id, text="নাম্বার আনা হচ্ছে...")
    
    try:
        # NXV প্যানেলের get-number এন্ডপয়েন্টে কল করুন
        # দ্রষ্টব্য: এখানে অনুমান করা হয়েছে যে প্যানেল GET রিকোয়েস্ট এবং Authorization হেডার সমর্থন করে
        response = requests.get(
            f"{NXV_BASE_URL}/get-number", 
            headers=headers, 
            timeout=15
        )
        
        # যদি প্যানেল POST রিকোয়েস্ট এবং JSON বডি চায়, তাহলে নিচের লাইনটি ব্যবহার করুন
        # response = requests.post(f"{NXV_BASE_URL}/get-number", headers=headers, json={}, timeout=15)

        if response.status_code == 200:
            data = response.json()
            # ধরে নিচ্ছি API রেসপন্সে 'number' এবং 'id' ফিল্ড আছে
            # নিশ্চিত করুন যে response ডেটা ফরম্যাট আপনার প্যানেল ডকুমেন্টেশনের সাথে মেলে
            number = data.get('number', 'অজানা নাম্বার')
            order_id = data.get('id', 'অজানা ID')
            
            result_text = (
                f"✅ **সফলভাবে নাম্বার পাওয়া গেছে!**\n\n"
                f"📱 নাম্বার: `{number}`\n"
                f"🆔 অর্ডার ID: `{order_id}`\n\n"
                f"👉 OTP পেতে `/getotp {order_id}` কমান্ড ব্যবহার করুন"
            )
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=result_text,
                parse_mode="Markdown"
            )
        else:
            # এরর মেসেজ হ্যান্ডলিং
            error_msg = f"নাম্বার পেতে ব্যর্থ, স্ট্যাটাস কোড: {response.status_code}\nসার্ভার প্রতিক্রিয়া: {response.text[:200]}"
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=error_msg
            )
            
    except requests.exceptions.Timeout:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="❌ অনুরোধ সময় শেষ, NXV প্যানেল সার্ভার সাড়া দিচ্ছে না।"
        )
    except Exception as e:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"❌ এরর ঘটেছে: {str(e)}"
        )

# ৩. OTP পাওয়ার সহায়ক কমান্ড (বোনাস ফিচার)
@bot.message_handler(commands=['getotp'])
def get_otp(message):
    try:
        # কমান্ড থেকে অর্ডার ID বের করুন
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "ব্যবহার: `/getotp <অর্ডার_ID>`", parse_mode="Markdown")
            return
        
        order_id = parts[1]
        
        # OTP এন্ডপয়েন্টে কল করুন
        response = requests.get(
            f"{NXV_BASE_URL}/get-otp", 
            headers=headers,
            params={"id": order_id}, # বা json={"id": order_id} আপনার API অনুযায়ী
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            otp = data.get('otp', 'এখনও OTP আসেনি')
            bot.reply_to(message, f"🔐 OTP: `{otp}`", parse_mode="Markdown")
        else:
            bot.reply_to(message, f"OTP পেতে ব্যর্থ: {response.status_code}")
            
    except Exception as e:
        bot.reply_to(message, f"এরর: {str(e)}")

# ৪. ব্যালেন্স চেক কমান্ড
@bot.message_handler(commands=['balance'])
def check_balance(message):
    try:
        response = requests.get(f"{NXV_BASE_URL}/balance", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            balance = data.get('balance', '0')
            bot.reply_to(message, f"💰 বর্তমান ব্যালেন্স: `{balance}`", parse_mode="Markdown")
        else:
            bot.reply_to(message, f"ব্যালেন্স পাওয়া যায়নি: {response.status_code}")
    except Exception as e:
        bot.reply_to(message, f"এরর: {str(e)}")

# বট চালু করুন
if __name__ == "__main__":
    print("NXV বট চালু হচ্ছে...")
    bot.infinity_polling()
