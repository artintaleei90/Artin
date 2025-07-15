import os
import telebot
from flask import Flask, request, send_from_directory, redirect
from threading import Thread
import json

from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
import arabic_reshaper
from bidi.algorithm import get_display

# ✅ توکن ربات - به صورت مستقیم داخل کد
TOKEN = '7739258515:AAEUXIZ3ySZ9xp9W31l7qr__sZkbf6qcKnE'

app = Flask(__name__, static_folder='webapp', static_url_path='')
bot = telebot.TeleBot(TOKEN)
user_data = {}

# ثبت فونت فارسی
FONT_PATH = "Vazirmatn-Regular.ttf"
if os.path.exists(FONT_PATH):
    pdfmetrics.registerFont(TTFont('Vazir', FONT_PATH))
else:
    print("⚠️ فونت فارسی پیدا نشد!")

def reshape_text(text):
    return get_display(arabic_reshaper.reshape(text))

# ساخت PDF فاکتور
def create_pdf(filename, data):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    c.setFont("Vazir", 16)
    c.drawCentredString(width / 2, height - 2 * cm, reshape_text("🧾 فاکتور سفارش"))

    y = height - 4 * cm
    c.setFont("Vazir", 12)
    info = [
        f"نام مشتری: {data['name']}",
        f"شماره تماس: {data['phone']}",
        f"شهر: {data['city']}",
        f"آدرس: {data['address']}"
    ]
    for line in info:
        c.drawRightString(width - 2 * cm, y, reshape_text(line))
        y -= 1 * cm

    y -= 0.5 * cm

    table_data = [[
        reshape_text("کد"), reshape_text("نام"), reshape_text("تعداد"),
        reshape_text("قیمت واحد"), reshape_text("جمع")
    ]]
    total = 0
    for item in data['orders']:
        sum_price = item['price'] * item['count']
        total += sum_price
        table_data.append([
            reshape_text(item['code']),
            reshape_text(item['name']),
            str(item['count']),
            str(item['price']),
            str(sum_price)
        ])

    table = Table(table_data, colWidths=[2*cm, 6*cm, 2*cm, 3*cm, 3*cm])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Vazir'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER')
    ]))
    table.wrapOn(c, width, height)
    table.drawOn(c, 2*cm, y - table._height)

    y -= table._height + 1 * cm
    c.drawRightString(width - 2 * cm, y, reshape_text(f"جمع کل: {total:,} تومان"))

    c.showPage()
    c.save()

# صفحه اصلی و فایل‌های وب‌اپ
@app.route('/')
def home():
    return redirect('/webapp/index.html')

@app.route('/webapp/<path:path>')
def serve_webapp(path):
    return send_from_directory('webapp', path)

# دریافت اطلاعات از Web App
@bot.message_handler(content_types=['web_app_data'])
def handle_webapp_data(message):
    try:
        data = json.loads(message.web_app_data.data)
        filename = f"order_{message.chat.id}.pdf"
        create_pdf(filename, data)
        with open(filename, 'rb') as f:
            bot.send_document(message.chat.id, f)
        bot.send_message(message.chat.id, "✅ فاکتور شما ارسال شد. برای نهایی‌سازی با شماره 09128883343 تماس بگیرید.")
        os.remove(filename)
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ خطا در پردازش فاکتور: {e}")

# Webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
        bot.process_new_updates([update])
        return "OK", 200
    except Exception as e:
        return f"Webhook Error: {e}", 500

# راه‌اندازی سرور Flask
def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    Thread(target=run).start()

keep_alive()

# ست کردن وبهوک روی رندر
WEBHOOK_URL = 'https://artin-oqaq.onrender.com/webhook'
bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL)
