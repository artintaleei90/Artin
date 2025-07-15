import os
from flask import Flask, request, redirect, send_from_directory
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

TOKEN = '7739258515:AAEUXIZ3ySZ9xp9W31l7qr__sZkbf6qcKnE'
WEBHOOK_URL = 'https://artin-oqaq.onrender.com/webhook'

app = Flask(__name__)
bot = telebot.TeleBot(TOKEN)

# محصولات نمونه (کوتاه کردم برای مثال)
products = {
    "3390": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 697000},
    "1107": {"name": "فری سایز - پک 6 عددی رنگ: سفید و مشکی", "price": 547000},
    # ... بقیه محصولات اینجا ...
}

user_data = {}

FONT_PATH = "Vazirmatn-Regular.ttf"
pdfmetrics.registerFont(TTFont('Vazir', FONT_PATH))

def reshape_text(text):
    reshaped = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped)
    return bidi_text

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

    from reportlab.platypus import Table, TableStyle
    from reportlab.lib import colors

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

@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

@bot.message_handler(commands=['start'])
def start(msg):
    cid = msg.chat.id
    user_data[cid] = {'orders': [], 'step': 'code'}
    bot.send_message(cid, '🛍 خوش آمدی به ربات فروشگاه هالستون! لطفا کد محصول را وارد کن:')

@bot.message_handler(func=lambda m: True)
def handle_message(msg):
    cid = msg.chat.id
    text = msg.text.strip()
    if cid not in user_data:
        user_data[cid] = {'orders': [], 'step': 'code'}
    step = user_data[cid].get('step', 'code')

    try:
        if step == 'code':
            if text not in products:
                bot.send_message(cid, '❌ کد محصول موجود نیست، دوباره وارد کن.')
                return
            prod = products[text]
            user_data[cid]['current_code'] = text
            user_data[cid]['current_name'] = prod['name']
            user_data[cid]['current_price'] = prod['price']
            user_data[cid]['step'] = 'count'
            bot.send_message(cid, f"محصول: {prod['name']}\nقیمت: {prod['price']} تومان\nتعداد را وارد کن:")

        elif step == 'count':
            if not text.isdigit():
                bot.send_message(cid, '❌ لطفا فقط عدد وارد کن.')
                return
            count = int(text)
            user_data[cid]['orders'].append({
                'code': user_data[cid]['current_code'],
                'name': user_data[cid]['current_name'],
                'price': user_data[cid]['current_price'],
                'count': count
            })
            user_data[cid]['step'] = 'more'
            bot.send_message(cid, 'محصول دیگری داری؟ (بله / خیر)')

        elif step == 'more':
            if text == 'بله':
                user_data[cid]['step'] = 'code'
                bot.send_message(cid, 'کد محصول بعدی را وارد کن:')
            elif text == 'خیر':
                if not user_data[cid]['orders']:
                    bot.send_message(cid, '❌ شما هیچ محصولی انتخاب نکردید.')
                    user_data[cid]['step'] = 'code'
                    return
                user_data[cid]['step'] = 'name'
                bot.send_message(cid, 'نام کامل خود را وارد کن:')
            else:
                bot.send_message(cid, 'لطفا فقط "بله" یا "خیر" بنویس.')

        elif step == 'name':
            user_data[cid]['name'] = text
            user_data[cid]['step'] = 'phone'
            bot.send_message(cid, 'شماره تماس را وارد کن:')

        elif step == 'phone':
            user_data[cid]['phone'] = text
            user_data[cid]['step'] = 'city'
            bot.send_message(cid, 'شهر را وارد کن:')

        elif step == 'city':
            user_data[cid]['city'] = text
            user_data[cid]['step'] = 'address'
            bot.send_message(cid, 'آدرس را وارد کن:')

        elif step == 'address':
            user_data[cid]['address'] = text
            filename = f'order_{cid}.pdf'
            create_pdf(filename, user_data[cid])
            with open(filename, 'rb') as f:
                bot.send_document(cid, f)
            os.remove(filename)
            bot.send_message(cid, '✅ فاکتور ارسال شد. ممنون از خرید شما!')
            user_data.pop(cid, None)

    except Exception as e:
        bot.send_message(cid, f'❌ خطا: {e}')

if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
