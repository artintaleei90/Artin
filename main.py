import requests, zipfile, io, os, telebot
from fpdf import FPDF
from flask import Flask
from threading import Thread

# لینک مستقیم ZIP از ریلیز رسمی فونت وزیر
FONTS_ZIP_URL = 'https://github.com/rastikerdar/vazirmatn/releases/download/v33.003/vazirmatn-v33.003.zip'
FONTS_DIR = 'fonts'
FONT_PATH = os.path.join(FONTS_DIR, 'fonts', 'ttf', 'Vazirmatn-Regular.ttf')

def download_and_extract_fonts():
    if not os.path.exists(FONTS_DIR):
        print("📦 در حال دانلود فونت‌ها...")
        resp = requests.get(FONTS_ZIP_URL)
        resp.raise_for_status()
        print("🗜 در حال استخراج فونت‌ها...")
        with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
            z.extractall(FONTS_DIR)
        print("✅ فونت‌ها با موفقیت استخراج شدند.")
    else:
        print("✅ پوشه فونت‌ها وجود دارد، دانلود مجدد نیاز نیست.")
    if not os.path.isfile(FONT_PATH):
        raise FileNotFoundError(f"❌ فونت پیدا نشد: {FONT_PATH}")
    print(f"✅ فونت Regular پیدا شد: {FONT_PATH}")

download_and_extract_fonts()

class PDF(FPDF):
    def header(self):
        self.add_font('Vazirmatn', '', FONT_PATH, uni=True)
        self.set_font('Vazirmatn', '', 16)
        self.cell(0, 10, 'فاکتور سفارش', ln=1, align='C')
        self.ln(5)
    def footer(self):
        self.set_y(-15)
        self.set_font('Vazirmatn', '', 10)
        self.cell(0, 10, 'مرکز پوشاک هالستون', align='C')
    def add_customer_info(self, name, phone, city, address):
        self.set_font('Vazirmatn', '', 12)
        self.cell(0, 8, f'نام مشتری: {name}', ln=1, align='R')
        self.cell(0, 8, f'شماره تماس: {phone}', ln=1, align='R')
        self.cell(0, 8, f'شهر: {city}', ln=1, align='R')
        self.multi_cell(0, 8, f'آدرس: {address}', align='R')
        self.ln(5)
    def add_order_table(self, orders):
        self.set_font('Vazirmatn', 'B', 12)
        self.cell(120, 8, 'کد محصول', border=1, align='C')
        self.cell(40, 8, 'تعداد', border=1, ln=1, align='C')
        self.set_font('Vazirmatn', '', 12)
        for o in orders:
            self.cell(120, 8, o['code'], border=1, align='C')
            self.cell(40, 8, str(o['count']), border=1, ln=1, align='C')

app = Flask('')
@app.route('/')
def home(): return "Bot is running..."

def run(): app.run(host='0.0.0.0', port=8080)
Thread(target=run).start()

TOKEN = '7739258515:AAEUXIZ3ySZ9xp9W31l7qr__sZkbf6qcKnE'
CHANNEL_LINK = 'https://t.me/Halston_shop'
bot = telebot.TeleBot(TOKEN)
bot.remove_webhook()

user_data = {}

# تابع فرار دادن کاراکترهای MarkdownV2
def escape_markdown_v2(text):
    escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for ch in escape_chars:
        text = text.replace(ch, f"\\{ch}")
    return text

@bot.message_handler(commands=['start'])
def start(msg):
    chat = msg.chat.id
    user_data[chat] = {'orders': [], 'step': 'code'}
    
    text = (
        '🛍 خوش آمدید به ربات فروشگاه هالستون!\n\n'
        'برای شروع:\nلطفاً *کد محصول* را ارسال کنید.\n\n'
        f'🌐 کانال ما: {CHANNEL_LINK}'
    )
    text = escape_markdown_v2(text)
    bot.send_message(chat, text, parse_mode='MarkdownV2')

@bot.message_handler(func=lambda m: True)
def handle_message(m):
    chat = m.chat.id
    txt = m.text.strip()
    if chat not in user_data:
        return start(m)
    s = user_data[chat]['step']

    if s == 'code':
        user_data[chat]['current_code'] = txt
        user_data[chat]['step'] = 'count'
        bot.send_message(chat, escape_markdown_v2('✅ *تعداد* را وارد کن:'), parse_mode='MarkdownV2')

    elif s == 'count':
        if not txt.isdigit():
            return bot.send_message(chat, '❗ لطفاً فقط عدد وارد کن.')
        user_data[chat]['orders'].append({'code': user_data[chat]['current_code'], 'count': int(txt)})
        user_data[chat]['step'] = 'more'
        bot.send_message(chat, escape_markdown_v2('محصول دیگه‌ای داری؟ (بله/خیر)'), parse_mode='MarkdownV2')

    elif s == 'more':
        if txt.lower() == 'بله':
            user_data[chat]['step'] = 'code'
            bot.send_message(chat, escape_markdown_v2('کد محصول بعدی را ارسال کن:'), parse_mode='MarkdownV2')
        elif txt.lower() == 'خیر':
            user_data[chat]['step'] = 'name'
            bot.send_message(chat, escape_markdown_v2('📝 لطفاً نام کامل را وارد کن:'), parse_mode='MarkdownV2')
        else:
            bot.send_message(chat, escape_markdown_v2('لطفاً فقط *بله* یا *خیر* بنویس.'), parse_mode='MarkdownV2')

    elif s == 'name':
        user_data[chat]['name'] = txt
        user_data[chat]['step'] = 'phone'
        bot.send_message(chat, escape_markdown_v2('📱 شماره تماس را وارد کن:'), parse_mode='MarkdownV2')

    elif s == 'phone':
        user_data[chat]['phone'] = txt
        user_data[chat]['step'] = 'city'
        bot.send_message(chat, escape_markdown_v2('🏙 نام شهر را وارد کن:'), parse_mode='MarkdownV2')

    elif s == 'city':
        user_data[chat]['city'] = txt
        user_data[chat]['step'] = 'address'
        bot.send_message(chat, escape_markdown_v2('📍 آدرس دقیق را وارد کن:'), parse_mode='MarkdownV2')

    elif s == 'address':
        user_data[chat]['address'] = txt
        d = user_data[chat]
        pdf = PDF()
        pdf.add_page()
        pdf.add_customer_info(d['name'], d['phone'], d['city'], d['address'])
        pdf.add_order_table(d['orders'])
        fn = f'order_{chat}.pdf'
        pdf.output(fn)
        with open(fn, 'rb') as f:
            bot.send_document(chat, f)
        bot.send_message(chat, escape_markdown_v2('✅ فاکتور شما ثبت شد!\n🌐 کانال ما: ' + CHANNEL_LINK), parse_mode='MarkdownV2')
        os.remove(fn)
        user_data.pop(chat)

bot.infinity_polling()
