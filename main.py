import telebot
from keep_alive import keep_alive  # یادت باشه این فایل رو داشته باشی

TOKEN = "7739258515:AAEUXIZ3ySZ9xp9W31l7qr__sZkbf6qcKnE"
bot = telebot.TeleBot(TOKEN)

keep_alive()

user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_data[chat_id] = {
        "orders": [],
        "step": "code"
    }
    bot.send_message(chat_id, "به ربات فروشگاه 👗 **هالستون** خوش اومدی!\n\n📢 گروه ما: https://t.me/Halston_shop\n\nلطفاً کد محصول رو وارد کن:")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    text = message.text.strip()

    if chat_id not in user_data:
        user_data[chat_id] = {"orders": [], "step": "code"}
        bot.send_message(chat_id, "شروع جدید! لطفاً کد محصول رو وارد کن:")
        return

    step = user_data[chat_id]["step"]

    if step == "code":
        user_data[chat_id]["current_code"] = text
        user_data[chat_id]["step"] = "count"
        bot.send_message(chat_id, "✅ تعداد این محصول رو وارد کن:")

    elif step == "count":
        if not text.isdigit():
            bot.send_message(chat_id, "❗️ لطفاً فقط عدد وارد کن.")
            return
        count = int(text)
        code = user_data[chat_id]["current_code"]
        user_data[chat_id]["orders"].append({"code": code, "count": count})
        user_data[chat_id]["step"] = "more"
        bot.send_message(chat_id, "📦 سفارش دیگه‌ای داری؟ (بله / خیر)")

    elif step == "more":
        if text.lower() == "بله":
            user_data[chat_id]["step"] = "code"
            bot.send_message(chat_id, "کد محصول بعدی رو وارد کن:")
        elif text.lower() == "خیر":
            user_data[chat_id]["step"] = "name"
            bot.send_message(chat_id, "📝 لطفاً نام کاملت رو وارد کن:")
        else:
            bot.send_message(chat_id, "فقط 'بله' یا 'خیر' بنویس لطفاً.")

    elif step == "name":
        user_data[chat_id]["full_name"] = text
        user_data[chat_id]["step"] = "phone"
        bot.send_message(chat_id, "📱 شماره تماس خودت رو وارد کن:")

    elif step == "phone":
        user_data[chat_id]["phone"] = text
        user_data[chat_id]["step"] = "city"
        bot.send_message(chat_id, "🏙 لطفاً نام شهرت رو وارد کن:")

    elif step == "city":
        user_data[chat_id]["city"] = text
        user_data[chat_id]["step"] = "address"
        bot.send_message(chat_id, "📍 آدرس دقیق رو وارد کن:")

    elif step == "address":
        user_data[chat_id]["address"] = text
        user_data[chat_id]["step"] = "done"

        # ساخت محتوای فایل متنی با جدول مرتب
        orders = user_data[chat_id]["orders"]
        text_file = f"سفارش مشتری: {user_data[chat_id]['full_name']}\n"
        text_file += f"شماره تماس: {user_data[chat_id]['phone']}\n"
        text_file += f"شهر: {user_data[chat_id]['city']}\n"
        text_file += f"آدرس: {user_data[chat_id]['address']}\n\n"
        text_file += "📦 محصولات سفارش داده شده:\n"
        text_file += "---------------------------------------\n"
        text_file += "{:<20} | {:<10}\n".format("کد محصول", "تعداد")
        text_file += "---------------------------------------\n"

        for order in orders:
            text_file += "{:<20} | {:<10}\n".format(order['code'], order['count'])

        text_file += "---------------------------------------\n"

        # ذخیره در فایل
        file_name = f"order_{chat_id}.txt"
        with open(file_name, "w", encoding='utf-8') as f:
            f.write(text_file)

        # ارسال فایل به کاربر
        with open(file_name, "rb") as f:
            bot.send_document(chat_id, f, visible_file_name="safareshe_shoma.txt")

        bot.send_message(chat_id, "✅ سفارش ثبت شد. فایل بالا رو برای نهایی کردن ارسال کن به ۰۹۱۲۸۸۸۳۳۴۳")

        user_data.pop(chat_id)

print("✅ ربات آماده‌ست سلطان!")
bot.infinity_polling()
