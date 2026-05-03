import streamlit as st
import random
import io
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# 1. إعدادات الصفحة والهوية البصرية
st.set_page_config(page_title="منصة الإلهام وتحويل الملفات", layout="wide", page_icon="✨")

st.markdown("""
<style>
    .main { background-color: #0e1117; }
    h1, h2, h3 { color: #00ffcc !important; text-align: center; }
    .stButton>button { 
        background: linear-gradient(45deg, #00ffcc, #0055ff); 
        color: white; border-radius: 10px; border: none; font-weight: bold; width: 100%;
        padding: 10px; font-size: 16px;
    }
    .custom-box {
        background: linear-gradient(135deg, #1e2130 0%, #0c2333 100%);
        padding: 20px; border-radius: 12px; border: 1px solid #00ffcc; text-align: center;
        margin-bottom: 20px; color: white; min-height: 220px;
    }
    .quran-text {
        font-size: 16px; color: #ffaa00; line-height: 1.8; font-weight: bold; text-align: right; direction: rtl;
    }
    .motivational-text {
        font-size: 17px; color: #00ffcc; line-height: 1.6; font-style: italic;
    }
    .dua-header {
        color: #00ffcc; font-size: 18px; font-weight: bold; text-align: center; margin-bottom: 15px; border-bottom: 1px dashed #00ffcc; padding-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>✨ منصة الإلهام وتحويل الملفات</h1>", unsafe_allow_html=True)

# 2. بنك الكلمات التحفيزية
motivational_quotes = [
    "النجاح ليس نهاية، والفشل ليس قاتلاً، إنما الشجاعة للاستمرار هي ما يهم. اجعل شغفك هو الوقود.",
    "كل جهد تبذله اليوم هو استثمار في مستقبلك. لا تتوقف عندما تتعب، بل توقف عندما تنتهي.",
    "البرمجة والتطوير مهارة تصنع الفارق في العالم، استمر في التعلم وحل المشكلات خطوة بخطوة.",
    "السر في المضي قدماً هو البدء. لا تنتظر الظروف المثالية، اصنع ظروفك بنفسك الآن.",
    "العظماء لا يولدون عمالقة، بل يبدأون من الصفر وبالمداومة والاستمرار يحققون المستحيل.",
    "الفرص لا تحدث بالصدفة، بل أنت من يصنعها بالعمل المستمر والتركيز العالي.",
    "ثق بقدراتك البرمجية والتقنية؛ فكل سطر كود تكتبه يختصر عليك مسافات طويلة في المستقبل."
]

# 3. بنك الآيات القرآنية
# الثوابت (آية الكرسي وسورة الناس)
fixed_verses = [
    "﴿اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ ۚ لَا تَأْخُذُهُ سِنَةٌ وَلَا نَوْمٌ ۚ لَّهُ مَا فِي السَّمَاوَاتِ وَمَا فِي الْأَرْضِ ۗ مَن ذَا الَّذِي يَشْفَعُ عِندَهُ إِلَّا بِإِذْنِهِ ۚ يَعْلَمُ مَا بَيْنَ أَيْدِيهِمْ وَمَا خَلْفَهُمْ ۖ وَلَا يُحِيطُونَ بِشَيْءٍ مِّنْ عِلْمِهِ إِلَّا بِمَا شَاءَ ۚ وَسِعَ كُرْسِيُّهُ السَّمَاوَاتِ وَالْأَرْضَ ۖ وَلَا يَئُودُهُ حِفْظُهُمَا ۚ وَهُوَ الْعَلِيُّ الْعَظِيمُ﴾",
    "﴿قُلْ أَعُوذُ بِرَبِّ النَّاسِ ۝ مَلِكِ النَّاسِ ۝ إِلَٰهِ النَّاسِ ۝ مِن شَرِّ الْوَسْوَاسِ الْخَنَّاسِ ۝ الَّذِي يُوَسْوِسُ فِي صُدُورِ النَّاسِ ۝ مِنَ الْجَنَّةِ وَالنَّاسِ﴾"
]

# بقية الآيات (48 آية متنوعة لاختيار 2 منها عشوائياً)
variable_verses = [
    "﴿إِنَّ مَعَ الْعُسْرِ يُسْرًا﴾",
    "﴿وَأَن لَّيْسَ لِلْإِنسَانِ إِلَّا مَا سَعَىٰ﴾",
    "﴿فَإِنِّي قَرِيبٌ ۖ أُجِيبُ دَعْوَةَ الدَّاعِ﴾",
    "﴿وَقُل رَّبِّ زِدْنِي عِلْمًا﴾",
    "﴿إِنَّ اللَّهَ لَا يُضِيعُ أَجْرَ مَنْ أَحْسَنَ عَمَلًا﴾",
    "﴿وَمَن يَتَوَكَّلْ عَلَى اللَّهِ فَهُوَ حَسْبُهُ﴾",
    "﴿وَلَسَوْفَ يُعْطِيكَ رَبُّكَ فَتَرْضَىٰ﴾",
    "﴿وَاصْبِرْ لِحُكْمِ رَبِّكَ فَإِنَّكَ بِأَعْيُنِنَا﴾",
    "﴿لَا يُكَلِّفُ اللَّهُ نَفْسًا إِلَّا وُسْعَهَا﴾",
    "﴿وَاللَّهُ يَعْلَمُ وَأَنْتُمْ لَا تَعْلَمُونَ﴾",
    "﴿فَاصْبِرْ صَبْرًا جَمِيلًا﴾",
    "﴿إِنَّ اللَّهَ مَعَ الصَّابِرِينَ﴾",
    "﴿ادْعُونِي أَسْتَجِبْ لَكُمْ﴾",
    "﴿وَأَحْسِنُوا ۛ إِنَّ اللَّهَ يُحِبُّ الْمُحْسِنِينَ﴾",
    "﴿رَبِّ اشْرَحْ لِي صَدْرِي ۝ وَيَسِّرْ لِي أَمْرِي﴾",
    "﴿قُلْ حَسْبِيَ اللَّهُ ۖ عَلَيْهِ يَتَوَكَّلُ الْمُتَوَكِّلُونَ﴾",
    "﴿إِنَّ رَحْمَتَ اللَّهِ قَرِيبٌ مِّنَ الْمُحْسِنِينَ﴾",
    "﴿وَهُوَ مَعَكُمْ أَيْنَ مَا كُنتُمْ﴾",
    "﴿فَسْتَجَبْنَا لَهُ وَنَجَّيْنَاهُ مِنَ الْغَمِّ ۚ وَكَذَٰلِكَ نُنجِي الْمُؤْمِنِينَ﴾",
    "﴿قُلْ إِنَّ صَلَاتِي وَنُسُكِي وَمَحْيَايَ وَمَمَاتِي لِلَّهِ رَبِّ الْعَالَمِينَ﴾",
    "﴿رَبَّنَا لَا تُزِغْ قُلُوبَنَا بَعْدَ إِذْ هَدَيْتَنَا وَهَبْ لَنَا مِن لَّدُنكَ رَحْمَةً﴾",
    "﴿وَقُل جَاءَ الْحَقُّ وَزَهَقَ الْبَاطِلُ ۚ إِنَّ الْبَاطِلَ كَانَ زَهُوقًا﴾",
    "﴿رَبِّ هَبْ لِي حُكْمًا وَأَلْحِقْنِي بِالصَّالِحِينَ﴾",
    "﴿إِنَّ رَبِّي لَطِيفٌ لِّمَا يَشَاءُ ۚ إِنَّهُ هُوَ الْعَلِيمُ الْحَكِيمُ﴾",
    "﴿وَاللَّهُ غَالِبط عَلَىٰ أَمْرِهِ وَلَٰكِنَّ أَكْثَرَ النَّاسِ لَا يَعْلَمُونَ﴾",
    "﴿إِنَّ اللَّهَ مَعَ الَّذِينَ اتَّقَوا وَّالَّذِينَ هُم مُّحْسِنُونَ﴾",
    "﴿وَتَوَكَّلْ عَلَى الْحَيِّ الَّذِي لَا يَمُوتُ﴾",
    "﴿فَاللَّهُ خَيْرٌ حَافِظًا ۖ وَهُوَ أَرْحَمُ الرَّاحِمِينَ﴾",
    "﴿رَبَّنَا آتِنَا مِن لَّدُنكَ رَحْمَةً وَهَيِّئْ لَنَا مِنْ أَمْرِنَا رَشَدًا﴾",
    "﴿وَاصْبِرْ وَمَا صَبْرُكَ إِلَّا بِاللَّهِ﴾",
    "﴿وَقُلِ الْحَمْدُ لِلَّهِ سَيُرِيكُمْ آيَاتِهِ فَتَعْرِفُونَهَا﴾",
    "﴿قُلِ اللَّهُ يُنَجِّيكُم مِّنْهَا وَمِن كُلِّ كَرْبٍ﴾",
    "﴿وَمَا تَوْفِيقِي إِلَّا بِاللَّهِ ۚ عَلَيْهِ تَوَكَّلْتُ وَإِلَيْهِ أُنِيبُ﴾",
    "﴿إِلَيْهِ يَصْعَدُ الْكَلِمُ الطَّيِّبُ وَالْعَمَلُ الصَّالِحُ يَرْفَعُهُ﴾",
    "﴿إِنَّ اللَّهَ هُوَ الرَّزَّاقُ ذُو الْقُوَّةِ الْمَتِينُ﴾",
    "﴿وَكَانَ حَقًّا عَلَيْنَا نَصْرُ الْمُؤْمِنِينَ﴾",
    "﴿أَلَيْسَ اللَّهَ بِكَافٍ عَبْدَهُ﴾",
    "﴿وَمَا كَانَ اللَّهُ لِيُعْجِزَهُ مِن شَيْءٍ فِي السَّمَاوَاتِ وَلَا فِي الْأَرْضِ﴾",
    "﴿وَقُل رَّبِّ أَدْخِلْنِي مُدْخَلَ صِدْقٍ وَأَخْرِجْنِي مُخْرَجَ صِدْقٍ﴾",
    "﴿لَا تَحْزَنْ إِنَّ اللَّهَ مَعَنَا﴾",
    "﴿وَمَن يَتَتقِ اللَّهَ يَجْعَل لَّهُ مَخْرَجًا وَيَرْزُقْهُ مِنْ حيثُ لَا يَحْتَسِبُ﴾",
    "﴿وَأُفَوِّضُ أَمْرِي إِلَى اللَّهِ ۚ إِنَّ اللَّهَ بَصِيرٌ بِالْعِبَادِ﴾",
    "﴿وَمَا جَعَلَهُ اللَّهُ إِلَّا بُشْرَىٰ لَكُمْ وَلِتَطْمَئِنَّ قُلُوبُكُم بِهِ﴾",
    "﴿فَسَيَكْفِيكَهُمُ اللَّهُ ۚ وَهُوَ السَّمِيعُ الْعَلِيمُ﴾",
    "﴿وَآتَاكُم مِّن كُلِّ مَا سَأَلْتُمُوهُ﴾",
    "﴿رَبِّ إِنِّي لِمَا أَنزَلْتَ إِلَيَّ مِنْ خَيْرٍ فَقِيرٌ﴾",
    "﴿وَتَزَوَّدُوا فَإِنَّ خَيْرَ الزَّادِ التَّقْوَىٰ﴾",
    "﴿وَجَزَاهُم بِمَا صَبَرُوا جَنَّةً وَحَرِيرًا﴾"
]

# 4. إدارة التحديث التلقائي واليدوي للعبارات عبر Session State
if "daily_quote" not in st.session_state or "daily_verses" not in st.session_state:
    st.session_state.daily_quote = random.choice(motivational_quotes)
    selected_variable = random.sample(variable_verses, 2)
    st.session_state.daily_verses = fixed_verses + selected_variable

# 5. التبويبات الرئيسية
tabs = st.tabs(["💡 قسم الإلهام والتذكير", "📄 قسم تحويل النصوص والصور إلى PDF"])

# --- القسم الأول: الإلهام والتذكير ---
with tabs[0]:
    st.markdown("### 🕊️ قسم التحفيز والذكر")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class='custom-box'>
            <h3>💡 كلمة تحفيزية</h3>
            <p class='motivational-text'>"{st.session_state.daily_quote}"</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        # العبارة والآيات المتجددة
        verses_html = "<br><br>".join([f"<b>{i+1}.</b> {v}" for i, v in enumerate(st.session_state.daily_verses)])
        st.markdown(f"""
        <div class='custom-box' style='text-align: right;'>
            <div class='dua-header'>إني خرجت من حولي وقوتي ودخلت في حولك وقوتك يا الله</div>
            <p class='quran-text'>{verses_html}</p>
        </div>
        """, unsafe_allow_html=True)
        
    # زر التحديث الفوري للعبارات
    if st.button("🔄 تحديث العبارات والآيات الآن"):
        st.session_state.daily_quote = random.choice(motivational_quotes)
        selected_variable = random.sample(variable_verses, 2)
        st.session_state.daily_verses = fixed_verses + selected_variable
        st.rerun()

# --- القسم الثاني: تحويل النصوص والصور إلى PDF ---
with tabs[1]:
    st.markdown("### 📂 تحويل النصوص والصور إلى ملف PDF احترافي")
    
    text_input = st.text_area("أدخل النص الذي تريد إضافته إلى ملف PDF:", height=150, placeholder="اكتب النص هنا...")
    uploaded_images = st.file_uploader("قم برفع الصور (JPG, PNG) لدمجها في الـ PDF:", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True)
    
    if st.button("توليد ملف الـ PDF"):
        if not text_input and not uploaded_images:
            st.error("الرجاء إدخال نص أو رفع صورة واحدة على الأقل!")
        else:
            try:
                pdf_buffer = io.BytesIO()
                doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
                
                styles = getSampleStyleSheet()
                normal_style = ParagraphStyle(
                    name='CustomStyle',
                    parent=styles['Normal'],
                    fontSize=12,
                    leading=16,
                    alignment=2
                )
                
                story = []
                
                if text_input:
                    for line in text_input.split('\n'):
                        if line.strip():
                            story.append(Paragraph(line, normal_style))
                    story.append(Spacer(1, 15))
                
                if uploaded_images:
                    for uploaded_img in uploaded_images:
                        img = Image.open(uploaded_img)
                        img_width, img_height = img.size
                        
                        aspect = img_height / float(img_width)
                        display_width = 500
                        display_height = 500 * aspect
                        
                        img_buffer = io.BytesIO()
                        img.save(img_buffer, format=img.format if img.format else "PNG")
                        img_buffer.seek(0)
                        
                        rl_img = RLImage(img_buffer, width=display_width, height=display_height)
                        story.append(rl_img)
                        story.append(Spacer(1, 15))
                
                doc.build(story)
                pdf_data = pdf_buffer.getvalue()
                
                st.success("✅ تم إنشاء ملف الـ PDF بنجاح!")
                
                st.download_button(
                    label="⬇️ اضغط هنا لتنزيل ملف الـ PDF",
                    data=pdf_data,
                    file_name="converted_document.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"حدث خطأ أثناء إنشاء الملف: {e}")

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888888;'>تم التطوير بواسطة شيماء علي عبد الحسين | v1.2</p>", unsafe_allow_html=True)
