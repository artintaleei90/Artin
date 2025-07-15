import os
import telebot
from flask import Flask, request
import json
from telebot import types
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from bidi.algorithm import get_display
import arabic_reshaper

TOKEN = "7739258515:AAEUXIZ3ySZ9xp9W31l7qr__sZkbf6qcKnE"
WEBAPP_URL = "https://artin-oqaq.onrender.com"  # آدرس مینی‌اپت رو اینجا بذار

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

pdfmetrics.registerFont(TTFont('Vazir', 'Vazirmatn-Regular.ttf'))

def reshape(text):
    return get_display(arabic_reshaper.reshape(text))

def create_pdf(cid, data):
    filename = f'order_{cid}.pdf'
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    y = height - 50

    c.setFont("Vazir", 16)
    c.drawCentredString(width / 2, y, reshape("🧾 فاکتور سفارش"))
    y -= 40

    c.setFont("Vazir", 12)
    for field in ["name", "phone", "city", "address"]:
        line = f"{field}: {data.get(field, '')}"
        c.drawRightString(width - 50, y, reshape(line))
        y -= 25

    y -= 20
    total = 0
    for item in data["orders"]:
        line = f"{item['code']} | {item['name']} | {item['count']} عدد × {item['price']} تومان"
        total += item['price'] * item['count']
        c.drawRightString(width - 50, y, reshape(line))
        y -= 20

    c.drawRightString(width - 50, y, reshape(f"مجموع: {total} تومان"))
    c.showPage()
    c.save()
    return filename

@app.route("/", methods=["GET"])
def home():
    return "✅ ربات فعال است."

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        payload = request.get_json()
        if "message" in payload and "web_app_data" in payload["message"]:
            data = json.loads(payload["message"]["web_app_data"]["data"])
            cid = payload["message"]["chat"]["id"]
            file = create_pdf(cid, data)
            with open(file, 'rb') as f:
                bot.send_document(cid, f)
            os.remove(file)
        else:
            bot.process_new_updates([telebot.types.Update.de_json(payload)])
        return "OK"
    except Exception as e:
        return f"Error: {e}", 500

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    webapp_btn = types.KeyboardButton('🛍 مشاهده محصولات', web_app=types.WebAppInfo(WEBAPP_URL))
    markup.add(webapp_btn)
    bot.send_message(message.chat.id, "سلام! از دکمه زیر می‌تونی محصولات رو ببینی و سفارش بدی:", reply_markup=markup)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
