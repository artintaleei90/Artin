import telebot
from fpdf import FPDF
from flask import Flask
from threading import Thread
import os

TOKEN = "توکن_تو"

bot = telebot.TeleBot(TOKEN)

app = Flask('')

@app.route('/')
def home():
    return "Bot is running..."

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    Thread(target=run).start()

keep_alive()

# بقیه کد ربات و ساخت فاکتور

bot.infinity_polling()
