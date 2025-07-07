import telebot
import requests
from keep_alive import keep_alive  # فایل keep_alive.py برای زنده نگه داشتن سرور Flask

TOKEN = "7266241036:AAFRW-1pMk1syso8kS_mXnoXFtVbsrpFdDY"
bot = telebot.TeleBot(TOKEN)

CHANNEL_LINK = "https://t.me/Halston_shop"
GROUP_LINK = "https://t.me/Halston_shop"

keep_alive()

user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_data[chat_id] = {
        "orders": [],
        "step": "code"
    }
    welcome_msg = f"""به ربات هالستون خوش آمدید 👗🛍
کانال ما: {CHANNEL_LINK}
گروه پشتیبانی: {GROUP_LINK}

لطفاً کد محصول را وارد کن:"""
    bot.send_message(chat_id, welcome_msg)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    text = message.text.strip()

    if chat_id not in user_data:
        user_data[chat_id] = {"orders": [], "step": "code"}
        bot.send_message(chat_id, "شروع جدید! لطفاً کد محصول را وارد کن:")
        return

    step = user_data[chat_id]["step"]

    if step == "code":
        user_data[chat_id]["current_code"] = text
        user_data[chat_id]["step"] = "count"
        bot.send_message(chat_id, "تعداد محصول رو وارد کن:")

    elif step == "count":
        if not text.isdigit():
            bot.send_message(chat_id, "لطفاً فقط عدد وارد کن.")
            return
        count = int(text)
        code = user_data[chat_id]["current_code"]
        user_data[chat_id]["orders"].append({"code": code, "count": count})
        user_data[chat_id]["step"] = "more"
        bot.send_message(chat_id, "سفارش دیگه‌ای داری؟ (بله / خیر)")

    elif step == "more":
        if text.lower() == "بله":
            user_data[chat_id]["step"] = "code"
            bot.send_message(chat_id, "کد محصول بعدی رو وارد کن:")
        elif text.lower() == "خیر":
            user_data[chat_id]["step"] = "name"
            bot.send_message(chat_id, "نام کامل خودتو وارد کن:")
        else:
            bot.send_message(chat_id, "فقط 'بله' یا 'خیر' بنویس لطفاً.")

    elif step == "name":
        user_data[chat_id]["full_name"] = text
        user_data[chat_id]["step"] = "city"
        bot.send_message(chat_id, "نام شهرت رو وارد کن:")

    elif step == "city":
        user_data[chat_id]["city"] = text
        user_data[chat_id]["step"] = "address"
        bot.send_message(chat_id, "آدرس دقیق رو وارد کن:")

    elif step == "address":
        user_data[chat_id]["address"] = text
        user_data[chat_id]["step"] = "phone"
        bot.send_message(chat_id, "شماره تماس همراهت رو وارد کن:")

    elif step == "phone":
        # چک کردن شماره تماس ساده
        if not (text.isdigit() and (8 <= len(text) <= 15)):
            bot.send_message(chat_id, "لطفاً شماره تماس معتبر وارد کن (فقط اعداد، ۸ تا ۱۵ رقم).")
            return
        user_data[chat_id]["phone"] = text
        user_data[chat_id]["step"] = "done"

        data = {
            "full_name": user_data[chat_id]["full_name"],
            "city": user_data[chat_id]["city"],
            "address": user_data[chat_id]["address"],
            "phone": user_data[chat_id]["phone"],
            "orders": user_data[chat_id]["orders"]
        }

        try:
            response = requests.post("https://artin-ehb4.onrender.com/render", json=data)
            if response.status_code == 200:
                bot.send_document(chat_id, response.content, visible_file_name="order.pdf")
                bot.send_message(chat_id, "✅ سفارش ثبت شد. لطفاً برای نهایی کردن با شماره ۰۹۱۲۸۸۸۳۳۴۳ تماس بگیر.")
            else:
                bot.send_message(chat_id, "❌ مشکلی در ساخت PDF پیش آمد.")
        except Exception as e:
            print(e)
            bot.send_message(chat_id, "❌ اتصال به سرور PDF برقرار نشد.")

        user_data.pop(chat_id)

print("✅ ربات روشن شد و آماده‌ست سلطان!")
bot.infinity_polling()
