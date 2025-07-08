import os
from flask import Flask, request
import telebot
from fpdf import FPDF

app = Flask(__name__)
TOKEN = '7739258515:AAEUXIZ3ySZ9xp9W31l7qr__sZkbf6qcKnE'
bot = telebot.TeleBot(TOKEN)

# اضافه کردن فونت فارسی
FONT_PATH = 'fonts/Vazirmatn-Regular.ttf'
if not os.path.exists(FONT_PATH):
    raise FileNotFoundError(f"❌ فونت پیدا نشد: {FONT_PATH}")

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font('Vazir', '', FONT_PATH, uni=True)
        self.set_font('Vazir', '', 14)

    def header(self):
        self.cell(0, 10, '🧾 فاکتور خرید', ln=True, align='C')

    def invoice_body(self, name, item, price):
        self.cell(0, 10, f'نام مشتری: {name}', ln=True, align='R')
        self.cell(0, 10, f'محصول: {item}', ln=True, align='R')
        self.cell(0, 10, f'قیمت: {price} تومان', ln=True, align='R')

@app.route('/', methods=['GET', 'POST'])
def webhook():
    if request.method == 'POST':
        update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
        bot.process_new_updates([update])
        return "!", 200
    return "سلام سلطان 😎", 200

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "سلام! برای ساخت فاکتور بنویس: فاکتور [اسم] [محصول] [قیمت]")

@bot.message_handler(func=lambda m: m.text.startswith("فاکتور"))
def create_invoice(message):
    try:
        parts = message.text.split()
        name, item, price = parts[1], parts[2], parts[3]
        pdf = PDF()
        pdf.add_page()
        pdf.invoice_body(name, item, price)

        filename = f"invoice_{message.chat.id}.pdf"
        pdf.output(filename)

        with open(filename, 'rb') as f:
            bot.send_document(message.chat.id, f)
        os.remove(filename)
    except Exception as e:
        bot.reply_to(message, f'خطا: {str(e)}')

if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url='https://artin-um4v.onrender.com')
    app.run(host='0.0.0.0', port=8080)
