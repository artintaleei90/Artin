import requests
import zipfile
import io
import os
import telebot
from fpdf import FPDF
from flask import Flask
from threading import Thread

# لینک فونت
FONTS_ZIP_URL = 'https://github.com/artintaleei90/Artin/raw/main/vazirmatn-v33.003.zip'
FONTS_DIR = 'fonts'
FONT_NAME = 'Vazirmatn-Regular.ttf'
FONT_FINAL_PATH = os.path.join(FONTS_DIR, FONT_NAME)

def download_and_extract_fonts():
    if not os.path.exists(FONTS_DIR):
        os.makedirs(FONTS_DIR)

    if not os.path.exists(FONT_FINAL_PATH):
        print("📥 Downloading fonts zip...")
        response = requests.get(FONTS_ZIP_URL)
        if response.status_code == 200:
            with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
                zip_ref.extractall(FONTS_DIR)
            print("✅ Fonts extracted.")

            for root, dirs, files in os.walk(FONTS_DIR):
                for file in files:
                    if file == FONT_NAME:
                        src_path = os.path.join(root, file)
                        with open(src_path, 'rb') as src, open(FONT_FINAL_PATH, 'wb') as dst:
                            dst.write(src.read())
                        return
            print("❌ Font file not found in extracted files.")
        else:
            print("❌ Failed to download fonts zip.")
    else:
        print("✅ Font already exists.")

download_and_extract_fonts()

# کلاس PDF
class PDF(FPDF):
    def header(self):
        self.add_font('Vazir', '', FONT_FINAL_PATH, uni=True)
        self.set_font('Vazir', '', 14)
        self.cell(0, 10, '🧾 فاکتور سفارش', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Vazir', '', 8)
        self.cell(0, 10, 'مرکز پوشاک هالستون - @Halston_shop', 0, 0, 'C')

    def add_customer_info(self, name, phone, city, address):
        self.set_font('Vazir', '', 12)
        self.cell(0, 10, f'نام مشتری: {name}', 0, 1, 'R')
        self.cell(0, 10, f'شماره تماس: {phone}', 0, 1, 'R')
        self.cell(0, 10, f'شهر: {city}', 0, 1, 'R')
        self.multi_cell(0, 10, f'آدرس: {address}', 0, 1, 'R')
        self.ln(5)

    def add_order_table(self, orders):
        self.set_font('Vazir', 'B', 12)
        self.cell(80, 10, 'کد محصول', 1, 0, 'C')
        self.cell(40, 10, 'تعداد', 1, 1, 'C')
        self.set_font('Vazir', '', 12)
        for item in orders:
            self.cell(80, 10, item['code'], 1, 0, 'C')
            self.cell(40, 10, str(item['count']), 1, 1, 'C')

# وب سرور برای Render
app = Flask('')
@app.route('/')
def home():
    return "Bot is running..."

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    Thread(target=run).start()

# توکن ربات
TOKEN = '7739258515:AAEUXIZ3ySZ9xp9W31l7qr__sZkbf6qcKnE'
bot = telebot.TeleBot(TOKEN)
user_data = {}

keep_alive()

# 📦 شروع با /start
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_data[chat_id] = {'orders': [], 'step': 'code'}
    bot.send_message(chat_id, '''🛍 به ربات فروشگاه هالستون خوش آمدی!

🧵 می‌تونی همین‌جا سفارش خودتو ثبت کنی و فاکتور PDF بگیری.

📢 برای دیدن محصولات بیشتر عضو کانال ما شو:
🔗 https://t.me/Halston_shop

🔢 لطفاً کد اولین محصول رو وارد کن:''')

# 📋 پردازش پیام‌ها
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
        bot.send_message(chat_id, '➕ محصول دیگری داری؟ (بله / خیر)')

    elif step == 'more':
        if text.lower() == 'بله':
            user_data[chat_id]['step'] = 'code'
            bot.send_message(chat_id, '🔢 کد محصول بعدی را وارد کن:')
        elif text.lower() == 'خیر':
            user_data[chat_id]['step'] = 'name'
            bot.send_message(chat_id, '📝 لطفا نام کامل خود را وارد کن:')
        else:
            bot.send_message(chat_id, '⚠️ لطفا فقط "بله" یا "خیر" بنویس.')

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

        bot.send_message(chat_id, '✅ فاکتور شما با موفقیت ثبت و ارسال شد.\n\n📢 کانال فروشگاه:\nhttps://t.me/Halston_shop')
        os.remove(filename)
        user_data.pop(chat_id)

# رفع ارور 409
bot.remove_webhook()
bot.infinity_polling()
