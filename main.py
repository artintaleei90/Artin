import os
from fpdf import FPDF
import telebot
from flask import Flask
from threading import Thread

# ------ keep_alive برای render ------
app = Flask('')

@app.route('/')
def home():
    return "Bot is running..."

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    Thread(target=run).start()

# ------ توکن ربات ------
TOKEN = "7739258515:AAEUXIZ3ySZ9xp9W31l7qr__sZkbf6qcKnE"
bot = telebot.TeleBot(TOKEN)

keep_alive()  # شروع سرویس وب برای زنده نگه داشتن ربات

user_data = {}

class InvoicePDF(FPDF):
    def header(self):
        self.add_font('Vazir', '', 'fonts/Vazir-Regular.ttf', uni=True)
        self.add_font('Vazir', 'B', 'fonts/Vazir-Bold.ttf', uni=True)
        self.set_font('Vazir', 'B', 16)
        self.cell(0, 10, 'فروشگاه هالستون', 0, 1, 'C')
        self.set_font('Vazir', '', 12)
        self.cell(0, 8, 'فاکتور خرید مشتری', 0, 1, 'C')
        self.ln(3)
        self.set_line_width(0.5)
        self.line(10, 35, 200, 35)
        self.ln(5)

    def footer(self):
        self.set_y(-35)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.set_font('Vazir', '', 10)
        self.cell(0, 8, 'مرکز پوشاک هالستون - تلفن: 09128883343', 0, 1, 'C')
        self.cell(0, 8, 'آدرس: تهران، خیابان مثال، پلاک 123', 0, 0, 'C')

    def add_customer_info(self, name, phone, city, address):
        self.set_font('Vazir', '', 12)
        self.cell(35, 8, 'نام مشتری:', 0, 0, 'R')
        self.cell(0, 8, name, 0, 1, 'R')
        self.cell(35, 8, 'شماره تماس:', 0, 0, 'R')
        self.cell(0, 8, phone, 0, 1, 'R')
        self.cell(35, 8, 'شهر:', 0, 0, 'R')
        self.cell(0, 8, city, 0, 1, 'R')
        self.cell(35, 8, 'آدرس:', 0, 0, 'R')
        self.multi_cell(0, 8, address, align='R')
        self.ln(5)

    def add_order_table(self, orders):
        self.set_font('Vazir', 'B', 12)
        self.set_fill_color(230, 230, 230)
        self.cell(90, 10, 'کد محصول', 1, 0, 'C', True)
        self.cell(90, 10, 'تعداد', 1, 1, 'C', True)

        self.set_font('Vazir', '', 12)
        total_count = 0
        for order in orders:
            self.cell(90, 10, order['code'], 1, 0, 'C')
            self.cell(90, 10, str(order['count']), 1, 1, 'C')
            total_count += order['count']

        self.set_font('Vazir', 'B', 12)
        self.cell(90, 10, 'جمع کل', 1, 0, 'C', True)
        self.cell(90, 10, str(total_count), 1, 1, 'C', True)

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_data[chat_id] = {"orders": [], "step": "code"}
    bot.send_message(chat_id, "🛍 خوش اومدی به ربات فروشگاه هالستون!\n\nلطفاً کد محصول رو وارد کن:")

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
        bot.send_message(chat_id, "✅ تعداد این محصول رو وارد کن:")

    elif step == "count":
        if not text.isdigit():
            bot.send_message(chat_id, "❗ فقط عدد وارد کن.")
            return
        count = int(text)
        code = user_data[chat_id]["current_code"]
        user_data[chat_id]["orders"].append({"code": code, "count": count})
        user_data[chat_id]["step"] = "more"
        bot.send_message(chat_id, "محصول دیگه‌ای داری؟ (بله / خیر)")

    elif step == "more":
        if text.lower() == "بله":
            user_data[chat_id]["step"] = "code"
            bot.send_message(chat_id, "کد محصول بعدی رو وارد کن:")
        elif text.lower() == "خیر":
            user_data[chat_id]["step"] = "name"
            bot.send_message(chat_id, "📝 لطفاً نام کاملت رو وارد کن:")
        else:
            bot.send_message(chat_id, "فقط بله یا خیر بنویس لطفاً.")

    elif step == "name":
        user_data[chat_id]["name"] = text
        user_data[chat_id]["step"] = "phone"
        bot.send_message(chat_id, "📱 شماره تماس رو وارد کن:")

    elif step == "phone":
        user_data[chat_id]["phone"] = text
        user_data[chat_id]["step"] = "city"
        bot.send_message(chat_id, "🏙 نام شهرت رو وارد کن:")

    elif step == "city":
        user_data[chat_id]["city"] = text
        user_data[chat_id]["step"] = "address"
        bot.send_message(chat_id, "📍 آدرس دقیق رو وارد کن:")

    elif step == "address":
        user_data[chat_id]["address"] = text
        data = user_data[chat_id]

        pdf = InvoicePDF()
        pdf.add_page()
        pdf.add_customer_info(data["name"], data["phone"], data["city"], data["address"])
        pdf.add_order_table(data["orders"])

        filename = f"order_{chat_id}.pdf"
        pdf.output(filename)

        with open(filename, "rb") as f:
            bot.send_document(chat_id, f)

        bot.send_message(chat_id, "✅ فاکتور ثبت شد. فایل بالا رو برای نهایی کردن به ۰۹۱۲۸۸۸۳۳۴۳ بفرست.")
        os.remove(filename)
        user_data.pop(chat_id)

bot.infinity_polling()
