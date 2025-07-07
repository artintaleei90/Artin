from flask import Flask, request, send_file
from fpdf import FPDF
import io

app = Flask(__name__)

@app.route('/render', methods=['POST'])
def render_pdf():
    data = request.get_json()
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.cell(200, 10, txt="سفارش جدید", ln=True, align='C')
    pdf.cell(200, 10, txt=f"نام: {data['full_name']}", ln=True)
    pdf.cell(200, 10, txt=f"شهر: {data['city']}", ln=True)
    pdf.cell(200, 10, txt=f"آدرس: {data['address']}", ln=True)
    
    pdf.cell(200, 10, txt="محصولات:", ln=True)
    for item in data['orders']:
        pdf.cell(200, 10, txt=f"- کد: {item['code']}, تعداد: {item['count']}", ln=True)

    output = io.BytesIO()
    pdf.output(output)
    output.seek(0)

    return send_file(output, download_name="order.pdf", as_attachment=True)

@app.route('/')
def home():
    return "سرور PDF فعاله سلطان 🧾"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
