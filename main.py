import telebot
from fpdf import FPDF
import os

TOKEN = '7739258515:AAEUXIZ3ySZ9xp9W31l7qr__sZkbf6qcKnE'
CHANNEL_LINK = 'https://t.me/your_channel_link'  # لینک کانال خودت را اینجا قرار بده

bot = telebot.TeleBot(TOKEN)

# کلاس PDF با پشتیبانی فونت فارسی
class PDF(FPDF):
    def header(self):
        self.set_font('Vazirmatn', 'B', 16)
        self.cell(0, 10, 'فاکتور سفارش', 0, 1, 'C')

    def add_order_table(self, orders):
        self.set_font('Vazirmatn', '', 14)
        for i, order in enumerate(orders, 1):
            self.cell(0, 10, f"{i}. محصول: {order['product']} - تعداد: {order['qty']}", 0, 1)

def add_farsi_font(pdf):
    # اگر فونت در فولدر fonts/ttf وجود دارد اضافه می‌شود
    pdf.add_font('Vazirmatn', '', 'fonts/fonts/ttf/Vazirmatn-Regular.ttf', uni=True)
    pdf.add_font('Vazirmatn', 'B', 'fonts/fonts/ttf/Vazirmatn-Bold.ttf', uni=True)

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    text = (
        "🛍 خوش آمدید به ربات فروشگاه هالستون!\n\n"
        "برای شروع لطفاً *کد محصول* را ارسال کنید.\n\n"
        f"🌐 کانال ما: {CHANNEL_LINK}"
    )
    # ارسال پیام بدون parse_mode چون متن ساده است و باعث ارور نمی‌شود
    bot.send_message(chat_id, text)

@bot.message_handler(func=lambda message: True)
def handle_order(message):
    chat_id = message.chat.id
    code = message.text.strip()

    # نمونه سفارش با کد دریافتی
    orders = [{'product': code, 'qty': 1}]

    pdf = PDF()
    add_farsi_font(pdf)
    pdf.add_page()
    pdf.add_order_table(orders)

    filename = f"{chat_id}_order.pdf"
    pdf.output(filename)

    with open(filename, 'rb') as file:
        bot.send_document(chat_id, file)

    bot.send_message(chat_id, "فاکتور سفارش شما ارسال شد.")

    # حذف فایل پس از ارسال برای صرفه جویی در فضا
    if os.path.exists(filename):
        os.remove(filename)

if __name__ == "__main__":
    print("ربات آماده است و شروع به کار کرد.")
    bot.polling(non_stop=True)
