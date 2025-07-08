import os
import telebot
import requests
import zipfile
import io
from fpdf import FPDF
from flask import Flask, request, abort

TOKEN = '7739258515:AAEUXIZ3ySZ9xp9W31l7qr__sZkbf6qcKnE'
WEBHOOK_URL = f'https://artin-d8qn.onrender.com/{TOKEN}'
CHANNEL_LINK = 'https://t.me/Halston_shop'

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
user_data = {}

# فونت‌ها
FONTS_ZIP_URL = 'https://github.com/rastikerdar/vazirmatn/releases/download/v33.003/vazirmatn-v33.003.zip'
FONTS_DIR = 'fonts'
FONT_REGULAR = os.path.join(FONTS_DIR, 'fonts', 'ttf', 'Vazirmatn-Regular.ttf')
FONT_BOLD = os.path.join(FONTS_DIR, 'fonts', 'ttf', 'Vazirmatn-Bold.ttf')

def download_fonts():
    if not os.path.exists(FONT_REGULAR):
        print("در حال دانلود فونت‌ها...")
        r = requests.get(FONTS_ZIP_URL)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.extractall(FONTS_DIR)
        print("فونت‌ها استخراج شدند.")

download_fonts()

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font('Vazir', '', FONT_REGULAR, uni=True)
        self.add_font('Vazir', 'B', FONT_BOLD, uni=True)

    def header(self):
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
    if request.headers.get('content-type') == 'application/json':
        json_str = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
        return '', 200
    else:
        abort(403)

@app.route('/', methods=['GET'])
def index():
    return '🤖 ربات فروشگاه هالستون فعال است.'

@bot.message_handler(commands=['start'])
def start_handler(message):
    chat_id = message.chat.id
    user_data[chat_id] = {'orders': [], 'step': 'code'}
    bot.send_message(chat_id,
        f'🛍 خوش آمدید به ربات فروشگاه هالستون!\n\n'
        f'برای شروع:\nلطفاً *کد محصول* را ارسال کنید.\n\n🌐 کانال ما: {CHANNEL_LINK}',
        parse_mode='Markdown')

@bot.message_handler(func=lambda m: True)
def message_handler(message):
    chat_id = message.chat.id
    text = message.text.strip()

    if chat_id not in user_data:
        start_handler(message)
        return

    step = user_data[chat_id]['step']

    if step == 'code':
        user_data[chat_id]['current_code'] = text
        user_data[chat_id]['step'] = 'count'
        bot.send_message(chat_id, '✅ لطفاً *تعداد* را وارد کنید:', parse_mode='Markdown')

    elif step == 'count':
        if not text.isdigit():
            bot.send_message(chat_id, '❗ لطفاً فقط عدد وارد کنید.')
            return
        user_data[chat_id]['orders'].append({'code': user_data[chat_id]['current_code'], 'count': int(text)})
        user_data[chat_id]['step'] = 'more'
        bot.send_message(chat_id, 'محصول دیگری دارید؟ (بله/خیر)')

    elif step == 'more':
        if text.lower() == 'بله':
            user_data[chat_id]['step'] = 'code'
            bot.send_message(chat_id, 'کد محصول بعدی را ارسال کنید:')
        elif text.lower() == 'خیر':
            user_data[chat_id]['step'] = 'name'
            bot.send_message(chat_id, '📝 لطفاً نام کامل خود را وارد کنید:')
        else:
            bot.send_message(chat_id, 'لطفاً فقط *بله* یا *خیر* بنویسید.', parse_mode='Markdown')

    elif step == 'name':
        user_data[chat_id]['name'] = text
        user_data[chat_id]['step'] = 'phone'
        bot.send_message(chat_id, '📱 شماره تماس خود را وارد کنید:')

    elif step == 'phone':
        user_data[chat_id]['phone'] = text
        user_data[chat_id]['step'] = 'city'
        bot.send_message(chat_id, '🏙 نام شهر خود را وارد کنید:')

    elif step == 'city':
        user_data[chat_id]['city'] = text
        user_data[chat_id]['step'] = 'address'
        bot.send_message(chat_id, '📍 آدرس دقیق خود را وارد کنید:')

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

        os.remove(filename)
        bot.send_message(chat_id, f'✅ فاکتور شما ثبت شد!\n🌐 کانال ما: {CHANNEL_LINK}')
        user_data.pop(chat_id)

def set_webhook():
    info = bot.get_webhook_info()
    if info.url != WEBHOOK_URL:
        print("حذف وب‌هوک قبلی...")
        bot.remove_webhook()
        print(f"ست کردن وب‌هوک به: {WEBHOOK_URL}")
        success = bot.set_webhook(url=WEBHOOK_URL)
        if success:
            print("وب‌هوک با موفقیت ست شد.")
        else:
            print("خطا در ست کردن وب‌هوک!")
    else:
        print("وب‌هوک قبلی فعال است.")

if __name__ == "__main__":
    set_webhook()
    port = int(os.environ.get('PORT', 10000))
    print(f"سرور روی پورت {port} اجرا شد.")
    app.run(host="0.0.0.0", port=port)
