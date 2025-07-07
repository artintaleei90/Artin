import os
import requests
from fpdf import FPDF
import telebot
from flask import Flask
from threading import Thread

# مسیر فونت و لینک دانلود مستقیم فونت
FONTS_DIR = 'fonts'
FONT_PATH = f'{FONTS_DIR}/Vazirmatn-Regular.ttf'
FONT_URL = 'https://github.com/artintaleei90/Artin/raw/main/Vazirmatn-Regular.ttf'

# دانلود فونت اگر وجود نداشت
def download_font():
    if not os.path.exists(FONTS_DIR):
        os.makedirs(FONTS_DIR)
    if not os.path.exists(FONT_PATH):
        print("📥 در حال دانلود فونت...")
        r = requests.get(FONT_URL)
        if r.status_code == 200:
            with open(FONT_PATH, 'wb') as f:
                f.write(r.content)
            print("✅ فونت دانلود شد.")
        else:
            print("❌ خطا در دانلود فونت.")

download_font()

# کلاس PDF
class PDF(FPDF):
    def header(self):
        self.add_font('Vazir', '', FONT_PATH, uni=True)
        self.set_font('Vazir', '', 16)
        self.cell(0, 10, '🧾 فاکتور سفارش', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Vazir', '', 10)
        self.cell(0, 10, 'کانال ما: @Halston_shop', 0, 0, 'C')

    def add_customer_info(self, name, phone, city, address):
        self.set_font('Vazir', '', 12)
        self.cell(0, 10, f'👤 نام مشتری: {name}', 0, 1, 'R')
        self.cell(0, 10, f'📱 شماره تماس: {phone}', 0, 1, 'R')
        self.cell(0, 10, f'🏙 شهر: {city}', 0, 1, 'R')
        self.multi_cell(0, 10, f'📍 آدرس: {address}', 0, 1, 'R')
        self.ln(5)

    def add_order_table(self, orders):
        self.set_font('Vazir', 'B', 12)
        self.cell(80, 10, '🔢 کد محصول', 1, 0, 'C')
        self.cell(40, 10, '📦 تعداد', 1, 1, 'C')
        self.set_font('Vazir', '', 12)
        for item in orders:
            self.cell(80, 10, item['code'], 1, 0, 'C')
            self.cell(40, 10, str(item['count']), 1, 1, 'C')

# Flask برای فعال نگه‌داشتن روی Render
app = Flask('')
@app.route('/')
def home():
    return "Bot is running..."

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    Thread(target=run).start()

keep_alive()

# ✅ توکن ربات (حتماً توکن واقعی خودتو بذار سلطان!)
TOKEN = '7739258515:AAEUXIZ3ySZ9xp9W31l7qr__sZkbf6qcKnE'
bot = telebot.TeleBot(TOKEN)
user_data = {}

# شروع ربات
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_data[chat_id] = {'orders': [], 'step': 'code'}
    bot.send_message(chat_id, '🛍 خوش آمدی به فروشگاه هالستون!\nلطفا کد محصول را وارد کن:')

# پیام‌های کاربر
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    text = message.text.strip()

    if chat_id not in user_data:
        user_data[chat_id] = {'orders': [], 'step': 'code'}

    step = user_data[chat_id]['step']

    if step == 'code':
        user_data[chat_id]['current_code'] = text
        user_data[chat_id]['step'] = 'count'
        bot.send_message(chat_id, '✅ تعداد این محصول را وارد کن:')

    elif step == 'count':
        if not text.isdigit():
            bot.send_message(chat_id, '❗ لطفا فقط عدد وارد کن.')
            return
        count = int(text)
        code = user_data[chat_id]['current_code']
        user_data[chat_id]['orders'].append({'code': code, 'count': count})
        user_data[chat_id]['step'] = 'more'
        bot.send_message(chat_id, 'محصول دیگری داری؟ (بله / خیر)')

    elif step == 'more':
        if text.lower() == 'بله':
            user_data[chat_id]['step'] = 'code'
            bot.send_message(chat_id, 'کد محصول بعدی را وارد کن:')
        elif text.lower() == 'خیر':
            user_data[chat_id]['step'] = 'name'
            bot.send_message(chat_id, '📝 لطفا نام کامل خود را وارد کن:')
        else:
            bot.send_message(chat_id, 'لطفا فقط بله یا خیر بنویس.')

    elif step == 'name':
        user_data[chat_id]['name'] = text
        user_data[chat_id]['step'] = 'phone'
        bot.send_message(chat_id, '📱 شماره تماس را وارد کن:')

    elif step == 'phone':
        user_data[chat_id]['phone'] = text
        user_data[chat_id]['step'] = 'city'
        bot.send_message(chat_id, '🏙 نام شهر را وارد کن:')

    elif step == 'city':
        user_data[chat_id]['city'] = text
        user_data[chat_id]['step'] = 'address'
        bot.send_message(chat_id, '📍 آدرس دقیق را وارد کن:')

    elif step == 'address':
        user_data[chat_id]['address'] = text
        data = user_data[chat_id]

        pdf = PDF()
        pdf.add_page()
        pdf.add_customer_info(data['name'], data['phone'], data['city'], data['address'])
        pdf.add_order_table(data['orders'])

        filename = f'order_{chat_id}.pdf'
        pdf.output(filename)

        with open(filename, 'rb') as f:
            bot.send_document(chat_id, f)

        bot.send_message(chat_id, '✅ فاکتور شما ثبت شد.\n🛍 برای دیدن محصولات بیشتر به کانال ما بیا:\n👉 https://t.me/Halston_shop')
        os.remove(filename)
        user_data.pop(chat_id)

bot.infinity_polling()
