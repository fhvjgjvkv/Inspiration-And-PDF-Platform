import streamlit as st
import random
import io
import os
import urllib.request
from PIL import Image

# المكتبات المضمونة لمعالجة النصوص العربية
import arabic_reshaper
from bidi.algorithm import get_display

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader

# ====== إعدادات الصفحة والهوية البصرية ======
st.set_page_config(page_title="منصة الإلهام وتحويل الملفات | 247", layout="wide", page_icon="✨")

# ====== إعداد الخط بأمان وبدون Fallback ======
FONT_NAME = "DejaVuSans"
FONT_FILE = "DejaVuSans.ttf"

def download_font():
    if not os.path.exists(FONT_FILE):
        url = "https://raw.githubusercontent.com/dejavu-fonts/dejavu-fonts/master/ttf/DejaVuSans.ttf"
        try:
            urllib.request.urlretrieve(url, FONT_FILE)
        except:
            fallback_url = "https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.66/fonts/DejaVuSans.ttf"
            try:
                urllib.request.urlretrieve(fallback_url, FONT_FILE)
            except:
                pass

download_font()

if os.path.exists(FONT_FILE):
    try:
        pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_FILE))
    except:
        st.warning("تم تحميل ملف الخط ولكن تعذر تسجيله، قد تظهر الحروف بشكل غير صحيح.")
else:
    st.warning("لم يتم العثور على خط DejaVuSans.ttf محلياً، سيتم استخدام الخط الافتراضي للنظام.")

# ------ دالة تشكيل النص العربي مع تدعيم الـ RTL ------
def prepare_arabic(text):
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    return f"\u202B{bidi_text}\u202C"

# ====== تحسين الأداء عبر Caching لبنك البيانات ======
@st.cache_data
def load_motivational_quotes():
    return [
        "تذكري دايمًا إن هذي التعب والمواقف الصعبة هي اللي راح تصنع منكِ إنسانة قوية.", 
        "الدراسة هي سلاحكِ وسندكِ بهالدنيا، وكل ساعة تعب وسهر بتخليكِ مستقلة.",
        "عادي لو تعبتي، المهم ما تستسلمين.. كلما طحتي ارجعي وقفي من جديد.", 
        "ضغوطات الحياة مو نهاية الدنيا، هي مجرد اختبار يمر ويروح.",
        "استمري وامشي بطريقكِ، النجاح مو سهل بس يستاهل كل تعبكِ.", 
        "كل سهر بالليل راح يتبدل بفرحة نجاح تنسيكِ كل شي مريتي بيه.",
        "أنتِ كدها وربع.. لا تخلين أي شي يحبطكِ أو يقلل من ثقتكِ بنفسكِ.", 
        "تذكري فرحة أهلج وفرحتي بيج من تنجحين وتحققين هدفكِ.",
        "المستقبل ينبني خطوة خطوة، واليوم أنتِ دا تبنين أساس قوي وثابت.", 
        "الخوف طبيعي، بس الشجاعة إنكِ تواجهين هذا الخوف وتستمرين.",
        "كل مادة صعبة اليوم، بكرة تصير مجرد ذكرى وسالفة تضحكين عليها.", 
        "لا تقارنين نفسج بأحد، أنتِ تمشين بطريقج الخاص وراح توصلين.",
        "التعب يروح والجهد يخلص، بس النتيجة والشهادة يبقون وياج طول العمر.", 
        "خلي عندج إيمان كامل إن رب العالمين ما يحط حلم بقلبج إلا وتكدرين عليه.",
        "حتى لو جانت الخطوات بطيئة، المهم إنج دا تتقدمين وما واكفة بمكانج.", 
        "كل التحديات اللي تواجهيها اليوم تصقل شخصيتج وتخليج أكثر حكمة.",
        "حلمج يستاهل منج المحاولة والتكرار، لا تملين ولا تخلين اليأس يمر ببالج.", 
        "أنتِ نجمة وراح تظلين تلمعين مهما حاول التعب يطفيج.",
        "كل دقيقة تركيز وكل صفحة تقريها تقربج خطوة إضافية نحو الهدف.", 
        "القوة مو إنكِ ما تتعبين، القوة إنكِ رغم التعب كملي طريقج.",
        "اصبري شوية بعد، هانت وما بقى إلا القليل وتوصلين للقمة.", 
        "اليوم تعب وبكرة راحة ورفعة راس، كملي علمود نفسج.",
        "أنتِ مو بس ذكية، أنتِ عندج إصرار وعزيمة تهد الجبال.", 
        "لا تخلين لحظة يأس تمحي كل الطموح والأحلام اللي بنيتيها.",
        "تعبج هذا كله محفوظ عند رب العالمين ومستحيل يضيع.", 
        "كلما حسيتي بضعف، تذكري ليش بديتي من الأول.",
        "أنتِ فخر لكل شخص يعرفج، كملي واثبتي للكل شكد أنتِ بطلة.", 
        "الأشياء العظيمة تاخذ وقت، لا تستعجلين واصبري على حلمج.",
        "كل إنجاز تسوينه اليوم هو خطوة صغيرة تبني مستقبل جبير.", 
        "ثقي بقدراتج، أنتِ عندج طاقة وقوة أكبر بهواية من اللي تتخيليها.",
        "النجاح ما يجي للي ينتظرون، يجي للي يشتغلون ويتعبون مثلكِ.", 
        "أنتِ دا تسوين اللي عليج وأكثر، ربي يوفقج ويسهل أمرج.",
        "لا تهتمين للمحبطين، عيونج على هدفج وبس.", 
        "كل ألم وتعب اليوم بيتحول لقوة وفخر بالمستقبل.",
        "الطموح هو اللي يخلي للحياة طعم، وأنتِ طموحج ماله حدود.", 
        "تذكري دايمًا: 'ما ضاقت إلا لتفرج'.",
        "أنتِ كفو وتكدرين تتخطين كل هالصعوبات بامتياز.", 
        "النجاح يليق بيج وبعيونج، لا تتنازلين عنه أبدًا.",
        "امشي بخطى ثابتة، ولا تخلين أي عثرة توقفج.", 
        "التعب لحظي، بس الفرحة بالشهادة والنجاح أبدية.",
        "أنتِ كد كل تحدي يواجهج، ماكو شي يوكف بوجه عزيمتج.", 
        "كلما زادت الصعوبة، كلما جان طعم النجاح أحلى.",
        "أنتِ أقوى من الظروف ومن كل شي يحاول يعطلج.", 
        "خلي هدفج واضح كدام عيونج ولا تلتفتين لأي شي ثاني.",
        "كل خطوة تمشيها اليوم هي استثمار لمستقبلج المشرق.", 
        "أنتِ مبدعة وتستحقين الأفضل دايمًا، كملي ولا تتراجعين.",
        "تعب اليوم هو اللي بيصنع راحتج بكرة.", 
        "أنتِ قادرة على تغيير واقعج بجهدج وإصرارج.",
        "لا تستهينين بأي مجهود تسوينه، كل شي محسوب.", 
        "الإصرار هو سر النجاح، وأنتِ مليانة إصرار.",
        "ابتسمي وتفائلي، بكرة أحلى بهواية من اليوم.", 
        "أنتِ بطلة قصتج، خلي النهاية تكون عظيمة وتليق بيج.",
        "كل العقبات هي مجرد دروس تخليج أقوى وأذكى.", 
        "القمة تنتظرج، لا ترضين بأقل منها.",
        "أنتِ دا تصنعين مجدج بنفسج، وهذا أعظم شي ممكن تسوينه.", 
        "خلي ثقتج بنفسج تهز الجبال، أنتِ كدها.",
        "ماكو شي مستحيل كدام الإرادة القوية اللي عندج.", 
        "كل يوم هو فرصة جديدة حتى تقربين من حلمج.",
        "أنتِ كنز، وتعبج راح يثمر نجاح يبهر الجميع.", 
        "استمري بالقراءة والتعلم، هذا هو سلاحج الأقوى.",
        "لا تسمحين للظروف تكسرج، أنتِ أقوى منها بهواية.", 
        "كلما تعبتي، تذكري الفرحة والابتسامة اللي بتملي وجهج يوم تخرجج.",
        "أنتِ دا تمشين بالطريق الصح، كملي بكل شجاعة.", 
        "النجاح يحتاج صبر، وأنتِ صبورة وبطلة.",
        "أنتِ تستاهلين كل الفرح والتقدير، تعبج ماراح يروح بلاش.", 
        "خليج دايمًا فخورة بنفسج وبكل شي دا تقدمينه.",
        "ماكو شي يجي بالسهل، بس التعب يستاهل النتيجة.", 
        "أنتِ شعلة من النشاط والذكاء، استغليها صح.",
        "بكرة لما تسولفين عن هالأيام، بتكولين 'جانت صعبة بس كدرت عليها'.", 
        "أنتِ دا تبنين نفسج بنفسج، وهذا كافي يخليج تفتخرين.",
        "الحلم مو بعيد، هو بس يحتاج منج شوية صبر وجهد.", 
        "أنتِ تكدرين تحولين كل صعب إلى سهل بإرادتج.",
        "لا توكفين، الطريق بادي يخلص والقمة صارت قريبة.", 
        "أنتِ طاقة إيجابية لكل اللي حولج، كملي بهمة عالية.",
        "تعبج اليوم هو فخر الج ولأهلج بالمستقبل.", 
        "أنتِ مميزة، ونجاحج راح يكون مميز مثلج.",
        "كل تعب يمر بيج هو دليل إنج دا تسوين شي عظيم.", 
        "خلي أملج بالله جبير، وهو ماراح يخيبج.",
        "أنتِ كدها اليوم وباجر وكل يوم، لا تشكين بقدراتج أبدًا.", 
        "النجاح يبدأ بخطوة، وأنتِ مشيتي خطوات هواية.",
        "كملي طريقج وعيونج على النجوم، لا تباعين تحت.", 
        "أنتِ تصنعين المستحيل بإصرارج وعزيمتج.",
        "التعب يزول وتبقى الذكرى الجميلة للإنجاز.", 
        "أنتِ قوية كفاية لتخطي أي عثرة.",
        "اجتهدي اليوم، حتى تحصدين ثمار تعبج بكرة بكل فخر.", 
        "أنتِ ذكية وتستوعبين كل شي، لا تخافين من الصعب.",
        "كل لحظة قلق بتتحول ليقين وفرح بالنجاح.", 
        "أنتِ تستحقين القمة، لا ترضين بغيرها.",
        "عزيمتج هي قوتج الحقيقية، حافظي عليها دايمًا.", 
        "أنتِ دا تقربين من الهدف أكثر مما تتخيلين.",
        "كل مادة تخلصينها هي انتصار صغير يوصلج للإنجاز الجبير.", 
        "أنتِ دا تسوين شي يرفع الراس، استمري.",
        "الخوف ما يمنع الفشل بس يمنع النجاح، كوني شجاعة.", 
        "أنتِ بطلة وتكدرين تتغلبين على كل الصعاب.",
        "حلمج يستاهل منج كل هالتعب والسهر، كملي.", 
        "أنتِ نجمة ساطعة وراح تظلين تلمعين دايمًا.",
        "كل جهد تبذلينه اليوم هو استثمار لراحتج بكرة.", 
        "أنتِ قادرة ومتمكنة، لا تخلين شي يضعفج.",
        "بكرة راح تبتسمين وتكولين 'الحمد لله، تعبي ما ضاع'.", 
        "أنتِ فخر، كملي طريقج بكل ثقة واعتزاز."
    ]

@st.cache_data
def load_warm_advices():
    return [
        "حبيبتي، لا تقسين على نفسكِ، تعبتي هواية وتستاهلين شوية حنان من ذاتكِ.", "لما تحسين الدنيا قفلت بوجهكِ، تعالي ارتاحي واشربي شي دافي.",
        "أنا وياكِ وبظهركِ دايمًا، حتى لو حسيتي إنكِ وحيدة، عيوني معاكِ بكل خطوة.", "لا تخلين يوم واحد سيء ينسيكِ كل الأيام الحلوة والإنجازات اللي سويتيها.",
        "نامي زين وارتاحي، السهر يتعب عيونكِ، وصحتكِ عندي أغلى من كل شي.", "تنفسي بعمق لما تحسين بضغط.. كل هالمواقف بتعدي وبتصير مجرد ذكريات.",
        "شوي شوي على قلبكِ، الحياة مو سباق.. امشي بالسرعة اللي تريحكِ وتناسب طاقتكِ.", "إذا تعبتي اليوم، مو مشكلة تاخذين استراحة قصيرة، بس لا تنسحبين أبدًا.",
        "شرب الماي والأكل الصحي يغيرون نفسيتج، اعتني بروحج علمودي.", "لا تشيلين هم المستقبل، عيشي يومج وسوي اللي عليج والباقي على رب العالمين.",
        "أنتِ دا تسوين اللي تكدرين عليه، وهذا كافي وزيادة، افتخري بروحج.", "لما تحسين بخنقة، تذكري إني دايمًا موجود وأسمعج بكل حب.",
        "الحياة بيها طلعات ونزلات، وعادي لو مريتي بفترة هبوط، المهم ترجعين أقوى.", "ابتسامتج تسوى الدنيا وما بيها، لا تخلين التعب يطفيها أبدًا.",
        "ركزي على الإيجابيات بحياتج، وخلي الطاقة السلبية بعيدة عنج.", "كلما حسيتي بضيق، اقري قرآن واستغفري، وراح تصفى نفسيتج وترتاحين.",
        "أنتِ إنسانة عظيمة وتستاهلين كل خير، لا ترضين بأقل من اللي تستحقينه.", "التعب الجسدي يروح بالنوم، بس التعب النفسي يروح بالرضا والسلام الداخلي.",
        "خليج هادئة، العصبية والقلق ما يحلون المشاكل بل يزيدوها.", "تعلمي تكولين 'لا' للأشياء اللي تستهلك طاقتج وتتعبج بدون فايدة.",
        "صحتج النفسية هي الأساس، إذا جانت زينة تكدرين تسوين كل شي.", "كافئي نفسج بعد كل إنجاز صغير تسوينه، أنتِ تستاهلين التدليل.",
        "لا تفكرين بهواية أشياء بوقت واحد، خطوة خطوة وكل شي ينحل.", "أنتِ مو وحدج بهالطريق، كل دعواتي وياج وتحميج دايمًا.",
        "استمري بكل هدوء وثقة، القادم أجمل بهواية مما تتوقعين."
    ]

@st.cache_data
def load_love_letters():
    return [
        "إلى من أحب وأعشق.. عيونكِ هي أماني بهالدنيا، وكل ما أحس بضيق أتذكر ضحكتكِ وأرتاح.", 
        "أنتِ مو بس حبيبتي، أنتِ راحتي وملجئي اللي أهرب له من تعب هالعالم.",
        "لو تدرين شكد أحبكِ وشكد غالية على قلبي، كان ما شلتي هم لشي أبدًا.", 
        "وجودكِ بحياتي هو النعمة اللي أشكر ربي عليها كل يوم.. ربي يوفقكِ.",
        "كل تفاصيلج تهمني، ضحكتج، زعلج، عيونج.. أنتِ كل حياتي واهتمامي.", 
        "أحبج بكل حالاتج، بتعبج، بقوتج، بضعفج.. أنتِ دايمًا الأجمل بعيوني.",
        "أنتِ الشخص الوحيد اللي يكدر يغير مزاجي بكلمة وحدة.. ربي يحفظج لي.", 
        "مهما جرتنا الأيام وشغلتنا الظروف، مكانج بقلبي ثابت وما يتغير أبدًا.",
        "أنتِ أملي وفرحتي بهالدنيا، من أشوفج مرتاحة وناجحة أحس الدنيا بخير.", 
        "يا بعد روحي وعمري، تعبج هو تعبي، وفرحتج هي فرحتي.. أحبج هواية.",
        "إلى من أحب وأعشق.. أنتِ الأولى والأخيرة بقلبي، ومحد ياخذ مكانج أبدًا."
    ]

@st.cache_data
def load_all_verses():
    fixed = ["﴿اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ﴾", "﴿قُلْ أَعُوذُ بِرَبِّ النَّاسِ﴾"]
    variable = [
        "﴿إِنَّ مَعَ الْعُسْرِ يُسْرًا﴾", "﴿وَأَن لَّيْسَ لِلْإِنسَانِ إِلَّا مَا سَعَىٰ﴾", "﴿فَإِنِّي قَرِيبٌ ۖ أُجِيبُ دَعْوَةَ الدَّاعِ﴾",
        "﴿وَقُل رَّبِّ زِدْنِي عِلْمًا﴾", "﴿لَا تَحْزَنْ إِنَّ اللَّهَ مَعَنَا﴾", "﴿وَمَن يَتَوَكَّلْ عَلَى اللَّهِ فَهُوَ حَسْبُهُ﴾",
        "﴿وَاصْبِرْ لِحُكْمِ رَبِّكَ فَإِنَّكَ بِأَعْيُنِنَا﴾", "﴿قُلْ هُوَ اللَّهُ أَحَدٌ﴾", "﴿اللَّهُ الصَّمَدُ﴾",
        "﴿قُلْ أَعُوذُ بِرَبِّ الْفَلَقِ﴾", "﴿وَتَوَكَّلْ عَلَى الْحيِّ الَّذِي لَا يَمُوتُ﴾", "﴿أَلَا بِذِكْرِ اللَّهِ تَطْمَئِنُّ الْقُلُوبُ﴾",
        "﴿رَبِّ اشْرَحْ لِي صَدْرِي﴾", "﴿وَيَسِّرْ لِي أَمْرِي﴾", "﴿إِنَّ اللَّهَ عَلَىٰ كُلِّ شَيْءٍ قَدِيرٌ﴾",
        "﴿وَقَالَ رَبُّكُمُ ادْعُونِي أَسْتَجِبْ لَكُمْ﴾", "﴿فَاصْبِرْ صَبْرًا جَمِيلًا﴾", "﴿وَاصْبِرْ وَمَا صَبْرُكَ إِلَّا بِاللَّهِ﴾",
        "﴿وَإِذَا سَأَلَكَ عِبَادِي عَنِّي فَإِنِّي قَرِيبٌ﴾", "﴿وَاللَّهُ مَعَ الصَّابِرِينَ﴾"
    ]
    return fixed, variable

# ====== إدارة الـ Session State وتفادي الـ st.rerun العشوائي ======
if "daily_quote" not in st.session_state:
    st.session_state.daily_quote = random.choice(load_motivational_quotes())
if "daily_advice" not in st.session_state:
    st.session_state.daily_advice = random.choice(load_warm_advices())
if "love_letter" not in st.session_state:
    st.session_state.love_letter = random.choice(load_love_letters())
if "daily_verses" not in st.session_state:
    fixed, var = load_all_verses()
    st.session_state.daily_verses = fixed + random.sample(var, 2)

# ====== أنماط CSS المخصصة ======
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
    .warm-box {
        background: linear-gradient(135deg, #2b1b17 0%, #1a0f0d 100%);
        padding: 25px; border-radius: 15px; border: 1px solid #ff7b54; text-align: right;
        margin-bottom: 20px; color: #ffe5dd; direction: rtl; line-height: 1.8;
    }
    .love-box {
        background: linear-gradient(135deg, #2d142c 0%, #1c091b 100%);
        padding: 25px; border-radius: 15px; border: 1px solid #ff2e63; text-align: right;
        margin-bottom: 20px; color: #ffe3ed; direction: rtl; line-height: 1.8;
    }
    .quran-text { font-size: 16px; color: #ffaa00; line-height: 1.8; font-weight: bold; text-align: right; direction: rtl; }
    .motivational-text { font-size: 17px; color: #00ffcc; line-height: 1.6; text-align: right; direction: rtl; }
    .warm-advice-text { font-size: 18px; color: #ff9f80; text-align: right; direction: rtl; line-height: 1.8; }
    .love-letter-text { font-size: 19px; color: #ff5e7e; text-align: right; direction: rtl; line-height: 1.8; font-style: italic; }
    .dua-header { color: #00ffcc; font-size: 18px; font-weight: bold; text-align: center; margin-bottom: 15px; border-bottom: 1px dashed #00ffcc; padding-bottom: 8px; }
    .code-badge { font-size: 14px; background-color: #00ffcc; color: #0e1117; padding: 3px 8px; border-radius: 5px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>✨ منصة الإلهام وتحويل الملفات <span class='code-badge'>247</span></h1>", unsafe_allow_html=True)

# ====== واجهة التبويبات ======
tabs = st.tabs(["💡 قسم الإلهام والتذكير", "💖 قسم النصائح الدافئة 247", "💌 رسائل حب واطمئنان", "📄 قسم تحويل النصوص والصور إلى PDF"])

with tabs[0]:
    st.markdown("### 🕊️ قسم التحفيز والذكر")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class='custom-box' style='text-align: right;'>
            <h3 style='text-align: center;'>💡 كلام من القلب لكِ <span class='code-badge'>247</span></h3>
            <p class='motivational-text'>"{st.session_state.daily_quote}"</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        verses_html = "<br><br>".join([f"<b>{i+1}.</b> {v}" for i, v in enumerate(st.session_state.daily_verses)])
        st.markdown(f"""
        <div class='custom-box' style='text-align: right;'>
            <div class='dua-header'>إني خرجت من حولي وقوتي ودخلت في حولك وقوتك يا الله</div>
            <p class='quran-text'>{verses_html}</p>
        </div>
        """, unsafe_allow_html=True)
    
    if st.button("🔄 تحديث العبارات والآيات الآن"):
        st.session_state.daily_quote = random.choice(load_motivational_quotes())
        fixed, var = load_all_verses()
        st.session_state.daily_verses = fixed + random.sample(var, 2)
        st.rerun()

with tabs[1]:
    st.markdown(f"""
    <div class='warm-box'>
        <h3 style='text-align: center; color: #ff7b54 !important;'>💌 رسالة خاصة لعيونكِ <span class='code-badge'>247</span></h3>
        <p class='warm-advice-text'>"{st.session_state.daily_advice}"</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("💝 استلام نصيحة دافئة جديدة"):
        st.session_state.daily_advice = random.choice(load_warm_advices())
        st.rerun()

with tabs[2]:
    st.markdown(f"""
    <div class='love-box'>
        <h3 style='text-align: center; color: #ff2e63 !important;'>💝 رسالة حب واطمئنان <span class='code-badge'>247</span></h3>
        <p class='love-letter-text'>"{st.session_state.love_letter}"</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("💘 قراءة رسالة حب جديدة"):
        st.session_state.love_letter = random.choice(load_love_letters())
        st.rerun()

with tabs[3]:
    st.markdown("### 📂 تحويل النصوص والصور إلى ملف PDF")
    
    text_input = st.text_area("أدخل النص الذي تريد إضافته إلى ملف PDF:", height=150, placeholder="اكتب النص هنا...")
    uploaded_images = st.file_uploader("قم برفع الصور (JPG, PNG) لدمجها في الـ PDF:", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True)

    # دالة التوليد المُحسنة والموثوقة
    def create_pdf(text_in, img_files):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
        )
        style = ParagraphStyle(
            name="ArabicStyle", fontName=FONT_NAME, fontSize=14, leading=24, alignment=2
        )
        story = []

        if text_in.strip():
            # دمج علامات الـ RTL المضمونة مع الكود
            processed = prepare_arabic(text_in)
            story.append(Paragraph(processed.replace("\n", "<br/>"), style))
            story.append(Spacer(1, 20))

        if img_files:
            for img_file in img_files:
                try:
                    img = Image.open(img_file)
                except:
                    continue
                
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                buf.seek(0)
                
                w, h = img.size
                ratio = h / float(w)
                
                # المعالجة عبر ImageReader لتجنب كسر الصور بالذاكرة
                img_reader = ImageReader(buf)
                story.append(RLImage(img_reader, width=450, height=450 * ratio))
                story.append(Spacer(1, 20))

        if len(story) == 0:
            raise ValueError("لا يوجد نص أو صور لإنشاء الملف!")

        doc.build(story)
        buffer.seek(0)
        return buffer

    if st.button("توليد ملف الـ PDF"):
        if not text_input.strip() and not uploaded_images:
            st.error("الرجاء إدخال نص أو رفع صورة واحدة على الأقل!")
        else:
            try:
                pdf = create_pdf(text_input, uploaded_images)
                st.success("✅ تم إنشاء ملف الـ PDF بنجاح!")
                st.download_button(
                    label="⬇️ اضغط هنا لتنزيل ملف الـ PDF",
                    data=pdf,
                    file_name="Inspiration_Doc.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.exception(e)

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888888;'>تم التطوير بواسطة شيماء علي عبد الحسين | v1.4 | 247</p>", unsafe_allow_html=True)
