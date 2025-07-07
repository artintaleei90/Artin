import telebot
import requests
from flask import Flask, request
from fpdf import FPDF

TOKEN = "7739258515:AAEUXIZ3ySZ9xp9W31l7qr__sZkbf6qcKnE"
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)
user_data = {}

@app.route(f'/{TOKEN}', methods=['POST'])
def getMessage():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '', 200

@app.route('/')
def index():
    return "من زنده‌ام سلطان 😎"

# روت مخصوص ساخت PDF
@app.route('/render', methods=['POST'])
def render_pdf():
    data = request.get_json()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="📦 سفارش جدید از ربات تلگرام", ln=True, align='C')
    pdf.cell(200, 10, txt="-------------------------------", ln=True, align='L')

    pdf.cell(200, 10, txt=f"👤 نام: {data['full_name']}", ln=True)
    pdf.cell(200, 10, txt=f"🏙 شهر: {data['city']}", ln=True)
    pdf.cell(200, 10, txt=f"📍 آدرس: {data['address']}", ln=True)
    pdf.cell(200, 10, txt="🛒 سفارش‌ها:", ln=True)

    for item in data['orders']:
        pdf.cell(200, 10, txt=f"- کد: {item['code']} / تعداد: {item['count']}", ln=True)

    pdf.output("order.pdf")
    return open("order.pdf", "rb").read(), 200

# دستور start
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_data[chat_id] = {"orders": [], "step": "code"}
    bot.send_message(chat_id, "به ربات هالستون خوش آمدی 👗🛍\nکد محصول رو وارد کن:")

# مدیریت مراحل سفارش
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
            bot.send_message(chat_id, "فقط بنویس بله یا خیر.")

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

        data = {
            "full_name": user_data[chat_id]["full_name"],
            "city": user_data[chat_id]["city"],
            "address": user_data[chat_id]["address"],
            "orders": user_data[chat_id]["orders"]
        }

        try:
            response = requests.post("https://artin-ehb4.onrender.com/render", json=data)
            if response.status_code == 200:
                bot.send_document(chat_id, response.content, visible_file_name="order.pdf")
                bot.send_message(chat_id, "✅ سفارش ثبت شد. برای نهایی‌کردن با ۰۹۱۲۸۸۸۳۳۴۳ تماس بگیر.")
            else:
                bot.send_message(chat_id, "❌ مشکلی در ساخت فایل PDF پیش اومد.")
        except:
            bot.send_message(chat_id, "❌ اتصال به سرور برقرار نشد.")
        
        user_data.pop(chat_id)

# اجرای Flask سرور
if __name__ == '__main__':
    import os
    import telebot.util
    bot.remove_webhook()
    bot.set_webhook(url=f"https://artin-ehb4.onrender.com/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 8080)))
