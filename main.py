import os
import telebot
from flask import Flask
from threading import Thread

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

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ ربات فعال است."

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    Thread(target=run).start()

keep_alive()

bot = telebot.TeleBot(TOKEN)
user_data = {}

# ثبت فونت فارسی (مطمئن شو فایل فونت تو مسیر هست)
FONT_PATH = "Vazirmatn-Regular.ttf"
if not os.path.exists(FONT_PATH):
    print("فونت فارسی پیدا نشد! لطفا فونت Vazirmatn-Regular.ttf را در کنار فایل قرار بده.")
pdfmetrics.registerFont(TTFont('Vazir', FONT_PATH))

def reshape_text(text):
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    return bidi_text

def create_pdf(filename, data):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    c.setFont("Vazir", 16)
    title = reshape_text("🧾 فاکتور سفارش")
    c.drawCentredString(width / 2, height - 2 * cm, title)

    c.setFont("Vazir", 12)
    y = height - 4 * cm

    # اطلاعات مشتری
    customer_info = [
        f"نام مشتری: {data.get('name', '')}",
        f"شماره تماس: {data.get('phone', '')}",
        f"شهر: {data.get('city', '')}",
        f"آدرس: {data.get('address', '')}",
    ]
    for info in customer_info:
        c.drawRightString(width - 2*cm, y, reshape_text(info))
        y -= 1 * cm

    y -= 0.5 * cm

    # آماده‌سازی داده‌های جدول
    orders = data.get('orders', [])
    if not orders:
        c.drawString(2 * cm, y, reshape_text("هیچ محصولی ثبت نشده است."))
        c.showPage()
        c.save()
        return

    table_data = [[reshape_text("کد محصول"), reshape_text("تعداد")]]
    for order in orders:
        table_data.append([reshape_text(order.get('code', '')), reshape_text(str(order.get('count', '')))])

    table = Table(table_data, colWidths=[10*cm, 4*cm])

    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Vazir'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])
    table.setStyle(style)

    # رسم جدول روی canvas
    table.wrapOn(c, width, height)
    table_height = table._height
    table.drawOn(c, 2*cm, y - table_height)

    c.showPage()
    c.save()

@bot.message_handler(commands=['start'])
def start(msg):
    cid = msg.chat.id
    user_data[cid] = {'orders': [], 'step': 'code'}
    bot.send_message(cid, '🛍 خوش آمدی به ربات فروشگاه هالستون!https://t.me/Halston_shop\nلطفاً کد محصول را وارد کن:')

@bot.message_handler(func=lambda m: True)
def handle_message(msg):
    cid = msg.chat.id
    text = msg.text.strip()

    if cid not in user_data:
        user_data[cid] = {'orders': [], 'step': 'code'}

    step = user_data[cid].get('step', 'code')

    try:
        if step == 'code':
            user_data[cid]['current_code'] = text
            user_data[cid]['step'] = 'count'
            bot.send_message(cid, '📦 تعداد این محصول را وارد کن:')

        elif step == 'count':
            if not text.isdigit():
                bot.send_message(cid, '❌ لطفا فقط عدد وارد کن.')
                return
            count = int(text)
            code = user_data[cid].get('current_code')
            if code is None:
                bot.send_message(cid, '❌ خطا: کد محصول ثبت نشده است. لطفا دوباره کد را وارد کن.')
                user_data[cid]['step'] = 'code'
                return
            user_data[cid]['orders'].append({'code': code, 'count': count})
            user_data[cid]['step'] = 'more'
            bot.send_message(cid, 'محصول دیگری هم داری؟ (بله / خیر)')

        elif step == 'more':
            if text.lower() == 'بله':
                user_data[cid]['step'] = 'code'
                bot.send_message(cid, 'کد محصول بعدی را وارد کن:')
            elif text.lower() == 'خیر':
                if not user_data[cid].get('orders'):
                    bot.send_message(cid, '❌ شما هیچ محصولی ثبت نکردید، لطفا حداقل یک محصول وارد کنید.')
                    user_data[cid]['step'] = 'code'
                    return
                user_data[cid]['step'] = 'name'
                bot.send_message(cid, '📝 نام کامل خود را وارد کن:')
            else:
                bot.send_message(cid, 'لطفا فقط "بله" یا "خیر" بنویس.')

        elif step == 'name':
            user_data[cid]['name'] = text
            user_data[cid]['step'] = 'phone'
            bot.send_message(cid, '📱 شماره تماس را وارد کن:')

        elif step == 'phone':
            user_data[cid]['phone'] = text
            user_data[cid]['step'] = 'city'
            bot.send_message(cid, '🏙 شهر را وارد کن:')

        elif step == 'city':
            user_data[cid]['city'] = text
            user_data[cid]['step'] = 'address'
            bot.send_message(cid, '📍 آدرس را وارد کن:')

        elif step == 'address':
            user_data[cid]['address'] = text
            data = user_data[cid]

            filename = f'order_{cid}.pdf'
            try:
                create_pdf(filename, data)
                with open(filename, 'rb') as f:
                    bot.send_document(cid, f)
                bot.send_message(cid, '✅ فاکتور شما ارسال شد. ممنون از خرید شما 🙏')
            except Exception as e:
                bot.send_message(cid, f'❌ خطا در ساخت یا ارسال فاکتور: {e}')
            finally:
                if os.path.exists(filename):
                    os.remove(filename)
                user_data.pop(cid, None)
    except Exception as e:
        bot.send_message(cid, f'❌ خطایی رخ داد: {e}')

bot.remove_webhook()
bot.infinity_polling()
