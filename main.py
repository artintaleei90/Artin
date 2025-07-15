‏import os
‏import telebot
‏from flask import Flask
‏from threading import Thread

‏from reportlab.pdfgen import canvas
‏from reportlab.pdfbase.ttfonts import TTFont
‏from reportlab.pdfbase import pdfmetrics
‏from reportlab.lib.pagesizes import A4
‏from reportlab.lib.units import cm
‏from reportlab.platypus import Table, TableStyle
‏from reportlab.lib import colors

‏import arabic_reshaper
‏from bidi.algorithm import get_display

‏TOKEN = '7739258515:AAEUXIZ3ySZ9xp9W31l7qr__sZkbf6qcKnE'

‏app = Flask(__name__)

‏@app.route('/')
‏def home():
‏    return "✅ ربات فعال است."

‏def run():
‏    app.run(host='0.0.0.0', port=8080)

‏def keep_alive():
‏    Thread(target=run).start()

‏keep_alive()

‏bot = telebot.TeleBot(TOKEN)
‏user_data = {}

‏products = {
‏    "3390": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 697000, "unit": "هزار تومان"},
‏    "1107": {"name": "فری سایز - پک 6 عددی رنگ: سفید و مشکی", "price": 547000, "unit": "هزار تومان"},
‏    "1303": {"name": "فری سایز - پک 4 عددی رنگ: در تصویر به جز سبز", "price": 747000, "unit": "هزار تومان"},
‏    "3389": {"name": "فری سایز - پک 4 عددی رنگ: در تصویر (مانتو کتی)", "price": 797000, "unit": "هزار تومان"},
‏    "1106": {"name": "فری سایز - دو طرح رنگ: در تصویر", "price": 397000, "unit": "هزار تومان"},
‏    "1203": {"name": "فری سایز - پک 6 عددی رنگ: سفید", "price": 547000, "unit": "هزار تومان"},
‏    "1213": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 497000, "unit": "هزار تومان"},
‏    "3392": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر (کرم و مشکی)", "price": 597000, "unit": "هزار تومان"},
‏    "3357": {"name": "فری سایز - پک 5 عددی رنگ: در تصویر", "price": 427000, "unit": "هزار تومان"},
‏    "1108": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 647000, "unit": "هزار تومان"},
‏    "3346": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 597000, "unit": "هزار تومان"},
‏    "1204": {"name": "فری سایز - پک 5 عددی رنگ: در تصویر", "price": 597000, "unit": "هزار تومان"},
‏    "3340": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 567000, "unit": "هزار تومان"},
‏    "1114": {"name": "فری سایز - پک 7 عددی رنگ: در تصویر (PERRY ترک)", "price": 637000, "unit": "هزار تومان"},
‏    "1102": {"name": "فری سایز - پک 5 عددی رنگ: در تصویر", "price": 397000, "unit": "هزار تومان"},
‏    "1301": {"name": "فری سایز - پک 4 عددی رنگ: در تصویر", "price": 597000, "unit": "هزار تومان"},
‏    "3377": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 597000, "unit": "هزار تومان"},
‏    "3759": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 347000, "unit": "هزار تومان"},
‏    "1117": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 697000, "unit": "هزار تومان"},
‏    "3395": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 757000, "unit": "هزار تومان"},
‏    "3364": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 457000, "unit": "هزار تومان"},
‏    "1201": {"name": "فری سایز - پک 4 عددی رنگ: کرم", "price": 797000, "unit": "هزار تومان"},
‏    "3383": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 657000, "unit": "هزار تومان"},
‏    "1202": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 737000, "unit": "هزار تومان"},
‏    "1211": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 567000, "unit": "هزار تومان"},
‏    "3345": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 597000, "unit": "هزار تومان"},
‏    "3752": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 347000, "unit": "هزار تومان"},
‏    "3356": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 697000, "unit": "هزار تومان"},
‏    "1209": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 497000, "unit": "هزار تومان"},
‏    "1208": {"name": "فری سایز - پک 7 عددی رنگ: در تصویر", "price": 397000, "unit": "هزار تومان"},
‏    "1305": {"name": "فری سایز - پک 4 عددی رنگ: فقط گل قرمز", "price": 517000, "unit": "هزار تومان"},
‏    "3353": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 417000, "unit": "هزار تومان"},
‏    "1210": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 657000, "unit": "هزار تومان"},
‏    "3370": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 697000, "unit": "هزار تومان"},
‏    "1302": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر با سفید و مشکی دوبل", "price": 497000, "unit": "هزار تومان"},
‏    "3325": {"name": "فری سایز - پک 4 عددی رنگ: در تصویر", "price": 497000, "unit": "هزار تومان"},
‏    "3781": {"name": "فری سایز - پک 4 عددی رنگ: مشکی", "price": 397000, "unit": "هزار تومان"},
‏    "3341": {"name": "فری سایز - پک 6 عددی رنگ: مشکی", "price": 637000, "unit": "هزار تومان"},
‏    "3379": {"name": "فری سایز - پک 4 عددی رنگ: در تصویر", "price": 697000, "unit": "هزار تومان"},
‏    "1105": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 737000, "unit": "هزار تومان"},
‏    "3381": {"name": "فری سایز - پک 4 عددی رنگ: در تصویر (قلاب بافی سبک)", "price": 597000, "unit": "هزار تومان"},
‏    "3762": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر (جنس پارچه در تصویر رنگبندی)", "price": 697000, "unit": "هزار تومان"},
‏    "3384": {"name": "فری سایز - پک 6 عددی رنگ: مشکی سبز طوسی", "price": 647000, "unit": "هزار تومان"},
‏    "1111": {"name": "فری سایز - پک 5 عددی رنگ: در تصویر", "price": 797000, "unit": "هزار تومان"},
‏    "1306": {"name": "فری سایز - پک 5 عددی رنگ: در تصویر", "price": 597000, "unit": "هزار تومان"},
‏    "3329": {"name": "فری سایز - پک 5 عددی رنگ: سه رنگ با سفید مشکی دوبل", "price": 557000, "unit": "هزار تومان"},
‏    "3791": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 597000, "unit": "هزار تومان"},
‏    "3348": {"name": "فری سایز - پک 8 عددی رنگ: در تصویر", "price": 297000, "unit": "هزار تومان"},
‏    "3494": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 497000, "unit": "هزار تومان"},
‏    "3394": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 957000, "unit": "هزار تومان"},
‏    "1116": {"name": "فری سایز - پک 4 عددی رنگ: در تصویر", "price": 647000, "unit": "هزار تومان"},
‏    "1112": {"name": "فری سایز - پک 4 عددی رنگ: در تصویر", "price": 597000, "unit": "هزار تومان"},
‏    "3393": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 597000, "unit": "هزار تومان"},
‏    "1115": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 547000, "unit": "هزار تومان"},
‏    "1118": {"name": "فری سایز - پک 4 عددی رنگ: در تصویر", "price": 697000, "unit": "هزار تومان"},

    }


‏FONT_PATH = "Vazirmatn-Regular.ttf"
‏if not os.path.exists(FONT_PATH):
‏    print("فونت فارسی پیدا نشد! لطفا فونت Vazirmatn-Regular.ttf را در کنار فایل قرار بده.")
‏pdfmetrics.registerFont(TTFont('Vazir', FONT_PATH))

‏def reshape_text(text):
‏    reshaped_text = arabic_reshaper.reshape(text)
‏    bidi_text = get_display(reshaped_text)
‏    return bidi_text

‏def create_pdf(filename, data):
‏    c = canvas.Canvas(filename, pagesize=A4)
‏    width, height = A4

‏    c.setFont("Vazir", 16)
‏    title = reshape_text("🧾 فاکتور سفارش")
‏    c.drawCentredString(width / 2, height - 2 * cm, title)

‏    c.setFont("Vazir", 12)
‏    y = height - 4 * cm

‏    customer_info = [
‏        f"نام مشتری: {data.get('name', '')}",
‏        f"شماره تماس: {data.get('phone', '')}",
‏        f"شهر: {data.get('city', '')}",
‏        f"آدرس: {data.get('address', '')}",
    ]
‏    for info in customer_info:
‏        c.drawRightString(width - 2*cm, y, reshape_text(info))
‏        y -= 1 * cm

‏    y -= 0.5 * cm

‏    orders = data.get('orders', [])
‏    if not orders:
‏        c.drawString(2 * cm, y, reshape_text("هیچ محصولی ثبت نشده است."))
‏        c.showPage()
‏        c.save()
‏        return

‏    table_data = [
        [
‏            reshape_text("کد محصول"),
‏            reshape_text("نام محصول"),
‏            reshape_text("تعداد"),
‏            reshape_text("قیمت واحد"),
‏            reshape_text("مبلغ کل")
        ]
    ]
‏    total_price = 0
‏    for order in orders:
‏        code = order.get('code', '')
‏        name = order.get('name', '')
‏        count = order.get('count', 0)
‏        price = order.get('price', 0)
‏        sum_price = count * price
‏        total_price += sum_price
‏        table_data.append([
‏            reshape_text(code),
‏            reshape_text(name),
‏            reshape_text(str(count)),
‏            reshape_text(str(price)),
‏            reshape_text(str(sum_price))
        ])

‏    table = Table(table_data, colWidths=[3*cm, 7*cm, 2*cm, 3*cm, 3*cm])

‏    style = TableStyle([
‏        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
‏        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
‏        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
‏        ('FONTNAME', (0, 0), (-1, -1), 'Vazir'),
‏        ('FONTSIZE', (0, 0), (-1, -1), 10),
‏        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
‏        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])
‏    table.setStyle(style)

‏    table.wrapOn(c, width, height)
‏    table_height = table._height
‏    table.drawOn(c, 2*cm, y - table_height)

‏    y = y - table_height - 1*cm
‏    c.setFont("Vazir", 12)
‏    c.drawRightString(width - 2*cm, y, reshape_text(f"جمع کل سفارش: {total_price} تومان"))

‏    y -= 1.5 * cm
‏    bank_text = [
        "💳بانک سامان - آزیتا فتوحی مظفرنژاد",
        "6219-8610-6509-3089",
‏        "IR440560083280078294010001",
        "",
        "👈🏼 واریز وجه تنها به شماره کارت های دریافتی از شماره تماس 09128883343 دارای اعتبار می باشد.",
        "",
        "📣 همکار گرامی تنها پس از تایید وجه در بانک مقصد، امکان خروجی از انبار میسر است.",
        "",
        "🛑لذا خواهشمندیم نسبت به انتقال وجه به صورت کارت به کارت، شبا، پایا ... توجه فرمایید."
    ]
‏    for line in bank_text:
‏        c.drawRightString(width - 2*cm, y, reshape_text(line))
‏        y -= 0.8 * cm

‏    c.showPage()
‏    c.save()

‏@bot.message_handler(commands=['start'])
‏def start(msg):
‏    cid = msg.chat.id
‏    user_data[cid] = {'orders': [], 'step': 'code'}
‏    bot.send_message(cid, '🛍 خوش آمدی به ربات فروشگاه هالستون! https://t.me/Halston_shop\nلطفاً کد محصول را وارد کن(به انگلیسی):')

‏@bot.message_handler(func=lambda m: True)
‏def handle_message(msg):
‏    cid = msg.chat.id
‏    text = msg.text.strip()

‏    if cid not in user_data:
‏        user_data[cid] = {'orders': [], 'step': 'code'}

‏    step = user_data[cid].get('step', 'code')

‏    try:
‏        if step == 'code':
‏            if text not in products:
‏                bot.send_message(cid, '❌ کد محصول وارد شده موجود نیست. لطفا کد صحیح را وارد کن.')
‏                return
‏            product_info = products[text]
‏            user_data[cid]['current_code'] = text
‏            user_data[cid]['current_name'] = product_info['name']
‏            user_data[cid]['current_price'] = product_info['price']
‏            user_data[cid]['step'] = 'count'
‏            bot.send_message(cid, f"محصول انتخاب شده:\n{product_info['name']}\nقیمت واحد: {product_info['price']} تومان\n\nلطفاً تعداد را وارد کن:")

‏        elif step == 'count':
‏            if not text.isdigit():
‏                bot.send_message(cid, '❌ لطفا فقط عدد وارد کن.')
‏                return
‏            count = int(text)
‏            code = user_data[cid].get('current_code')
‏            name = user_data[cid].get('current_name')
‏            price = user_data[cid].get('current_price')
‏            if code is None:
‏                bot.send_message(cid, '❌ خطا: کد محصول ثبت نشده است. لطفا دوباره کد را وارد کن.')
‏                user_data[cid]['step'] = 'code'
‏                return
‏            user_data[cid]['orders'].append({
‏                'code': code,
‏                'name': name,
‏                'price': price,
‏                'count': count
            })
‏            user_data[cid]['step'] = 'more'
‏            bot.send_message(cid, 'محصول دیگری هم داری؟ (بله / خیر)')

‏        elif step == 'more':
‏            if text.lower() == 'بله':
‏                user_data[cid]['step'] = 'code'
‏                bot.send_message(cid, 'کد محصول بعدی را وارد کن:')
‏            elif text.lower() == 'خیر':
‏                if not user_data[cid].get('orders'):
‏                    bot.send_message(cid, '❌ شما هیچ محصولی ثبت نکردید، لطفا حداقل یک محصول وارد کنید.')
‏                    user_data[cid]['step'] = 'code'
‏                    return
‏                user_data[cid]['step'] = 'name'
‏                bot.send_message(cid, '📝 نام کامل خود را وارد کن:')
‏            else:
‏                bot.send_message(cid, 'لطفا فقط "بله" یا "خیر" بنویس.')

‏        elif step == 'name':
‏            user_data[cid]['name'] = text
‏            user_data[cid]['step'] = 'phone'
‏            bot.send_message(cid, '📱 شماره تماس را وارد کن:')

‏        elif step == 'phone':
‏            user_data[cid]['phone'] = text
‏            user_data[cid]['step'] = 'city'
‏            bot.send_message(cid, '🏙 شهر را وارد کن:')

‏        elif step == 'city':
‏            user_data[cid]['city'] = text
‏            user_data[cid]['step'] = 'address'
‏            bot.send_message(cid, '📍 آدرس را وارد کن:')

‏        elif step == 'address':
‏            user_data[cid]['address'] = text
‏            data = user_data[cid]

‏            filename = f'order_{cid}.pdf'
‏            try:
‏                create_pdf(filename, data)
‏                with open(filename, 'rb') as f:
‏                    bot.send_document(cid, f)
‏                bot.send_message(cid, '✅ فاکتور شما ارسال شد. ممنون از خرید شما 🙏برای نهایی کردن به شماره09128883343در واتساپ پیام دهید')
‏            except Exception as e:
‏                bot.send_message(cid, f'❌ خطا در ساخت یا ارسال فاکتور: {e}')
‏            finally:
‏                if os.path.exists(filename):
‏                    os.remove(filename)
‏                user_data.pop(cid, None)
‏    except Exception as e:
‏        bot.send_message(cid, f'❌ خطایی رخ داد: {e}')

‏bot.remove_webhook()
‏bot.infinity_polling()
