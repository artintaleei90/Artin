import os
import io
import zipfile
import requests
from flask import Flask, request
import telebot
from fpdf import FPDF

TOKEN = '7739258515:AAEUXIZ3ySZ9xp9W31l7qr__sZkbf6qcKnE'
WEBHOOK_URL = f'https://artin-d8qn.onrender.com/{TOKEN}'

FONTS_ZIP_URL = 'https://github.com/rastikerdar/vazirmatn/releases/download/v33.003/vazirmatn-v33.003.zip'
FONTS_DIR = 'fonts'
FONT_REGULAR = os.path.join(FONTS_DIR, 'Vazirmatn-Regular.ttf')
FONT_BOLD = os.path.join(FONTS_DIR, 'Vazirmatn-Bold.ttf')

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
user_data = {}

def download_fonts():
    if not os.path.exists(FONTS_DIR):
        os.makedirs(FONTS_DIR)
    if not os.path.isfile(FONT_REGULAR) or not os.path.isfile(FONT_BOLD):
        print("📦 در حال دانلود فونت‌ها...")
        r = requests.get(FONTS_ZIP_URL)
        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
            z.extractall(FONTS_DIR)
        print("✅ فونت‌ها استخراج شدند.")

download_fonts()

class PDF(FPDF):
    def header(self):
        self.add_font('Vazir', '', FONT_REGULAR, uni=True)
        self.add_font('Vazir', 'B', FONT_BOLD, uni=True)
        self.set_font('Vazir', 'B', 16)
        self.cell(0, 10, 'فاکتور سفارش', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Vazir', '', 10)
        self.cell(0, 10, 'مرکز پوشاک هالستون', 0, 0, 'C')

    def add_customer_info(self, name, phone, city, address):
        self.set_font('Vazir', '', 12)
        self.cell(0, 8, f'نام مشتری: {name}', 0, 1, 'R')
        self.cell(0, 8, f'شماره تماس: {phone}', 0, 1, 'R')
        self.cell(0, 8, f'شهر: {city}', 0, 1, 'R')
        self.multi_cell(0, 8, f'آدرس: {address}', 0, 'R')
        self.ln(5)

    def add_order_table(self, orders):
        self.set_font('Vazir', 'B', 12)
        self.cell(120, 8, 'کد محصول', 1, 0, 'C')
        self.cell(40, 8, 'تعداد', 1, 1, 'C')
        self.set_font('Vazir', '', 12)
        for o in orders:
            self.cell(120, 8, o['code'], 1, 0, 'C')
            self.cell(40, 8, str(o['count']), 1, 1, 'C')

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return 'OK', 200

@app.route('/', methods=['GET'])
def index():
    return '🤖 ربات هالستون فعال است.', 200

@bot.message_handler(commands=['start'])
def start(msg):
    chat = msg.chat.id
    user_data[chat] = {'orders': [], 'step': 'code'}
    bot.send_message(chat,
        '🛍 خوش آمدید به ربات فروشگاه هالستون!\n\n'
        'برای شروع:\nلطفاً کد محصول را ارسال کنید.\n\n'
        '🌐 کانال ما: https://t.me/Halston_shop')

@bot.message_handler(func=lambda m: True)
def handle_message(msg):
    chat = msg.chat.id
    text = msg.text.strip()
    if chat not in user_data:
        start(msg)
        return

    step = user_data[chat]['step']

    if step == 'code':
        user_data[chat]['current_code'] = text
        user_data[chat]['step'] = 'count'
        bot.send_message(chat, '✅ تعداد را وارد کنید:')

    elif step == 'count':
        if not text.isdigit():
            bot.send_message(chat, '❗ لطفاً فقط عدد وارد کنید.')
            return
        user_data[chat]['orders'].append({'code': user_data[chat]['current_code'], 'count': int(text)})
        user_data[chat]['step'] = 'more'
        bot.send_message(chat, 'محصول دیگری دارید؟ (بله/خیر)')

    elif step == 'more':
        if text.lower() == 'بله':
            user_data[chat]['step'] = 'code'
            bot.send_message(chat, 'کد محصول بعدی را ارسال کنید:')
        elif text.lower() == 'خیر':
            user_data[chat]['step'] = 'name'
            bot.send_message(chat, '📝 نام کامل خود را وارد کنید:')
        else:
            bot.send_message(chat, 'لطفاً فقط "بله" یا "خیر" بنویسید.')

    elif step == 'name':
        user_data[chat]['name'] = text
        user_data[chat]['step'] = 'phone'
        bot.send_message(chat, '📱 شماره تماس را وارد کنید:')

    elif step == 'phone':
        user_data[chat]['phone'] = text
        user_data[chat]['step'] = 'city'
        bot.send_message(chat, '🏙 نام شهر را وارد کنید:')

    elif step == 'city':
        user_data[chat]['city'] = text
        user_data[chat]['step'] = 'address'
        bot.send_message(chat, '📍 آدرس دقیق را وارد کنید:')

    elif step == 'address':
        user_data[chat]['address'] = text

        data = user_data[chat]
        pdf = PDF()
        pdf.add_page()
        pdf.add_customer_info(data['name'], data['phone'], data['city'], data['address'])
        pdf.add_order_table(data['orders'])

        file_name = f'order_{chat}.pdf'
        pdf.output(file_name)

        with open(file_name, 'rb') as f:
            bot.send_document(chat, f)

        bot.send_message(chat, '✅ فاکتور شما ثبت شد!\n🌐 کانال ما: https://t.me/Halston_shop')
        os.remove(file_name)
        user_data.pop(chat)

def setup_webhook():
    print('در حال حذف وب‌هوک قدیمی...')
    bot.remove_webhook()
    print(f'در حال ست‌کردن وب‌هوک به {WEBHOOK_URL} ...')
    bot.set_webhook(url=WEBHOOK_URL)
    print('وب‌هوک ست شد!')

if __name__ == '__main__':
    download_fonts()
    setup_webhook()
    port = int(os.environ.get('PORT', 10000))
    print(f'سرور روی پورت {port} اجرا شد.')
    app.run(host='0.0.0.0', port=port)
