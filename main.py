import requests, zipfile, io, os, telebot
from fpdf import FPDF
from flask import Flask
from threading import Thread

# لینک فایل ZIP فونت از GitHub
FONTS_ZIP_URL = 'https://github.com/rastikerdar/vazirmatn/raw/v33.003/fonts/ttf/Vazirmatn-Regular.ttf.zip'
FONTS_DIR = 'fonts'

def download_fonts():
    os.makedirs(FONTS_DIR, exist_ok=True)
    font_zip = os.path.join(FONTS_DIR, 'Vazirmatn-Regular.ttf.zip')
    if not os.path.exists(font_zip):
        print("📦 دانلود فونت...")
        r = requests.get(FONTS_ZIP_URL)
        if r.status_code == 200:
            open(font_zip, 'wb').write(r.content)
            print("🗜 استخراج فونت...")
            with zipfile.ZipFile(font_zip, 'r') as z:
                z.extractall(FONTS_DIR)
            print("✅ فونت استخراج شد.")
        else:
            raise Exception("❌ دانلود فونت با خطا مواجه شد!")
    else:
        print("✅ فونت قبلاً دانلود شده.")

download_fonts()

FONT_PATH = os.path.join(FONTS_DIR, 'Vazirmatn-Regular.ttf')
if not os.path.exists(FONT_PATH):
    raise FileNotFoundError(f"❌ فونت پیدا نشد: {FONT_PATH}")

class PDF(FPDF):
    def header(self):
        self.add_font('Vazir', '', FONT_PATH, uni=True)
        self.set_font('Vazir', '', 14)
        self.cell(0, 10, 'فاکتور سفارش', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Vazir', '', 8)
        self.cell(0, 10, 'مرکز پوشاک هالستون', 0, 0, 'C')

    def add_customer_info(self, name, phone, city, address):
        self.set_font('Vazir', '', 12)
        for label, value in [('نام مشتری', name), ('شماره تماس', phone),
                             ('شهر', city), ('آدرس', address)]:
            if label == 'آدرس':
                self.multi_cell(0, 10, f'{label}: {value}', 0, 'R')
            else:
                self.cell(0, 10, f'{label}: {value}', 0, 1, 'R')
        self.ln(5)

    def add_order_table(self, orders):
        self.set_font('Vazir', 'B', 12)
        self.cell(80, 10, 'کد محصول', 1, 0, 'C')
        self.cell(40, 10, 'تعداد', 1, 1, 'C')
        self.set_font('Vazir', '', 12)
        for o in orders:
            self.cell(80, 10, o['code'], 1, 0, 'C')
            self.cell(40, 10, str(o['count']), 1, 1, 'C')

app = Flask('')
@app.route('/')
def home(): return "Bot is running..."

Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()

TOKEN = '7739258515:AAEUXIZ3ySZ9xp9W31l7qr__sZkbf6qcKnE'
bot = telebot.TeleBot(TOKEN)
bot.remove_webhook()  # جلوگیری از خطای 409
user_data = {}

@bot.message_handler(commands=['start'])
def start(m):
    user_data[m.chat.id] = {'orders': [], 'step': 'code'}
    bot.send_message(m.chat.id, '🛍 خوش آمدی!\nلطفاً کد محصول را وارد کن:')

@bot.message_handler(func=lambda m: True)
def h(m):
    cid, txt = m.chat.id, m.text.strip()
    if cid not in user_data: return start(m)
    s = user_data[cid]['step']
    if s == 'code':
        user_data[cid]['current_code'], user_data[cid]['step'] = txt, 'count'
        bot.send_message(cid, '✅ تعداد؟')
    elif s == 'count':
        if not txt.isdigit(): return bot.send_message(cid, '❗ فقط عدد')
        user_data[cid]['orders'].append({'code': user_data[cid]['current_code'], 'count': int(txt)})
        user_data[cid]['step'] = 'more'
        bot.send_message(cid, 'محصول دیگه؟ بله/خیر')
    elif s == 'more':
        if txt.lower() == 'بله': user_data[cid]['step'] = 'code'; bot.send_message(cid, 'کد محصول بعدی؟')
        elif txt.lower() == 'خیر': user_data[cid]['step'] = 'name'; bot.send_message(cid, 'نام کاملت رو بگو:')
        else: bot.send_message(cid, 'بله یا خیر بنویس')
    elif s == 'name':
        user_data[cid]['name'], user_data[cid]['step'] = txt, 'phone'; bot.send_message(cid, 'شماره تماس؟')
    elif s == 'phone':
        user_data[cid]['phone'], user_data[cid]['step'] = txt, 'city'; bot.send_message(cid, 'نام شهر؟')
    elif s == 'city':
        user_data[cid]['city'], user_data[cid]['step'] = txt, 'address'; bot.send_message(cid, 'آدرس دقیق؟')
    elif s == 'address':
        user_data[cid]['address'] = txt
        data = user_data[cid]
        pdf = PDF(); pdf.add_page()
        pdf.add_customer_info(data['name'], data['phone'], data['city'], data['address'])
        pdf.add_order_table(data['orders'])
        fn = f'order_{cid}.pdf'
        pdf.output(fn)
        with open(fn, 'rb') as f: bot.send_document(cid, f)
        bot.send_message(cid, '✅ فاکتور ثبت شد.\nکانال ما: https://t.me/Halston_shop')
        os.remove(fn); user_data.pop(cid)

bot.infinity_polling()
