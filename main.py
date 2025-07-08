import os
import requests, zipfile, io
from fpdf import FPDF
from flask import Flask, request
import telebot

TOKEN = '7739258515:AAEUXIZ3ySZ9xp9W31l7qr__sZkbf6qcKnE'
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

FONTS_ZIP_URL = 'https://github.com/rastikerdar/vazirmatn/releases/download/v33.003/vazirmatn-v33.003.zip'
FONTS_DIR = 'fonts'
FONT_REGULAR = os.path.join(FONTS_DIR, 'fonts', 'ttf', 'Vazirmatn-Regular.ttf')
FONT_BOLD = os.path.join(FONTS_DIR, 'fonts', 'ttf', 'Vazirmatn-Bold.ttf')

def download_and_extract_fonts():
    if not os.path.exists(FONTS_DIR):
        print("📦 دانلود فونت‌ها...")
        resp = requests.get(FONTS_ZIP_URL)
        resp.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
            z.extractall(FONTS_DIR)
        print("✅ فونت‌ها استخراج شدند.")
    else:
        print("✅ فونت‌ها قبلا دانلود شده‌اند.")

download_and_extract_fonts()

class PDF(FPDF):
    def header(self):
        self.add_font('Vazirmatn', '', FONT_REGULAR, uni=True)
        self.add_font('Vazirmatn', 'B', FONT_BOLD, uni=True)
        self.set_font('Vazirmatn', 'B', 16)
        self.cell(0, 10, 'فاکتور سفارش', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Vazirmatn', '', 10)
        self.cell(0, 10, 'مرکز پوشاک هالستون', 0, 0, 'C')

    def add_customer_info(self, name, phone, city, address):
        self.set_font('Vazirmatn', '', 12)
        self.cell(0, 8, f'نام مشتری: {name}', 0, 1, 'R')
        self.cell(0, 8, f'شماره تماس: {phone}', 0, 1, 'R')
        self.cell(0, 8, f'شهر: {city}', 0, 1, 'R')
        self.multi_cell(0, 8, f'آدرس: {address}', 0, 'R')
        self.ln(5)

    def add_order_table(self, orders):
        self.set_font('Vazirmatn', 'B', 12)
        self.cell(120, 8, 'کد محصول', 1, 0, 'C')
        self.cell(40, 8, 'تعداد', 1, 1, 'C')
        self.set_font('Vazirmatn', '', 12)
        for o in orders:
            self.cell(120, 8, o['code'], 1, 0, 'C')
            self.cell(40, 8, str(o['count']), 1, 1, 'C')

user_data = {}

@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return 'ok', 200

@app.route('/')
def index():
    return "Bot is running!"

@bot.message_handler(commands=['start'])
def start(msg):
    chat = msg.chat.id
    user_data[chat] = {'orders': [], 'step': 'code'}
    bot.send_message(chat,
        '🛍 خوش آمدید به ربات فروشگاه هالستون!\n'
        'لطفاً کد محصول را ارسال کنید.')

@bot.message_handler(func=lambda m: True)
def handle_message(msg):
    chat = msg.chat.id
    txt = msg.text.strip()
    if chat not in user_data:
        start(msg)
        return
    s = user_data[chat]['step']

    if s == 'code':
        user_data[chat]['current_code'] = txt
        user_data[chat]['step'] = 'count'
        bot.send_message(chat, '✅ تعداد را وارد کنید:')
    elif s == 'count':
        if not txt.isdigit():
            bot.send_message(chat, '❗ لطفاً فقط عدد وارد کنید.')
            return
        user_data[chat]['orders'].append({'code': user_data[chat]['current_code'], 'count': int(txt)})
        user_data[chat]['step'] = 'more'
        bot.send_message(chat, 'محصول دیگری دارید؟ (بله/خیر)')
    elif s == 'more':
        if txt.lower() == 'بله':
            user_data[chat]['step'] = 'code'
            bot.send_message(chat, 'کد محصول بعدی را ارسال کنید:')
        elif txt.lower() == 'خیر':
            user_data[chat]['step'] = 'name'
            bot.send_message(chat, '📝 لطفاً نام کامل خود را وارد کنید:')
        else:
            bot.send_message(chat, 'لطفاً فقط "بله" یا "خیر" وارد کنید.')
    elif s == 'name':
        user_data[chat]['name'] = txt
        user_data[chat]['step'] = 'phone'
        bot.send_message(chat, '📱 شماره تماس را وارد کنید:')
    elif s == 'phone':
        user_data[chat]['phone'] = txt
        user_data[chat]['step'] = 'city'
        bot.send_message(chat, '🏙 نام شهر را وارد کنید:')
    elif s == 'city':
        user_data[chat]['city'] = txt
        user_data[chat]['step'] = 'address'
        bot.send_message(chat, '📍 آدرس دقیق را وارد کنید:')
    elif s == 'address':
        user_data[chat]['address'] = txt
        d = user_data[chat]

        pdf = PDF()
        pdf.add_page()
        pdf.add_customer_info(d['name'], d['phone'], d['city'], d['address'])
        pdf.add_order_table(d['orders'])

        fn = f'order_{chat}.pdf'

        try:
            pdf.output(fn)
            with open(fn, 'rb') as f:
                bot.send_document(chat, f)
            bot.send_message(chat, '✅ فاکتور شما ثبت شد!\n🌐 کانال ما: https://t.me/Halston_shop')
            print(f"[INFO] PDF ساخته و ارسال شد برای {chat}")
        except Exception as e:
            print(f"[ERROR] هنگام ساخت یا ارسال PDF: {e}")
            bot.send_message(chat, '⚠️ خطایی رخ داد، لطفا دوباره تلاش کنید.')

        if os.path.exists(fn):
            os.remove(fn)

        user_data.pop(chat)

if __name__ == "__main__":
    # حذف webhook قبلی و تنظیم webhook جدید
    print(bot.remove_webhook())
    bot.set_webhook(url='https://artin-um4v.onrender.com/' + TOKEN)

    app.run(host='0.0.0.0', port=8080)
