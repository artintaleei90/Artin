import os
from flask import Flask, send_file
from fpdf import FPDF

app = Flask(__name__)

@app.route('/')
def generate_pdf():
    # ساخت PDF
    pdf = FPDF()
    pdf.add_page()

    # افزودن فونت
    font_path = 'fonts/Vazirmatn-RD-NL-Regular.ttf'
    if not os.path.exists(font_path):
        return '❌ فونت پیدا نشد: ' + font_path

    pdf.add_font('Vazir', '', font_path, uni=True)
    pdf.set_font('Vazir', '', 14)

    # متن فارسی نمونه
    text = "🧾 فاکتور نمونه\nنام محصول: مانتو تابستانی\nقیمت: ۳۲۰٬۰۰۰ تومان\nتعداد: ۲ عدد\nمبلغ کل: ۶۴۰٬۰۰۰ تومان"

    # نوشتن از راست به چپ با معکوس کردن رشته‌ها
    for line in text.split('\n'):
        pdf.cell(0, 10, txt=line[::-1], ln=True, align='R')

    # ذخیره PDF
    pdf.output("sample.pdf")
    return send_file("sample.pdf", mimetype='application/pdf')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
