from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    filters,  # تم تغيير Filters إلى filters بحرف صغير
    CallbackContext,
    ApplicationBuilder  # أضيف لدعم الإصدارات الحديثة
)
from dotenv import load_dotenv
import os
import logging  # أضيف لتفعيل نظام التسجيل

# تفعيل نظام التسجيل لرؤية الأخطاء
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# تحميل التوكين من ملف .env
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    TOKEN = "ضع_التوكن_هنا_مباشرة"  # فقط للاختبار المؤقت!
    print("⚠️ تحذير: يتم استخدام توكن من الكود مباشرة")

print("="*50)
print(f"قيمة TOKEN: {TOKEN[:10]}...")  # عرض جزء من التوكن لأمانه
print("="*50)

# القائمة الرئيسية
main_menu_keyboard = [
    ["آيات الصباح 🌅", "آيات المساء 🌙"],
    ["آيات السكينة 🕊️", "آيات التوبة 🙏"],
    ["تلاوات مختارة 🎧", "المشايخ المفضلين 🎙️"]
]

async def start(update: Update, context: CallbackContext) -> None:
    """Handler لآمر /start"""
    reply_markup = ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "مرحباً بك في بوت القرآن الكريم 🌿\n"
        "اختر من القائمة أدناه:",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: CallbackContext) -> None:
    """Handler للرسائل النصية"""
    text = update.message.text
    response = ""

    if text == "آيات الصباح 🌅":
        response = "«أَعُوذُ بِاللَّهِ مِنَ الشَّيْطَانِ الرَّجِيمِ»\n\n" \
                   "اللّهُ لاَ إِلَـهَ إِلاَّ هُوَ الْحَيُّ الْقَيُّومُ لاَ تَأْخُذُهُ سِنَةٌ وَلاَ نَوْمٌ... (آية الكرسي)"
    
    elif text == "آيات المساء 🌙":
        response = "«أَعُوذُ بِاللَّهِ مِنَ الشَّيْطَانِ الرَّجِيمِ»\n\n" \
                   "قُلْ هُوَ اللَّهُ أَحَدٌ، اللَّهُ الصَّمَدُ... (الإخلاص والفلق والناس)"
    
    elif text == "آيات السكينة 🕊️":
        response = "«الَّذِينَ آمَنُوا وَتَطْمَئِنُّ قُلُوبُهُم بِذِكْرِ اللَّهِ ۗ أَلَا بِذِكْرِ اللَّهِ تَطْمَئِنُّ الْقُلُوبُ» (الرعد:28)"
    
    elif text == "آيات التوبة 🙏":
        response = "«وَتُوبُوا إِلَى اللَّهِ جَمِيعًا أَيُّهَ الْمُؤْمِنُونَ لَعَلَّكُمْ تُفْلِحُونَ» (النور:31)"
    
    elif text == "تلاوات مختارة 🎧":
        response = "سيتم إضافة تلاوات مختارة قريباً إن شاء الله."
    
    elif text == "المشايخ المفضلين 🎙️":
        response = "سيتم إضافة قائمة بالمشايخ المفضلين قريباً."

    if response:
        await update.message.reply_text(response)


def main() -> None:
    """الدالة الرئيسية لتشغيل البوت"""
    # إنشاء التطبيق باستخدام Builder
    application = ApplicationBuilder().token(TOKEN).build()
    
    # إضافة الـ Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # تشغيل البوت
    print("جارٍ تشغيل البوت...")
    application.run_polling()

if __name__ == "__main__":
    main()
