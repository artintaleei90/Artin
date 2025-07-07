from flask import Flask, request, send_file
from fpdf import FPDF
import io

app = Flask('')

@app.route('/')
def home():
    return "من زنده‌ام سلطان 😎"

@app.route('/render', methods=['POST'])
def render_pdf():
    data = request.get_json()
    if not data:
        return "اطلاعاتی دریافت نشد", 400

    # ساخت PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)

    pdf.cell(200, 10, txt="🧾 فاکتور سفارش", ln=True, align='C')
    pdf.ln(10)

    pdf.cell(200, 10, txt=f"👤 نام: {data['full_name']}", ln=True)
    pdf.cell(200, 10, txt=f"🏙 شهر: {data['city']}", ln=True)
    pdf.multi_cell(200, 10, txt=f"📍 آدرس: {data['address']}")

    pdf.ln(5)
    pdf.cell(200, 10, txt="🛒 سفارش‌ها:", ln=True)

    for order in data["orders"]:
        pdf.cell(200, 10, txt=f"کد: {order['code']} | تعداد: {order['count']}", ln=True)

    # خروجی PDF در حافظه
    pdf_output = io.BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)

    return send_file(pdf_output, mimetype='application/pdf', as_attachment=True, download_name="order.pdf")

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    from threading import Thread
    t = Thread(target=run)
    t.start()
