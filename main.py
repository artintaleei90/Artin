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
pdfmetrics.registerFont(TTFont('Vazir', "Vazirmatn-Regular.ttf"))

def reshape_text(text):
    return get_display(arabic_reshaper.reshape(text))

def create_pdf(filename, data):
    c = canvas.Canvas(filename, pagesize=A4)
    w, h = A4
    c.setFont("Vazir", 16)
    c.drawCentredString(w/2, h-2*cm, reshape_text("🧾 فاکتور سفارش"))
    c.setFont("Vazir", 12)
    y = h - 4*cm
    for info in [f"نام مشتری: {data.get('name','')}", f"شماره تماس: {data.get('phone','')}", f"شهر: {data.get('city','')}", f"آدرس: {data.get('address','')}"]:
        c.drawRightString(w-2*cm, y, reshape_text(info))
        y -= 1*cm
    y -= 0.5*cm
    orders = data.get('orders', [])
    if not orders:
        c.drawString(2*cm, y, reshape_text("هیچ محصولی ثبت نشده است."))
        c.showPage()
        c.save()
        return
    table_data = [[reshape_text(hdr) for hdr in ["کد محصول", "نام محصول", "تعداد", "قیمت واحد", "مبلغ کل"]]]
    total = 0
    for o in orders:
        sum_price = o['count'] * o['price']
        total += sum_price
        table_data.append([
            reshape_text(str(o['code'])),
            reshape_text(o['name']),
            reshape_text(str(o['count'])),
            reshape_text(str(o['price'])),
            reshape_text(str(sum_price))
        ])
    table = Table(table_data, colWidths=[3*cm,7*cm,2*cm,3*cm,3*cm])
    style = TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.lightgrey),
        ('TEXTCOLOR',(0,0),(-1,0),colors.black),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('FONTNAME',(0,0),(-1,-1),'Vazir'),
        ('FONTSIZE',(0,0),(-1,-1),10),
        ('GRID',(0,0),(-1,-1),1,colors.black),
    ])
    table.setStyle(style)
    table.wrapOn(c,w,h)
    table_height = table._height
    table.drawOn(c, 2*cm, y - table_height)
    y = y - table_height - 1*cm
    c.drawRightString(w-2*cm, y, reshape_text(f"جمع کل سفارش: {total} تومان"))
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
    chat_id = data.get('chat_id')
    if not chat_id:
        return jsonify({'status':'error','message':'chat_id ارسال نشده'}),400
    if not data.get('orders'):
        return jsonify({'status':'error','message':'سبد خرید خالی است'}),400

    filename = f"order_{chat_id}.pdf"
    create_pdf(filename, data)

    try:
        with open(filename, 'rb') as f:
            bot.send_document(chat_id=chat_id, document=f)
        return jsonify({'status':'success','message':'سفارش ثبت و فاکتور ارسال شد'})
    except Exception as e:
        return jsonify({'status':'error','message':str(e)}),500
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
    bot.send_message(msg.chat.id, "به فروشگاه پوشاک زنانه هالستون خوش آمدی 💃\nروی دکمه زیر بزن تا محصولات رو ببینی:", reply_markup=markup)

if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
