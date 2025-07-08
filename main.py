import os, telebot, requests, zipfile, io
from flask import Flask, request
from fpdf import FPDF

# تنظیمات اولیه
TOKEN = '7739258515:AAEUXIZ3ySZ9xp9W31l7qr__sZkbf6qcKnE'
CHANNEL_LINK = 'https://t.me/Halston_shop'
API_URL = f"https://api.telegram.org/bot{TOKEN}"
WEBHOOK_URL = 'https://artin-um4v.onrender.com/'  # آدرس وب‌هوک شما در Render

bot = telebot.TeleBot(TOKEN)

# 📥 دانلود فونت فارسی
FONTS_DIR = 'fonts'
FONT_PATH = os.path.join(FONTS_DIR, 'fonts', 'ttf', 'Vazirmatn-Regular.ttf')
FONT_BOLD_PATH = os.path.join(FONTS_DIR, 'fonts', 'ttf', 'Vazirmatn-Bold.ttf')
FONTS_ZIP_URL = 'https://github.com/rastikerdar/vazirmatn/releases/download/v33.003/vazirmatn-v33.003.zip'

def download_fonts():
    if not os.path.exists(FONT_PATH) or not os.path.exists(FONT_BOLD_PATH):
        print("📦 دانلود فونت‌ها...")
        r = requests.get(FONTS_ZIP_URL)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.extractall(FONTS_DIR)
        print("✅ فونت‌ها دانلود و استخراج شدند.")
    else:
        print("✅ فونت‌ها قبلاً موجودند.")

download_fonts()

# 💾 حافظه موقت کاربران
user_data = {}

# 🧾 ساخت PDF
class PDF(FPDF):
    def header(self):
        self.add_font('Vazirmatn', '', FONT_PATH, uni=True)
        self.set_font('Vazirmatn', '', 16)
        self.cell(0, 10, '🧾 فاکتور سفارش', ln=1, align='C')
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
        self.set_font('Vazirmatn', '', 12)
        self.cell(120, 8, 'کد محصول', border=1, align='C')
        self.cell(40, 8, 'تعداد', border=1, ln=1, align='C')
        for o in orders:
            self.cell(120, 8, o['code'], border=1, align='C')
            self.cell(40, 8, str(o['count']), border=1, ln=1, align='C')

# ✉️ شروع ربات
@bot.message_handler(commands=['start'])
def send_welcome(m):
    chat = m.chat.id
    user_data[chat] = {'orders': [], 'step': 'code'}
    bot.send_message(chat, f"🛍 خوش آمدید به ربات فروشگاه هالستون!\n\nلطفاً *کد محصول* را ارسال کنید.", parse_mode='Markdown')

@bot.message_handler(func=lambda m: True)
def handle(m):
    chat = m.chat.id
    text = m.text.strip()
    if chat not in user_data:
        return send_welcome(m)
    step = user_data[chat]['step']

    if step == 'code':
        user_data[chat]['current_code'] = text
        user_data[chat]['step'] = 'count'
        bot.send_message(chat, '📦 تعداد را وارد کن:')
    elif step == 'count':
        if not text.isdigit():
            return bot.send_message(chat, '❌ فقط عدد وارد کن!')
        user_data[chat]['orders'].append({'code': user_data[chat]['current_code'], 'count': int(text)})
        user_data[chat]['step'] = 'more'
        bot.send_message(chat, 'محصول دیگه‌ای داری؟ (بله/خیر)')
    elif step == 'more':
        if text.lower() == 'بله':
            user_data[chat]['step'] = 'code'
            bot.send_message(chat, 'کد محصول را وارد کن:')
        elif text.lower() == 'خیر':
            user_data[chat]['step'] = 'name'
            bot.send_message(chat, 'نام کامل مشتری:')
        else:
            bot.send_message(chat, '❗ لطفاً "بله" یا "خیر" بنویس.')
    elif step == 'name':
        user_data[chat]['name'] = text
        user_data[chat]['step'] = 'phone'
        bot.send_message(chat, 'شماره تماس:')
    elif step == 'phone':
        user_data[chat]['phone'] = text
        user_data[chat]['step'] = 'city'
        bot.send_message(chat, 'شهر:')
    elif step == 'city':
        user_data[chat]['city'] = text
        user_data[chat]['step'] = 'address'
        bot.send_message(chat, 'آدرس کامل:')
    elif step == 'address':
        user_data[chat]['address'] = text
        d = user_data[chat]
        pdf = PDF()
        pdf.add_page()
        pdf.add_customer_info(d['name'], d['phone'], d['city'], d['address'])
        pdf.add_order_table(d['orders'])
        filename = f"order_{chat}.pdf"
        pdf.output(filename)
        with open(filename, 'rb') as f:
            bot.send_document(chat, f)
        bot.send_message(chat, '✅ فاکتور ارسال شد.\n🌐 ' + CHANNEL_LINK)
        os.remove(filename)
        user_data.pop(chat)

# ⚙️ Flask app برای Webhook
app = Flask(__name__)

@app.route('/', methods=['GET'])
def root(): return 'Bot is live!'

@app.route('/', methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
    bot.process_new_updates([update])
    return 'OK', 200

# ثبت وب‌هوک
bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL)

# اجرای سرور Flask
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
