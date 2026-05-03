import streamlit as st
import io
import os
import urllib.request
from PIL import Image

# ==== إعدادات الصفحة ====
st.set_page_config(page_title="تحويل النصوص والصور إلى PDF", layout="centered")

# ==== خطوط ====
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FONT_NAME = "DejaVuSans"
FONT_FILE = "DejaVuSans.ttf"

def download_font():
    if not os.path.exists(FONT_FILE):
        url = "https://github.com/googlefonts/dejavu-fonts/raw/master/resources/fonts/ttf/DejaVuSans.ttf"
        try:
            urllib.request.urlretrieve(url, FONT_FILE)
        except:
            fallback = "https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.66/fonts/DejaVuSans.ttf"
            urllib.request.urlretrieve(fallback, FONT_FILE)

download_font()

pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_FILE))

# تسجيل الخط كعائلة متكاملة لتفادي أخطاء النمط (Bold/Italic) في ReportLab
pdfmetrics.registerFontFamily(
    FONT_NAME,
    normal=FONT_NAME,
    bold=FONT_NAME,
    italic=FONT_NAME,
    boldItalic=FONT_NAME
)

# ==== دعم العربي ====
import arabic_reshaper
from bidi.algorithm import get_display
from xml.sax.saxutils import escape

def prepare_arabic(text):
    if not text.strip():
        return ""
    reshaped = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped)
    return escape(bidi_text)

# ==== واجهة المستخدم ====

st.title("📄 تحويل النصوص والصور إلى PDF")

text_input = st.text_area("أدخل النص العربي أو الإنجليزي:", height=150, placeholder="اكتب النص هنا...")
uploaded_images = st.file_uploader(
    "ارفع الصور (JPG, PNG, JPEG, WEBP):",
    type=["jpg", "png", "jpeg", "webp"],
    accept_multiple_files=True
)

if st.button("توليد PDF"):
    if not text_input and not uploaded_images:
        st.error("الرجاء إدخال نص أو رفع صورة واحدة على الأقل")
    else:
        try:
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
            from reportlab.lib.styles import ParagraphStyle
            from reportlab.lib.pagesizes import A4

            buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                buffer, 
                pagesize=A4,
                rightMargin=40,
                leftMargin=40,
                topMargin=40,
                bottomMargin=40
            )

            style = ParagraphStyle(
                name="ArabicStyle",
                fontName=FONT_NAME,
                fontSize=14,
                leading=22,
                alignment=2  # محاذاة النص من اليمين إلى اليسار
            )

            story = []

            # ==== 1. معالجة النص وإضافته للـ PDF ====
            if text_input:
                for line in text_input.split("\n"):
                    if line.strip():
                        safe_text = prepare_arabic(line.strip())
                        story.append(Paragraph(safe_text, style))
                        story.append(Spacer(1, 10))

            # ==== 2. معالجة الصور وإضافتها للـ PDF ====
            if uploaded_images:
                for img_file in uploaded_images:
                    # فتح الصورة لمعرفة أبعادها الأصلية فقط
                    img = Image.open(img_file)
                    width, height = img.size
                    ratio = height / width

                    # ضبط العرض ليتناسب مع الصفحة تلقائياً
                    new_width = 450
                    new_height = new_width * ratio

                    # إعادة مؤشر القراءة لبداية الملف الأصلي لكي تقرأه ReportLab بالكامل
                    img_file.seek(0)

                    # تمرير الملف المرفوع مباشرة لضمان أعلى استقرار ومنع تلف البيانات
                    story.append(RLImage(img_file, width=new_width, height=new_height))
                    story.append(Spacer(1, 15))

            # بناء الملف وحفظه في الذاكرة
            doc.build(story)

            st.success("تم إنشاء PDF بنجاح ✅")

            st.download_button(
                "تحميل الملف",
                data=buffer.getvalue(),
                file_name="converted_file.pdf",
                mime="application/pdf"
            )

        except Exception as e:
            st.error(f"خطأ أثناء إنشاء الملف: {e}")
