import telebot
from keep_alive import keep_alive

# توکن ربات
TOKEN = "8134014873:AAGGfPvYLrSUyFWsRP0xXS_CRMS97BsO7f4"
bot = telebot.TeleBot(TOKEN)

# فعال‌سازی سرور برای آنلاین موندن
keep_alive()

@bot.message_handler(func=lambda m: True)
def echo(message):
    bot.reply_to(message, f"سلام سلطان 😎 گفتی: {message.text}")

print("ربات روشن شد...")
bot.infinity_polling()