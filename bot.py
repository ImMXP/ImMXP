import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackContext
)

# إعدادات التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# تحميل التوكن
def load_token():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("""
        [خطأ حرج] لم يتم العثور على التوكن!
        تأكد من:
        1. وجود ملف .env محليًا يحتوي على TELEGRAM_BOT_TOKEN
        2. وجود متغير بيئة TELEGRAM_BOT_TOKEN على Render
        3. أن القيمة لا تحتوي على مسافات قبل/بعد
        """)
        raise RuntimeError("توكن البوت غير معين")
    logger.info(f"تم تحميل التوكن (الأحرف الأولى): {token[:4]}****")
    return token

TOKEN = load_token()

# القوائم والنصوص
MAIN_MENU = [
    ["آيات الصباح 🌅", "آيات المساء 🌙"],
    ["آيات السكينة 🕊️", "آيات التوبة 🙏"],
    ["تلاوات مختارة 🎧", "المشايخ المفضلين 🎙️"]
]

VERSES = {
    "آيات الصباح 🌅": "آية الكرسي: اللّهُ لاَ إِلَـهَ إِلاَّ هُوَ الْحَيُّ الْقَيُّومُ...",
    "آيات المساء 🌙": "سورة الإخلاص: قُلْ هُوَ اللَّهُ أَحَدٌ...",
    "آيات السكينة 🕊️": "الرعد:28: أَلَا بِذِكْرِ اللَّهِ تَطْمَئِنُّ الْقُلُوبُ",
    "آيات التوبة 🙏": "النور:31: وَتُوبُوا إِلَى اللَّهِ جَمِيعًا",
    "تلاوات مختارة 🎧": "سيتم إضافة تلاوات قريبًا إن شاء الله",
    "المشايخ المفضلين 🎙️": "سيتم إضافة المشايخ قريبًا إن شاء الله"
}

# تعريف الدوال
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج أمر /start"""
    user = update.effective_user
    logger.info(f"المستخدم {user.id} بدأ التشغيل")
    
    reply_markup = ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True)
    await update.message.reply_text(
        f"مرحباً بك {user.first_name} في بوت القرآن الكريم 🌿\n"
        "اختر من القائمة أدناه:",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج الرسائل النصية"""
    text = update.message.text
    user = update.effective_user
    
    if text in VERSES:
        logger.info(f"المستخدم {user.id} اختار: {text}")
        await update.message.reply_text(VERSES[text])
    else:
        logger.warning(f"المستخدم {user.id} أرسل نص غير معروف: {text}")
        await update.message.reply_text("لم أفهم طلبك، يرجى استخدام القائمة")

async def post_init(app):
    """دالة ما بعد التهيئة"""
    logger.info("✅ البوت جاهز للعمل")

def main() -> None:
    """الدالة الرئيسية"""
    try:
        app = ApplicationBuilder() \
            .token(TOKEN) \
            .post_init(post_init) \  # تم التصحيح هنا
            .build()
            
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        logger.info("جاري تشغيل البوت...")
        app.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        )
        
    except Exception as e:
        logger.critical(f"انهيار التطبيق: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
