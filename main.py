import telebot
from fpdf import FPDF
import os
from flask import Flask
from threading import Thread

# keep_alive برای render
app = Flask('')

@app.route('/')
def home():
    return "Bot is running..."

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    Thread(target=run).start()

# توکن رباتتو اینجا بزار
TOKEN = "7739258515:AAEUXIZ3ySZ9xp9W31l7qr__sZkbf6qcKnE"
bot = telebot.TeleBot(TOKEN)
keep_alive()

user_data = {}

class PDF(FPDF):
    def header(self):
        # اضافه کردن فونت وزیر
        self.add_font('Vazir', '', 'fonts/Vazir-Regular.ttf', uni=True)
        self.set_font('Vazir', 'B', 16)
        self.cell(0, 10, "فاکتور سفارش", 0, 1, "C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.add_font('Vazir', '', 'fonts/Vazir-Regular.ttf', uni=True)
        self.set_font('Vazir', 'I', 10)
        self.cell(0, 10, "مرکز پوشاک هالستون", 0, 0, "C")

    def add_customer_info(self, name, phone, city, address):
        self.add_font('Vazir', '', 'fonts/Vazir-Regular.ttf', uni=True)
        self.set_font('Vazir', '', 12)
        self.cell(0, 10, f"نام مشتری: {name}", 0, 1, "R")
        self.cell(0, 10, f"شماره تماس: {phone}", 0, 1, "R")
        self.cell(0, 10, f"شهر: {city}", 0, 1, "R")
        self.multi_cell(0, 10, f"آدرس: {address}", align="R")
        self.ln(5)

    def add_order_table(self, orders):
        self.add_font('Vazir', '', 'fonts/Vazir-Regular.ttf', uni=True)
        self.set_font('Vazir', 'B', 12)
        self.cell(70, 10, "کد محصول", 1, 0, "C")
        self.cell(40, 10, "تعداد", 1, 1, "C")
        self.set_font('Vazir', '', 12)
        for item in orders:
            self.cell(70, 10, item['code'], 1, 0, "C")
            self.cell(40, 10, str(item['count']), 1, 1, "C")

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_data[chat_id] = {"orders": [], "step": "code"}
    bot.send_message(chat_id, "🛍 خوش آمدی به ربات فروشگاه هالستون!\nلطفا کد محصول را وارد کن:")

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
        bot.send_message(chat_id, "✅ تعداد این محصول را وارد کن:")

    elif step == "count":
        if not text.isdigit():
            bot.send_message(chat_id, "❗ فقط عدد وارد کن.")
            return
        count = int(text)
        code = user_data[chat_id]["current_code"]
        user_data[chat_id]["orders"].append({"code": code, "count": count})
        user_data[chat_id]["step"] = "more"
        bot.send_message(chat_id, "محصول دیگری داری؟ (بله / خیر)")

    elif step == "more":
        if text.lower() == "بله":
            user_data[chat_id]["step"] = "code"
            bot.send_message(chat_id, "کد محصول بعدی را وارد کن:")
        elif text.lower() == "خیر":
            user_data[chat_id]["step"] = "name"
            bot.send_message(chat_id, "📝 لطفا نام کاملت را وارد کن:")
        else:
            bot.send_message(chat_id, "لطفا فقط 'بله' یا 'خیر' بنویس.")

    elif step == "name":
        user_data[chat_id]["name"] = text
        user_data[chat_id]["step"] = "phone"
        bot.send_message(chat_id, "📱 شماره تماس را وارد کن:")

    elif step == "phone":
        user_data[chat_id]["phone"] = text
        user_data[chat_id]["step"] = "city"
        bot.send_message(chat_id, "🏙 نام شهر را وارد کن:")

    elif step == "city":
        user_data[chat_id]["city"] = text
        user_data[chat_id]["step"] = "address"
        bot.send_message(chat_id, "📍 آدرس دقیق را وارد کن:")

    elif step == "address":
        user_data[chat_id]["address"] = text
        data = user_data[chat_id]

        pdf = PDF()
        pdf.add_page()
        pdf.add_customer_info(data["name"], data["phone"], data["city"], data["address"])
        pdf.add_order_table(data["orders"])

        filename = f"order_{chat_id}.pdf"
        pdf.output(filename)

        with open(filename, "rb") as f:
            bot.send_document(chat_id, f)

        bot.send_message(chat_id, "✅ فاکتور ثبت شد. فایل را برای نهایی کردن به ۰۹۱۲۸۸۸۳۳۴۳ بفرست.")
        os.remove(filename)
        user_data.pop(chat_id)

bot.infinity_polling()
