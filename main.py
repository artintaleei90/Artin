import telebot
from flask import Flask, request

TOKEN = "7739258515:AAEUXIZ3ySZ9xp9W31l7qr__sZkbf6qcKnE"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
user_data = {}

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '', 200

@app.route('/')
def index():
    return "من زنده‌ام سلطان 😎"

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_data[chat_id] = {"orders": [], "step": "code"}
    bot.send_message(chat_id, "به ربات هالستون خوش آمدی 👗🛍\nکد محصول رو وارد کن:")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    text = message.text.strip()

    if chat_id not in user_data:
        user_data[chat_id] = {"orders": [], "step": "code"}

    step = user_data[chat_id]["step"]

    if step == "code":
        user_data[chat_id]["current_code"] = text
        user_data[chat_id]["step"] = "count"
        bot.send_message(chat_id, "تعداد محصول رو وارد کن:")

    elif step == "count":
        if not text.isdigit():
            bot.send_message(chat_id, "لطفاً فقط عدد وارد کن.")
            return
        user_data[chat_id]["orders"].append({"code": user_data[chat_id]["current_code"], "count": int(text)})
        user_data[chat_id]["step"] = "more"
        bot.send_message(chat_id, "سفارش دیگه‌ای داری؟ (بله / خیر)")

    elif step == "more":
        if text.lower() == "بله":
            user_data[chat_id]["step"] = "code"
            bot.send_message(chat_id, "کد محصول بعدی رو وارد کن:")
        elif text.lower() == "خیر":
            user_data[chat_id]["step"] = "name"
            bot.send_message(chat_id, "نام کاملتو وارد کن:")
        else:
            bot.send_message(chat_id, "لطفاً فقط 'بله' یا 'خیر' بنویس.")

    elif step == "name":
        user_data[chat_id]["full_name"] = text
        user_data[chat_id]["step"] = "city"
        bot.send_message(chat_id, "نام شهرتو وارد کن:")

    elif step == "city":
        user_data[chat_id]["city"] = text
        user_data[chat_id]["step"] = "address"
        bot.send_message(chat_id, "آدرس دقیق رو وارد کن:")

    elif step == "address":
        user_data[chat_id]["address"] = text
        user_data[chat_id]["step"] = "phone"
        bot.send_message(chat_id, "شماره همراهتو وارد کن:")

    elif step == "phone":
        user_data[chat_id]["phone"] = text

        # ساخت متن نهایی سفارش
        text_order = f"📦 سفارش جدید:\n\n"
        text_order += f"👤 نام کامل: {user_data[chat_id]['full_name']}\n"
        text_order += f"🏙 شهر: {user_data[chat_id]['city']}\n"
        text_order += f"📍 آدرس: {user_data[chat_id]['address']}\n"
        text_order += f"📞 شماره همراه: {user_data[chat_id]['phone']}\n"
        text_order += f"🛒 سفارش‌ها:\n"

        for o in user_data[chat_id]["orders"]:
            text_order += f"  - کد: {o['code']} | تعداد: {o['count']}\n"

        bot.send_message(chat_id, "✅ سفارش شما ثبت شد. متشکریم!")
        # می‌تونی اینجا این متن رو به کانال یا ادمین هم بفرستی:
        admin_id = 123456789  # شناسه تلگرام خودت رو اینجا بگذار
        bot.send_message(admin_id, text_order)

        user_data.pop(chat_id)

if __name__ == '__main__':
    import os
    bot.remove_webhook()
    bot.set_webhook(url=f"https://yourdomain.com/{TOKEN}")  # آدرس وب‌هوک واقعی‌ت رو بگذار
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
