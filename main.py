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

TOKEN = '7739258515:AAEUXIZ3ySZ9xp9W31l7qr__sZkbf6qcKnE'
WEBHOOK_URL = 'https://artin-oqaq.onrender.com/webhook'

app = Flask(__name__)
bot = telebot.TeleBot(TOKEN)
FONT_PATH = "Vazirmatn-Regular.ttf"
pdfmetrics.registerFont(TTFont('Vazir', FONT_PATH))

def reshape_text(text):
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)

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
    if not orders:
        c.drawString(2*cm, y, reshape_text("هیچ محصولی ثبت نشده است."))
        c.showPage()
        c.save()
        return

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
        sum_price = count * price
        total += sum_price
        table_data.append([
            reshape_text(code),
            reshape_text(name),
            reshape_text(str(count)),
            reshape_text(str(price)),
            reshape_text(str(sum_price))
        ])

    table = Table(table_data, colWidths=[3*cm, 7*cm, 2*cm, 3*cm, 3*cm])
    style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,-1), 'Vazir'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ])
    table.setStyle(style)

    table.wrapOn(c, width, height)
    table_height = table._height
    table.drawOn(c, 2*cm, y - table_height)
    y = y - table_height - 1*cm

    c.drawRightString(width - 2*cm, y, reshape_text(f"جمع کل سفارش: {total} تومان"))
    c.showPage()
    c.save()

@app.route('/')
def home():
    return redirect('/webapp/index.html')

@app.route('/webapp/<path:path>')
def send_webapp(path):
    return send_from_directory('webapp', path)

@app.route('/webapp/order', methods=['POST'])
def handle_webapp_order():
    data = request.get_json()
    phone = data.get('phone')
    if not data.get('orders'):
        return jsonify({'status': 'error', 'message': 'سبد خرید خالی است'}), 400

    filename = f"order_{phone}.pdf"
    create_pdf(filename, data)

    try:
        with open(filename, 'rb') as f:
            bot.send_document(chat_id='@Halston_shop', document=f)
        return jsonify({'status': 'success'})
    finally:
        if os.path.exists(filename):
            os.remove(filename)

@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

@bot.message_handler(commands=['start'])
def start(msg):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("🛍 ورود به فروشگاه", web_app=WebAppInfo(url="https://artin-oqaq.onrender.com/webapp/index.html")))
    bot.send_message(msg.chat.id, "به فروشگاه پوشاک زنانه هالستون خوش اومدی 💃\nروی دکمه زیر بزن تا محصولات رو ببینی:", reply_markup=markup)

if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
