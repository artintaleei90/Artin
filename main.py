import os, requests, zipfile, io
from flask import Flask, request
from telebot import TeleBot, types
from fpdf import FPDF

# 📦 دانلود و استخراج فونت
FONTS_URL = 'https://github.com/rastikerdar/vazirmatn/releases/download/v33.003/vazirmatn-v33.003.zip'
FONTS_DIR = 'fonts'
FONT_REGULAR = os.path.join(FONTS_DIR, 'fonts', 'ttf', 'Vazirmatn-Regular.ttf')
FONT_BOLD = os.path.join(FONTS_DIR, 'fonts', 'ttf', 'Vazirmatn-Bold.ttf')

def download_fonts():
    if not os.path.exists(FONT_REGULAR) or not os.path.exists(FONT_BOLD):
        print("📦 در حال دانلود فونت‌ها...")
        r = requests.get(FONTS_URL)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.extractall(FONTS_DIR)
        print(f"✅ فونت‌ها پیدا شدند: {FONT_REGULAR} و {FONT_BOLD}")
download_fonts()

# 📄 کلاس ساخت PDF
class PDF(FPDF):
    def header(self):
        self.set_font('Vazirmatn', '', 16)
        self.cell(0, 10, '🧾 فاکتور سفارش', ln=True, align='C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Vazirmatn', '', 10)
        self.cell(0, 10, 'مرکز پوشاک هالستون', align='C')

    def add_customer_info(self, name, phone, city, address):
        self.set_font('Vazirmatn', '', 12)
        self.cell(0, 8, f'👤 نام: {name}', ln=1, align='R')
        self.cell(0, 8, f'📱 تلفن: {phone}', ln=1, align='R')
        self.cell(0, 8, f'🏙 شهر: {city}', ln=1, align='R')
        self.multi_cell(0, 8, f'📍 آدرس: {address}', align='R')
        self.ln(5)

    def add_order_table(self, orders):
        self.set_font('Vazirmatn', 'B', 12)
        self.cell(120, 8, '🧾 کد محصول', 1, 0, 'C')
        self.cell(40, 8, '📦 تعداد', 1, 1, 'C')
        self.set_font('Vazirmatn', '', 12)
        for item in orders:
            self.cell(120, 8, item['code'], 1, 0, 'C')
            self.cell(40, 8, str(item['count']), 1, 1, 'C')

# ⚙️ تنظیمات ربات
TOKEN = '7739258515:AAEUXIZ3ySZ9xp9W31l7qr__sZkbf6qcKnE'
bot = TeleBot(TOKEN)
bot.remove_webhook()
WEBHOOK_URL = 'https://artin-um4v.onrender.com'  # ← آدرس سایتت اینجا باشه

user_data = {}

# 📥 هندلرهای پیام
@bot.message_handler(commands=['start'])
def start(msg):
    chat = msg.chat.id
    user_data[chat] = {'orders': [], 'step': 'code'}
    bot.send_message(chat, "🛍 به فروشگاه *هالستون* خوش اومدی!\n\n"
                           "📦 لطفاً *کد محصول* رو بفرست.",
                     parse_mode='Markdown')

@bot.message_handler(func=lambda m: True)
def handler(msg):
    chat = msg.chat.id
    text = msg.text.strip()
    data = user_data.get(chat, {'step': 'code', 'orders': []})
    step = data['step']

    if step == 'code':
        data['current_code'] = text
        data['step'] = 'count'
        bot.send_message(chat, "✅ تعداد این محصول چنده؟")
    elif step == 'count':
        if not text.isdigit():
            return bot.send_message(chat, "❗ فقط عدد وارد کن.")
        data['orders'].append({'code': data['current_code'], 'count': int(text)})
        data['step'] = 'more'
        bot.send_message(chat, "محصول دیگه‌ای داری؟ (بله/خیر)")
    elif step == 'more':
        if text.lower() == 'بله':
            data['step'] = 'code'
            bot.send_message(chat, "🧾 کد محصول بعدی رو بفرست:")
        elif text.lower() == 'خیر':
            data['step'] = 'name'
            bot.send_message(chat, "👤 نام کامل شما؟")
        else:
            bot.send_message(chat, "لطفاً فقط 'بله' یا 'خیر' بنویس.")
    elif step == 'name':
        data['name'] = text
        data['step'] = 'phone'
        bot.send_message(chat, "📱 شماره تماس رو وارد کن:")
    elif step == 'phone':
        data['phone'] = text
        data['step'] = 'city'
        bot.send_message(chat, "🏙 نام شهر؟")
    elif step == 'city':
        data['city'] = text
        data['step'] = 'address'
        bot.send_message(chat, "📍 آدرس دقیق؟")
    elif step == 'address':
        data['address'] = text

        pdf = PDF()
        pdf.add_font('Vazirmatn', '', FONT_REGULAR, uni=True)
        pdf.add_font('Vazirmatn', 'B', FONT_BOLD, uni=True)
        pdf.add_page()
        pdf.add_customer_info(data['name'], data['phone'], data['city'], data['address'])
        pdf.add_order_table(data['orders'])

        filename = f"invoice_{chat}.pdf"
        pdf.output(filename)
        with open(filename, 'rb') as f:
            bot.send_document(chat, f)
        os.remove(filename)

        bot.send_message(chat, "✅ فاکتور شما ثبت شد.\n📢 کانال ما: https://t.me/Halston_shop")
        user_data.pop(chat)
    user_data[chat] = data

# 🌐 اجرای وب‌سرور Flask
app = Flask(__name__)
@app.route('/', methods=['GET'])
def home():
    return '✅ Bot is running.'

@app.route('/', methods=['POST'])
def webhook():
    bot.process_new_updates([types.Update.de_json(request.stream.read().decode("utf-8"))])
    return 'OK', 200

# ست کردن Webhook
import time
time.sleep(1)
bot.set_webhook(url=WEBHOOK_URL)

# اجرای سرور
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
