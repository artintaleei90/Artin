from fpdf import FPDF
import arabic_reshaper
from bidi.algorithm import get_display

pdf = FPDF()
pdf.add_page()

# اضافه کردن فونت فارسی (مسیر فونت رو درست وارد کن)
pdf.add_font('Vazir', '', 'fonts/Vazirmatn-Regular.ttf', uni=True)
pdf.set_font('Vazir', '', 14)

# متن فارسی اصلی
text = "سلام سلطان عزیز! این یک متن تستی است."

# شکل‌دهی و راست به چپ کردن متن
reshaped_text = arabic_reshaper.reshape(text)
bidi_text = get_display(reshaped_text)

pdf.cell(0, 10, bidi_text)
pdf.output("output.pdf")
