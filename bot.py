import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

# إعدادات التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# طريقة محكمة لتحميل التوكن
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

# ... (بقية الكود كما في الإصدار السابق مع دوال start و handle_message)

def main():
    try:
        app = ApplicationBuilder() \
            .token(TOKEN) \
            .post_init(lambda _: logger.info("✅ البوت جاهز للعمل")) \
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
