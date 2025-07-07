import requests
import zipfile
import io
import os
from fpdf import FPDF

FONT_ZIP_URL = 'https://github.com/artintaleei90/Artin/raw/main/vazirmatn-v33.003.zip'
FONTS_DIR = 'fonts'
FONT_FILE = f'{FONTS_DIR}/Vazirmatn-Regular.ttf'

def download_and_extract_fonts():
    if not os.path.exists(FONT_FILE):
        os.makedirs(FONTS_DIR, exist_ok=True)
        print("دانلود فونت...")
        r = requests.get(FONT_ZIP_URL)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        for file in z.namelist():
            if 'Vazirmatn-Regular.ttf' in file:
                z.extract(file, FONTS_DIR)
                # تغییر نام به مسیر درست
                os.rename(os.path.join(FONTS_DIR, file), FONT_FILE)
                break
        print("فونت استخراج شد.")
    else:
        print("فونت قبلاً دانلود شده.")

download_and_extract_fonts()

# ساخت PDF تستی
class PDF(FPDF):
    def header(self):
        self.add_font('Vazir', '', FONT_FILE, uni=True)
        self.set_font('Vazir', '', 16)
        self.cell(0, 10, 'سلام سلطان!', 0, 1, 'C')

pdf = PDF()
pdf.add_page()
pdf.output('test.pdf')
print("PDF ساخته شد ✅")
