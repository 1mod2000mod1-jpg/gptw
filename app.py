#!/usr/bin/env python3
import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# المتغيرات
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('🎉 **أهلاً! البوت يعمل بنجاح!**\n\n✅ النشر على Render ناجح!\n\n💡 جرب /help')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
🆘 **الأوامر المتاحة:**
/start - بدء البوت
/help - هذه الرسالة  
/ping - فحص الاتصال
/status - حالة الخادم

🔧 **يعمل على Render.com**
    """
    await update.message.reply_text(help_text)

async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('🏓 **pong!**\n\n✅ البوت يعمل بشكل ممتاز!')

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    import psutil
    memory = psutil.virtual_memory()
    status_text = f"""
📊 **حالة الخادم:**
• الذاكرة: {memory.percent}% مستخدم
• النظام: يعمل بشكل طبيعي
• البوت: نشط ✅
    """
    await update.message.reply_text(status_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text(f'📩 رسالتك: "{text}"\n\n💡 استخدم /help للأوامر')

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f'خطأ: {context.error}')

def main():
    if not BOT_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN غير معروف")
        return

    # إنشاء التطبيق
    application = Application.builder().token(BOT_TOKEN).build()

    # إضافة المعالجات
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ping", ping_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)

    # البدء
    logger.info("🚀 بدء تشغيل البوت...")
    application.run_polling()
    logger.info("✅ البوت يعمل!")

if __name__ == "__main__":
    main()
