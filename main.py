import os
import telebot
import requests
import zipfile
import io
from fpdf import FPDF
from flask import Flask, request

# تنظیمات اولیه
TOKEN = '7739258515:AAEUXIZ3ySZ9xp9W31l7qr__sZkbf6qcKnE'
WEBHOOK_URL = f'https://artin-um4v.onrender.com/{TOKEN}'
CHANNEL_LINK = 'https://t.me/Halston_shop'

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
user_data = {}

# دانلود و استخراج فونت فارسی اگر وجود نداشت
FONTS_ZIP_URL = 'https://github.com/rastikerdar/vazirmatn/releases/download/v33.003/vazirmatn-v33.003.zip'
FONTS_DIR = 'fonts'
FONT_REGULAR = os.path.join(FONTS_DIR, 'fonts', 'ttf', 'Vazirmatn-Regular.ttf')
FONT_BOLD = os.path.join(FONTS_DIR, 'fonts', 'ttf', 'Vazirmatn-Bold.ttf')

def download_fonts():
    if not os.path.isfile(FONT_REGULAR) or not os.path.isfile(FONT_BOLD):
        print("📦 در حال دانلود فونت...")
        r = requests.get(FONTS_ZIP_URL)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.extractall(FONTS_DIR)
        print("✅ فونت استخراج شد.")
    else:
        print("✅ فونت‌ها قبلاً دانلود شده‌اند.")

download_fonts()

# کلاس ساخت PDF با فونت فارسی
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

# هندلر وب‌هوک تلگرام روی مسیر توکن
@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return 'ok', 200

# صفحه اصلی فقط تست سلامت سرور
@app.route('/', methods=['GET'])
def index():
    return "🤖 ربات فروشگاه هالستون فعال است."

# هندلرهای تلگرام
@bot.message_handler(commands=['start'])
def start(msg):
    chat = msg.chat.id
    user_data[chat] = {'orders': [], 'step': 'code'}
    bot.send_message(chat,
        f'🛍 خوش آمدید به ربات فروشگاه هالستون!\n\n'
        f'برای شروع:\nلطفاً *کد محصول* را ارسال کنید.\n\n🌐 کانال ما: {CHANNEL_LINK}',
        parse_mode='Markdown')

@bot.message_handler(func=lambda m: True)
def handle_message(m):
    chat = m.chat.id
    txt = m.text.strip()
    if chat not in user_data:
        return start(m)
    step = user_data[chat]['step']

    if step == 'code':
        user_data[chat]['current_code'] = txt
        user_data[chat]['step'] = 'count'
        bot.send_message(chat, '✅ *تعداد* را وارد کن:', parse_mode='Markdown')

    elif step == 'count':
        if not txt.isdigit():
            return bot.send_message(chat, '❗ لطفاً فقط عدد وارد کن.')
        user_data[chat]['orders'].append({'code': user_data[chat]['current_code'], 'count': int(txt)})
        user_data[chat]['step'] = 'more'
        bot.send_message(chat, 'محصول دیگه‌ای داری؟ (بله/خیر)')

    elif step == 'more':
        if txt.lower() == 'بله':
            user_data[chat]['step'] = 'code'
            bot.send_message(chat, 'کد محصول بعدی را ارسال کن:')
        elif txt.lower() == 'خیر':
            user_data[chat]['step'] = 'name'
            bot.send_message(chat, '📝 لطفاً نام کامل را وارد کن:')
        else:
            bot.send_message(chat, 'لطفاً فقط *بله* یا *خیر* بنویس.', parse_mode='Markdown')

    elif step == 'name':
        user_data[chat]['name'] = txt
        user_data[chat]['step'] = 'phone'
        bot.send_message(chat, '📱 شماره تماس را وارد کن:')

    elif step == 'phone':
        user_data[chat]['phone'] = txt
        user_data[chat]['step'] = 'city'
        bot.send_message(chat, '🏙 نام شهر را وارد کن:')

    elif step == 'city':
        user_data[chat]['city'] = txt
        user_data[chat]['step'] = 'address'
        bot.send_message(chat, '📍 آدرس دقیق را وارد کن:')

    elif step == 'address':
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
        bot.send_message(chat, f'✅ فاکتور شما ثبت شد!\n🌐 کانال ما: {CHANNEL_LINK}')
        os.remove(fn)
        user_data.pop(chat)

# پاک کردن وب‌هوک قبلی و ست کردن وب‌هوک جدید
bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL)

# اجرای اپلیکیشن
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host="0.0.0.0", port=port)
