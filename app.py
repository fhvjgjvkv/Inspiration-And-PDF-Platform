import streamlit as st
import random
import io
import os
import urllib.request
from PIL import Image

# ---- تسجيل الخط العربي بأمان لتجنب حساسية الأحرف ----
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FONT_NAME_1 = 'DejaVuSans'
FONT_NAME_2 = 'dejavusans'
FONT_FILE = 'DejaVuSans.ttf'

def download_font():
    if not os.path.exists(FONT_FILE):
        url = "https://github.com/googlefonts/dejavu-fonts/raw/master/resources/fonts/ttf/DejaVuSans.ttf"
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
        pdfmetrics.registerFont(TTFont(FONT_NAME_1, FONT_FILE))
        pdfmetrics.registerFont(TTFont(FONT_NAME_2, FONT_FILE))
    except:
        pass
else:
    try:
        pdfmetrics.registerFont(TTFont(FONT_NAME_1, 'Helvetica'))
        pdfmetrics.registerFont(TTFont(FONT_NAME_2, 'Helvetica'))
    except:
        pass

# ---- دالة تشكيل النص العربي ----
ARABIC_RESHAPER_MAP = {
    '\u0627': ('\uFE8D', '\uFE8E', '\uFE8D', '\uFE8E'),
    '\u0628': ('\uFE8F', '\uFE90', '\uFE91', '\uFE92'),
    '\u062A': ('\uFE95', '\uFE96', '\uFE97', '\uFE98'),
    '\u062B': ('\uFE99', '\uFE9A', '\uFE9B', '\uFE9C'),
    '\u062C': ('\uFE9D', '\uFE9E', '\uFE9F', '\uFEA0'),
    '\u062D': ('\uFEA1', '\uFEA2', '\uFEA3', '\uFEA4'),
    '\u062E': ('\uFEA5', '\uFEA6', '\uFEA7', '\uFEA8'),
    '\u062F': ('\uFEA9', '\uFEAA', '\uFEA9', '\uFEAA'),
    '\u0630': ('\uFEAB', '\uFEAC', '\uFEAB', '\uFEAC'),
    '\u0631': ('\uFEAD', '\uFEAE', '\uFEAD', '\uFEAE'),
    '\u0632': ('\uFEAF', '\uFEB0', '\uFEAF', '\uFEB0'),
    '\u0633': ('\uFEB1', '\uFEB2', '\uFEB3', '\uFEB4'),
    '\u0634': ('\uFEB5', '\uFEB6', '\uFEB7', '\uFEB8'),
    '\u0635': ('\uFEB9', '\uFEBA', '\uFEBB', '\uFEBC'),
    '\u0636': ('\uFEBD', '\uFEBE', '\uFEBF', '\uFEC0'),
    '\u0637': ('\uFEC1', '\uFEC2', '\uFEC3', '\uFEC4'),
    '\u0638': ('\uFEC5', '\uFEC6', '\uFEC7', '\uFEC8'),
    '\u0639': ('\uFEC9', '\uFECA', '\uFECB', '\uFECC'),
    '\u063A': ('\uFECD', '\uFECE', '\uFECF', '\uFED0'),
    '\u0641': ('\uFED1', '\uFED2', '\uFED3', '\uFED4'),
    '\u0642': ('\uFED5', '\uFED6', '\uFED7', '\uFED8'),
    '\u0643': ('\uFED9', '\uFEDA', '\uFEDB', '\uFEDC'),
    '\u0644': ('\uFEDD', '\uFEDE', '\uFEDF', '\uFEE0'),
    '\u0645': ('\uFEE1', '\uFEE2', '\uFEE3', '\uFEE4'),
    '\u0646': ('\uFEE5', '\uFEE6', '\uFEE7', '\uFEE8'),
    '\u0647': ('\uFEE9', '\uFEEA', '\uFEEB', '\uFEEC'),
    '\u0648': ('\uFEED', '\uFEEE', '\uFEED', '\uFEEE'),
    '\u064A': ('\uFEF1', '\uFEF2', '\uFEF3', '\uFEF4'),
    '\u0629': ('\uFE93', '\uFE94', '\uFE93', '\uFE94'),
    '\u0649': ('\uFEEF', '\uFEF0', '\uFEEF', '\uFEF0'),
    '\u0622': ('\uFE81', '\uFE82', '\uFE81', '\uFE82'),
    '\u0623': ('\uFE83', '\uFE84', '\uFE83', '\uFE84'),
    '\u0625': ('\uFE87', '\uFE88', '\uFE87', '\uFE88'),
    '\u0626': ('\uFE89', '\uFE8A', '\uFE8B', '\uFE8C'),
    '\u0621': ('\uFE80', '\uFE80', '\uFE80', '\uFE80'),
    '\u0624': ('\uFE85', '\uFE86', '\uFE85', '\uFE86'),
}
NON_JOINING_NEXT = {
    '\u0627', '\u062F', '\u0630', '\u0631', '\u0632', '\u0648',
    '\u0622', '\u0623', '\u0625', '\u0624', '\u0629', '\u0649'
}

def _reshape_word(word):
    chars = list(word)
    n = len(chars)
    result = []
    for i, char in enumerate(chars):
        if char not in ARABIC_RESHAPER_MAP:
            result.append(char)
            continue
        prev_joins = (i > 0 and chars[i-1] in ARABIC_RESHAPER_MAP and chars[i-1] not in NON_JOINING_NEXT)
        next_joins = (i < n-1 and chars[i+1] in ARABIC_RESHAPER_MAP and char not in NON_JOINING_NEXT)
        forms = ARABIC_RESHAPER_MAP[char]
        if prev_joins and next_joins:
            result.append(forms[3])
        elif prev_joins:
            result.append(forms[1])
        elif next_joins:
            result.append(forms[2])
        else:
            result.append(forms[0])
    return ''.join(reversed(result))

def prepare_arabic(text):
    lines = text.split('\n')
    result_lines = []
    for line in lines:
        words = line.split(' ')
        processed = []
        for w in words:
            if any('\u0600' <= c <= '\u06FF' for c in w):
                processed.append(_reshape_word(w))
            else:
                processed.append(w)
        result_lines.append(' '.join(reversed(processed)))
    return '\n'.join(result_lines)

# ====== إعدادات الصفحة ======
st.set_page_config(page_title="منصة الإلهام وتحويل الملفات | 247", layout="wide", page_icon="✨")

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
    .quran-text {
        font-size: 16px; color: #ffaa00; line-height: 1.8; font-weight: bold; text-align: right; direction: rtl;
    }
    .motivational-text {
        font-size: 17px; color: #00ffcc; line-height: 1.6; font-style: normal; text-align: right; direction: rtl;
    }
    .warm-advice-text {
        font-size: 18px; color: #ff9f80; font-weight: normal; text-align: right; direction: rtl; line-height: 1.8;
    }
    .love-letter-text {
        font-size: 19px; color: #ff5e7e; font-weight: normal; text-align: right; direction: rtl; line-height: 1.8; font-style: italic;
    }
    .dua-header {
        color: #00ffcc; font-size: 18px; font-weight: bold; text-align: center; margin-bottom: 15px; border-bottom: 1px dashed #00ffcc; padding-bottom: 8px;
    }
    .code-badge { font-size: 14px; background-color: #00ffcc; color: #0e1117; padding: 3px 8px; border-radius: 5px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>✨ منصة الإلهام وتحويل الملفات <span class='code-badge'>247</span></h1>", unsafe_allow_html=True)

# ====== بنك البيانات الكامل ======
motivational_quotes = [
    "تذكري دايمًا إن هذي التعب والمواقف الصعبة هي اللي راح تصنع منكِ إنسانة قوية.", "الدراسة هي سلاحكِ وسندكِ بهالدنيا، وكل ساعة تعب وسهر بتخليكِ مستقلة.",
    "عادي لو تعبتي، المهم ما تستسلمين.. كلما طحتي ارجعي وقفي من جديد.", "ضغوطات الحياة مو نهاية الدنيا، هي مجرد اختبار يمر ويروح.",
    "استمري وامشي بطريقكِ، النجاح مو سهل بس يستاهل كل تعبكِ.", "كل سهر بالليل راح يتبدل بفرحة نجاح تنسيكِ كل شي مريتي بيه.",
    "أنتِ كدها وربع.. لا تخلين أي شي يحبطكِ أو يقلل من ثقتكِ بنفسكِ.", "تذكري فرحة أهلج وفرحتي بيج من تنجحين وتحققين هدفكِ.",
    "المستقبل ينبني خطوة خطوة، واليوم أنتِ دا تبنين أساس قوي وثابت.", "الخوف طبيعي، بس الشجاعة إنكِ تواجهين هذا الخوف وتستمرين.",
    "كل مادة صعبة اليوم، بكرة تصير مجرد ذكرى وسالفة تضحكين عليها.", "لا تقارنين نفسج بأحد، أنتِ تمشين بطريقج الخاص وراح توصلين.",
    "التعب يروح والجهد يخلص، بس النتيجة والشهادة يبقون وياج طول العمر.", "خلي عندج إيمان كامل إن رب العالمين ما يحط حلم بقلبج إلا وتكدرين عليه.",
    "حتى لو جانت الخطوات بطيئة، المهم إنج دا تتقدمين وما واكفة بمكانج.", "كل التحديات اللي تواجهيها اليوم تصقل شخصيتج وتخليج أكثر حكمة.",
    "حلمج يستاهل منج المحاولة والتكرار، لا تملين ولا تخلين اليأس يمر ببالج.", "أنتِ نجمة وراح تظلين تلمعين مهما حاول التعب يطفيج.",
    "كل دقيقة تركيز وكل صفحة تقريها تقربج خطوة إضافية نحو الهدف.", "القوة مو إنكِ ما تتعبين، القوة إنكِ رغم التعب تكملين طريقج.",
    "اصبري شوية بعد، هانت وما بقى إلا القليل وتوصلين للقمة.", "اليوم تعب وبكرة راحة ورفعة راس، كملي علمود نفسج.",
    "أنتِ مو بس ذكية، أنتِ عندج إصرار وعزيمة تهد الجبال.", "لا تخلين لحظة يأس تمحي كل الطموح والأحلام اللي بنيتيها.",
    "تعبج هذا كله محفوظ عند رب العالمين ومستحيل يضيع.", "كلما حسيتي بضعف، تذكري ليش بديتي من الأول.",
    "أنتِ فخر لكل شخص يعرفج، كملي واثبتي للكل شكد أنتِ بطلة.", "الأشياء العظيمة تاخذ وقت، لا تستعجلين واصبري على حلمج.",
    "كل إنجاز تسوينه اليوم هو خطوة صغيرة تبني مستقبل جبير.", "ثقي بقدراتج، أنتِ عندج طاقة وقوة أكبر بهواية من اللي تتخيليها.",
    "النجاح ما يجي للي ينتظرون، يجي للي يشتغلون ويتعبون مثلكِ.", "أنتِ دا تسوين اللي عليج وأكثر، ربي يوفقج ويسهل أمرج.",
    "لا تهتمين للمحبطين، عيونج على هدفج وبس.", "كل ألم وتعب اليوم بيتحول لقوة وفخر بالمستقبل.",
    "الطموح هو اللي يخلي للحياة طعم، وأنتِ طموحج ماله حدود.", "تذكري دايمًا: 'ما ضاقت إلا لتفرج'.",
    "أنتِ كفو وتكدرين تتخطين كل هالصعوبات بامتياز.", "النجاح يليق بيج وبعيونج، لا تتنازلين عنه أبدًا.",
    "امشي بخطى ثابتة، ولا تخلين أي عثرة توقفج.", "التعب لحظي، بس الفرحة بالشهادة والنجاح أبدية.",
    "أنتِ كد كل تحدي يواجهج، ماكو شي يوكف بوجه عزيمتج.", "كلما زادت الصعوبة، كلما جان طعم النجاح أحلى.",
    "أنتِ أقوى من الظروف ومن كل شي يحاول يعطلج.", "خلي هدفج واضح كدام عيونج ولا تلتفتين لأي شي ثاني.",
    "كل خطوة تمشيها اليوم هي استثمار لمستقبلج المشرق.", "أنتِ مبدعة وتستحقين الأفضل دايمًا، كملي ولا تتراجعين.",
    "تعب اليوم هو اللي بيصنع راحتج بكرة.", "أنتِ قادرة على تغيير واقعج بجهدج وإصرارج.",
    "لا تستهينين بأي مجهود تسوينه، كل شي محسوب.", "الإصرار هو سر النجاح، وأنتِ مليانة إصرار.",
    "ابتسمي وتفائلي، بكرة أحلى بهواية من اليوم.", "أنتِ بطلة قصتج، خلي النهاية تكون عظيمة وتليق بيج.",
    "كل العقبات هي مجرد دروس تخليج أقوى وأذكى.", "القمة تنتظرج، لا ترضين بأقل منها.",
    "أنتِ دا تصنعين مجدج بنفسج، وهذا أعظم شي ممكن تسوينه.", "خلي ثقتج بنفسج تهز الجبال، أنتِ كدها.",
    "ماكو شي مستحيل كدام الإرادة القوية اللي عندج.", "كل يوم هو فرصة جديدة حتى تقربين من حلمج.",
    "أنتِ كنز، وتعبج راح يثمر نجاح يبهر الجميع.", "استمري بالقراءة والتعلم، هذا هو سلاحج الأقوى.",
    "لا تسمحين للظروف تكسرج، أنتِ أقوى منها بهواية.", "كلما تعبتي، تذكري الفرحة والابتسامة اللي بتملي وجهج يوم تخرجج.",
    "أنتِ دا تمشين بالطريق الصح، كملي بكل شجاعة.", "النجاح يحتاج صبر، وأنتِ صبورة وبطلة.",
    "أنتِ تستاهلين كل الفرح والتقدير، تعبج ماراح يروح بلاش.", "خليج دايمًا فخورة بنفسج وبكل شي دا تقدمينه.",
    "ماكو شي يجي بالسهل، بس التعب يستاهل النتيجة.", "أنتِ شعلة من النشاط والذكاء، استغليها صح.",
    "بكرة لما تسولفين عن هالأيام، بتكولين 'جانت صعبة بس كدرت عليها'.", "أنتِ دا تبنين نفسج بنفسج، وهذا كافي يخليج تفتخرين.",
    "الحلم مو بعيد، هو بس يحتاج منج شوية صبر وجهد.", "أنتِ تكدرين تحولين كل صعب إلى سهل بإرادتج.",
    "لا توكفين، الطريق بادي يخلص والقمة صارت قريبة.", "أنتِ طاقة إيجابية لكل اللي حولج، كملي بهمة عالية.",
    "تعبج اليوم هو فخر الج ولأهلج بالمستقبل.", "أنتِ مميزة، ونجاحج راح يكون مميز مثلج.",
    "كل تعب يمر بيج هو دليل إنج دا تسوين شي عظيم.", "خلي أملج بالله جبير، وهو ماراح يخيبج.",
    "أنتِ كدها اليوم وباجر وكل يوم، لا تشكين بقدراتج أبدًا.", "النجاح يبدأ بخطوة، وأنتِ مشيتي خطوات هواية.",
    "كملي طريقج وعيونج على النجوم، لا تباعين تحت.", "أنتِ تصنعين المستحيل بإصرارج وعزيمتج.",
    "التعب يزول وتبقى الذكرى الجميلة للإنجاز.", "أنتِ قوية كفاية لتخطي أي عثرة.",
    "اجتهدي اليوم، حتى تحصدين ثمار تعبج بكرة بكل فخر.", "أنتِ ذكية وتستوعبين كل شي، لا تخافين من الصعب.",
    "كل لحظة قلق بتتحول ليقين وفرح بالنجاح.", "أنتِ تستحقين القمة، لا ترضين بغيرها.",
    "عزيمتج هي قوتج الحقيقية، حافظي عليها دايمًا.", "أنتِ دا تقربين من الهدف أكثر مما تتخيلين.",
    "كل مادة تخلصينها هي انتصار صغير يوصلج للإنجاز الجبير.", "أنتِ دا تسوين شي يرفع الراس، استمري.",
    "الخوف ما يمنع الفشل بس يمنع النجاح، كوني شجاعة.", "أنتِ بطلة وتكدرين تتغلبين على كل الصعاب.",
    "حلمج يستاهل منج كل هالتعب والسهر، كملي.", "أنتِ نجمة ساطعة وراح تظلين تلمعين دايمًا.",
    "كل جهد تبذلينه اليوم هو استثمار لراحتج بكرة.", "أنتِ قادرة ومتمكنة، لا تخلين شي يضعفج.",
    "بكرة راح تبتسمين وتكولين 'الحمد لله، تعبي ما ضاع'.", "أنتِ فخر، كملي طريقج بكل ثقة واعتزاز."
]

warm_advices = [
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
    "استمتعي بالرحلة وبالتعلم، ولا تخلين النتيجة تكون هي همج الوحيد.", "كوني لطيفة ويا نفسج، أنتِ دا تبذلين جهد جبير ومستمر.",
    "الراحة مو كسل، الراحة هي جزء من العمل حتى تكدرين تكملين.", "لا تخلين كلام الناس يحبطج، أنتِ تعرفين نفسج وقدراتج زين.",
    "أنتِ قطعة من الجمال بهالدنيا، حافظي على هدوئج وسلامج الداخلي.", "كل مشكلة ولها حل، لا تكبرين المواضيع ببالج وتتعبين قلبج.",
    "خلي عندج وقت خاص بيج، تسوين بيه الأشياء اللي تحبيها وترتاحين بيها.", "أنتِ قوية بس مو لازم تكونين خارقة دايمًا، عادي تبجين وتتعبين.",
    "الحياة قصيرة، لا تضيعيها بالقلق والخوف من المجهول.", "ثقي بالله وبترتيبه لحياتج، هو دايمًا يختارلج الأفضل.",
    "خلي ابتسامتج هي أول شي تبدين بيه يومج، بتغير كل طاقتج.", "أنتِ دا تبنين مستقبلج بأيدج، وهذا أعظم استثمار تسوينه.",
    "التعب يروح بس الفخر بالإنجاز يبقى وياج طول العمر.", "لا تنسين تتنفسين بعمق من فترة لفترة، وتهدين بالج.",
    "أنتِ غالية على قلبي هواية، وصحتج وراحتج هي أولويتي الأولى.", "استمري بكل هدوء وثقة، القادم أجمل بهواية مما تتوقعين."
]

love_letters = [
    "إلى من أحب وأعشق.. عيونكِ هي أماني بهالدنيا، وكل ما أحس بضيق أتذكر ضحكتكِ وأرتاح.", "أنتِ مو بس حبيبتي، أنتِ راحتي وملجئي اللي أهرب له من تعب هالعالم.",
    "لو تدرين شكد أحبكِ وشكد غالية على قلبي، كان ما شلتي هم لشي أبدًا.", "وجودكِ بحياتي هو النعمة اللي أشكر ربي عليها كل يوم.. ربي يوفقكِ.",
    "كل تفاصيلج تهمني، ضحكتج، زعلج، عيونج.. أنتِ كل حياتي واهتمامي.", "أحبج بكل حالاتج، بتعبج، بقوتج، بضعفج.. أنتِ دايمًا الأجمل بعيوني.",
    "أنتِ الشخص الوحيد اللي يكدر يغير مزاجي بكلمة وحدة.. ربي يحفظج لي.", "مهما جرتنا الأيام وشغلتنا الظروف، مكانج بقلبي ثابت وما يتغير أبدًا.",
    "أنتِ أملي وفرحتي بهالدنيا، من أشوفج مرتاحة وناجحة أحس الدنيا بخير.", "يا بعد روحي وعمري، تعبج هو تعبي، وفرحتج هي فرحتي.. أحبج هواية.",
    "كلما أتذكر إنج وياي بحياتي، أحمد ربي وأبوس إيدي وجه وظهر على هالنعمة.", "أنتِ عيونج قصة جمال، وضحكتج تنسيني كل هموم الدنيا وتعبها.",
    "يا أغلى من الهوى على قلبي، ربي لا يحرمني منج ومن طيبة قلبج الدافية.", "أنتِ مو بس شريكة حياتي، أنتِ صديقتي وحبيبتي وكل ناسي.",
    "كل دعوة أدعيها لروحي، الج نصيب الأسد منها.. ربي يحميج ويسعدج دايمًا.", "أحبج حب ماله نهاية، حب يكبر ويا كل يوم يمر واحنا سوة.",
    "أنتِ النور اللي يضوي أيامي المظلمة، والملجأ اللي أرتاح بيه من كل شي.", "يا بعد كل ناسي، قربج مني يخليني أحس إني أملك الدنيا وما بيها.",
    "أنتِ أجمل صدفة بحياتي، وأجمل هدية كرمني بيها رب العالمين.", "عيونج أمان، وحضنج وطن، وضحكتج حياة كاملة بالنسبة لي.. أحبج.",
    "أنتِ راحتي النفسية، وكل ما أحس بتعب بس أسمع صوتج كل شي يطيب.", "يا عمري وروحي، ربي يكتبلج النجاح والتوفيق بكل خطوة تمشيها.",
    "أنتِ بقلبي دايمًا، حتى لو جُبرنا نبتعد مسافات، الروح قريبة من الروح.", "يا كل دنيتي، أتمنى أكدر أشيل كل التعب عنج وأخليج بس تبتسمين.",
    "أنتِ غالية لدرجة ما تتخيليها، وماكو شي بهالدنيا يعوضني عن وجودج.", "أحبج بكد النجوم وبكد كل كلمة حب انقالت من بداية الدنيا لحد الآن.",
    "أنتِ حلمي اللي تحقق، وراح أظل أحافظ عليج وأحبج لآخر نفس بيا.", "يا روحي، ثقي إني بظهرج دايمًا، وما راح أتخلى عنج لو شنو ما يصير.",
    "أنتِ دواي من كل ضيق، وبلسم لكل جرح.. ربي يخليج لي طول العمر.", "إلى من أحب وأعشق.. أنتِ الأولى والأخيرة بقلبي، ومحد ياخذ مكانج أبدًا."
]

fixed_verses = [
    "﴿اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ﴾",
    "﴿قُلْ أَعُوذُ بِرَبِّ النَّاسِ﴾"
]

variable_verses = [
    "﴿إِنَّ مَعَ الْعُسْرِ يُسْرًا﴾", "﴿وَأَن لَّيْسَ لِلْإِنسَانِ إِلَّا مَا سَعَىٰ﴾", "﴿فَإِنِّي قَرِيبٌ ۖ أُجِيبُ دَعْوَةَ الدَّاعِ﴾",
    "﴿وَقُل رَّبِّ زِدْنِي عِلْمًا﴾", "﴿لَا تَحْزَنْ إِنَّ اللَّهَ مَعَنَا﴾", "﴿وَمَن يَتَوَكَّلْ عَلَى اللَّهِ فَهُوَ حَسْبُهُ﴾",
    "﴿وَاصْبِرْ لِحُكْمِ رَبِّكَ فَإِنَّكَ بِأَعْيُنِنَا﴾", "﴿قُلْ هُوَ اللَّهُ أَحَدٌ﴾", "﴿اللَّهُ الصَّمَدُ﴾",
    "﴿قُلْ أَعُوذُ بِرَبِّ الْفَلَقِ﴾", "﴿وَتَوَكَّلْ عَلَى الْحَيِّ الَّذِي لَا يَمُوتُ﴾", "﴿أَلَا بِذِكْرِ اللَّهِ تَطْمَئِنُّ الْقُلُوبُ﴾",
    "﴿رَبِّ اشْرَحْ لِي صَدْرِي﴾", "﴿وَيَسِّرْ لِي أَمْرِي﴾", "﴿إِنَّ اللَّهَ عَلَىٰ كُلِّ شَيْءٍ قَدِيرٌ﴾",
    "﴿وَقَالَ رَبُّكُمُ ادْعُونِي أَسْتَجِبْ لَكُمْ﴾", "﴿فَاصْبِرْ صَبْرًا جَمِيلًا﴾", "﴿وَاصْبِرْ وَمَا صَبْرُكَ إِلَّا بِاللَّهِ﴾",
    "﴿وَإِذَا سَأَلَكَ عِبَادِي عَنِّي فَإِنِّي قَرِيبٌ﴾", "﴿يَسْتَبْشِرُونَ بِنِعْمَةٍ مِّنَ اللَّهِ وَفَضْلٍ﴾", "﴿وَكَانَ فَضْلُ اللَّهِ عَلَيْكَ عَظِيمًا﴾",
    "﴿وَمَا تَوْفِيقِي إِلَّا بِاللَّهِ ۚ عَلَيْهِ تَوَكَّلْتُ﴾", "﴿وَآتَاكُم مِّن كُلِّ مَا سَأَلْتُمُوهُ﴾", "﴿وَمَا رَبُّكَ بِظَلَّامٍ لِّلْعَبِيدِ﴾",
    "﴿إِنَّ رَبِّي لَطِيفٌ لِّمَا يَشَاءُ﴾", "﴿وَهُوَ مَعَكُمْ أَيْنَ مَا كُنتُمْ﴾", "﴿إِنَّ اللَّهَ مَعَ الَّذِينَ اتَّقَوا﴾",
    "﴿لَا تَدْرِي لَعَلَّ اللَّهَ يُحْدِثُ بَعْدَ ذَٰلِكَ أَمْرًا﴾", "﴿وَلَسَوْفَ يُعْطِيكَ رَبُّكَ فَتَرْضَىٰ﴾", "﴿وَاللَّهُ يَعْلَمُ وَأَنتُمْ لَا تَعْلَمُونَ﴾",
    "﴿قَدْ جَعَلَ اللَّهُ لِكُلِّ شَيْءٍ قَدْرًا﴾", "﴿فَسَيَكْفِيكَهُمُ اللَّهُ ۚ وَهُوَ السَّمِيعُ الْعَلِيمُ﴾", "﴿رَبِّ لَا تَذَرْنِي فَرْدًا﴾",
    "﴿إِنَّ اللَّهَ لَا يُضِيعُ أَجْرَ الْمُحْسِنِينَ﴾", "﴿وَرَحْمَتِي وَسِعَتْ كُلَّ شَيْءٍ﴾", "﴿وَإِن تَعُدُّوا نِعْمَةَ اللَّهِ لَا تُحْصُوهَا﴾",
    "﴿وَهُوَ عَلَىٰ كُلِّ شَيْءٍ قَدِيرٌ﴾", "﴿فَاصْبِرْ إِنَّ وَعْدَ اللَّه حق﴾", "﴿وَمَا كَانَ اللَّهُ لِيُعْجِزَهُ مِن شَيْءٍ﴾",
    "﴿وَسَيَجْزِي اللَّهُ الشَّاكِرِينَ﴾", "﴿إِنَّا لَا نُضِيعُ أَجْرَ مَنْ أَحْسَنَ عَمَلًا﴾", "﴿وَاللَّهُ يَخْتَصُّ بِرَحْمَتِهِ مَن يَشَاءُ﴾",
    "﴿وَمَا خَلَقْتُ الْجِنَّ وَالْإِنسَ إِلَّا لِيَعْبُدُونِ﴾", "﴿قُلِ اللَّهُ يُنَجِّيكُم مِّنْهَا﴾", "﴿وَهُوَ الْغَفُورُ الرَّحِيمُ﴾",
    "﴿وَاللَّهُ مَعَ الصَّابِرِينَ﴾"
]

if "daily_quote" not in st.session_state:
    st.session_state.daily_quote = random.choice(motivational_quotes)
    st.session_state.daily_advice = random.choice(warm_advices)
    st.session_state.love_letter = random.choice(love_letters)
    st.session_state.daily_verses = fixed_verses + random.sample(variable_verses, 2)

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
        st.session_state.daily_quote = random.choice(motivational_quotes)
        st.session_state.daily_advice = random.choice(warm_advices)
        st.session_state.love_letter = random.choice(love_letters)
        st.session_state.daily_verses = fixed_verses + random.sample(variable_verses, 2)
        st.rerun()

with tabs[1]:
    st.markdown(f"""
    <div class='warm-box'>
        <h3 style='text-align: center; color: #ff7b54 !important;'>💌 رسالة خاصة لعيونكِ <span class='code-badge'>247</span></h3>
        <p class='warm-advice-text'>"{st.session_state.daily_advice}"</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("💝 استلام نصيحة دافئة جديدة"):
        st.session_state.daily_advice = random.choice(warm_advices)
        st.rerun()

with tabs[2]:
    st.markdown(f"""
    <div class='love-box'>
        <h3 style='text-align: center; color: #ff2e63 !important;'>💝 رسالة حب واطمئنان <span class='code-badge'>247</span></h3>
        <p class='love-letter-text'>"{st.session_state.love_letter}"</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("💘 قراءة رسالة حب جديدة"):
        st.session_state.love_letter = random.choice(love_letters)
        st.rerun()

with tabs[3]:
    st.markdown("### 📂 تحويل النصوص والصور إلى ملف PDF")
    st.info("✅ يدعم الآن النص العربي بشكل صحيح (الحروف متصلة واتجاه RTL)")
    
    text_input = st.text_area("أدخل النص الذي تريد إضافته إلى ملف PDF:", height=150, placeholder="اكتب النص هنا...")
    uploaded_images = st.file_uploader("قم برفع الصور (JPG, PNG) لدمجها في الـ PDF:", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True)

    if st.button("توليد ملف الـ PDF"):
        if not text_input and not uploaded_images:
            st.error("الرجاء إدخال نص أو رفع صورة واحدة على الأقل!")
        else:
            try:
                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
                from reportlab.lib.styles import ParagraphStyle
                from reportlab.lib.pagesizes import A4

                pdf_buffer = io.BytesIO()
                doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)

                arabic_style = ParagraphStyle(name='ArabicStyle', fontName='dejavusans', fontSize=13, leading=22, alignment=2, rightIndent=5)
                story = []

                if text_input:
                    for line in text_input.split('\n'):
                        if line.strip():
                            processed_line = prepare_arabic(line.strip())
                            story.append(Paragraph(processed_line, arabic_style))
                            story.append(Spacer(1, 6))
                    story.append(Spacer(1, 15))

                if uploaded_images:
                    for uploaded_img in uploaded_images:
                        img = Image.open(uploaded_img)
                        img_width, img_height = img.size
                        aspect = img_height / float(img_width)
                        display_width = 480
                        display_height = 480 * aspect

                        img_buf = io.BytesIO()
                        img.save(img_buf, format="PNG")
                        img_buf.seek(0)

                        rl_img = RLImage(img_buf, width=display_width, height=display_height)
                        story.append(rl_img)
                        story.append(Spacer(1, 15))

                doc.build(story)
                pdf_data = pdf_buffer.getvalue()

                st.success("✅ تم إنشاء ملف الـ PDF بنجاح!")
                st.download_button(label="⬇️ اضغط هنا لتنزيل ملف الـ PDF", data=pdf_data, file_name="Inspiration_Doc.pdf", mime="application/pdf")
            except Exception as e:
                st.error(f"حدث خطأ أثناء إنشاء الملف: {e}")

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888888;'>تم التطوير بواسطة شيماء علي عبد الحسين | v1.3 | 247</p>", unsafe_allow_html=True)
