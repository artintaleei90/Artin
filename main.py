import os
from flask import Flask, request, redirect, send_from_directory, jsonify
import telebot
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
import arabic_reshaper
from bidi.algorithm import get_display
from telebot.types import WebAppInfo, KeyboardButton, ReplyKeyboardMarkup

# تنظیمات
TOKEN = '7739258515:AAEUXIZ3ySZ9xp9W31l7qr__sZkbf6qcKnE'
WEBHOOK_URL = 'https://artin-oqaq.onrender.com/webhook'
FONT_PATH = "Vazirmatn-Regular.ttf"
CHANNEL = '@Halston_shop'  # یا chat_id کاربر

# راه‌اندازی
app = Flask(__name__)
bot = telebot.TeleBot(TOKEN)

# فونت فارسی
try:
    pdfmetrics.registerFont(TTFont('Vazir', FONT_PATH))
except Exception as e:
    print(f"❌ خطا در بارگذاری فونت: {e}")

# تابع فارسی‌سازی متن
def reshape_text(text):
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)

# ساخت فایل PDF سفارش
def create_pdf(filename, data):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    c.setFont("Vazir", 16)
    c.drawCentredString(width / 2, height - 2*cm, reshape_text("🧾 فاکتور سفارش"))

    c.setFont("Vazir", 12)
    y = height - 4*cm
    customer_info = [
        f"نام مشتری: {data.get('name', '')}",
        f"شماره تماس: {data.get('phone', '')}",
        f"شهر: {data.get('city', '')}",
        f"آدرس: {data.get('address', '')}",
    ]
    for info in customer_info:
        c.drawRightString(width - 2*cm, y, reshape_text(info))
        y -= 1*cm

    y -= 0.5*cm
    orders = data.get('orders', [])
    table_data = [[
        reshape_text("کد محصول"),
        reshape_text("نام محصول"),
        reshape_text("تعداد"),
        reshape_text("قیمت واحد"),
        reshape_text("مبلغ کل")
    ]]
    total = 0
    for order in orders:
        code = order['code']
        name = order['name']
        count = order['count']
        price = order['price']
        total_price = count * price
        total += total_price
        table_data.append([
            reshape_text(code),
            reshape_text(name),
            reshape_text(str(count)),
            reshape_text(str(price)),
            reshape_text(str(total_price))
        ])
    table = Table(table_data, colWidths=[3*cm, 7*cm, 2*cm, 3*cm, 3*cm])
    style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('FONTNAME', (0,0), (-1,-1), 'Vazir'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'CENTER')
    ])
    table.setStyle(style)
    table.wrapOn(c, width, height)
    table.drawOn(c, 2*cm, y - table._height)
    y = y - table._height - 1*cm
    c.drawRightString(width - 2*cm, y, reshape_text(f"جمع کل سفارش: {total:,} تومان"))
    c.showPage()
    c.save()

# نمایش مینی‌اپ
@app.route('/')
def home():
    return redirect('/webapp/index.html')

@app.route('/webapp/<path:path>')
def webapp_static(path):
    return send_from_directory('webapp', path)

# دریافت سفارش از WebApp
@app.route('/webapp/order', methods=['POST'])
def handle_order():
    try:
        data = request.get_json()
        if not data or not data.get('orders'):
            print("❌ سفارش نامعتبر یا خالی.")
            return jsonify({'status': 'error', 'message': 'سفارش خالی است'}), 400
        
        filename = f"order_{data.get('phone', 'no_phone')}.pdf"
        create_pdf(filename, data)

        with open(filename, 'rb') as f:
            bot.send_document(chat_id=CHANNEL, document=f, caption="📥 سفارش جدید ثبت شد!")

        os.remove(filename)
        return jsonify({'status': 'success'}), 200

    except Exception as e:
        print(f"❌ خطا در ثبت سفارش: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# وب‌هوک تلگرام
@app.route('/webhook', methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

# /start => دکمه ورود به فروشگاه
@bot.message_handler(commands=['start'])
def handle_start(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("🛍 ورود به فروشگاه", web_app=WebAppInfo(url="https://artin-oqaq.onrender.com/webapp/index.html")))
    bot.send_message(message.chat.id, "به فروشگاه پوشاک زنانه هالستون خوش اومدی 💃", reply_markup=markup)

# اجرای سرور
if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
