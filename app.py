#!/usr/bin/env python3
"""
Telegram Bot - النسخة المصححة والمضمونة
"""

import os
import logging
import platform
import psutil
from datetime import datetime

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("TelegramBot")

class TelegramBot:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.token:
            raise Exception("❌ TELEGRAM_BOT_TOKEN مطلوب")
        
        self.users = {}
        logger.info("✅ البوت مهيأ")
    
    def setup_handlers(self, dispatcher):
        """إعداد معالجات الأوامر"""
        from telegram.ext import CommandHandler, MessageHandler, Filters
        
        # الأوامر
        dispatcher.add_handler(CommandHandler("start", self.handle_start))
        dispatcher.add_handler(CommandHandler("help", self.handle_help))
        dispatcher.add_handler(CommandHandler("status", self.handle_status))
        dispatcher.add_handler(CommandHandler("ping", self.handle_ping))
        
        # الرسائل العادية
        dispatcher.add_handler(MessageHandler(Filters.text, self.handle_message))
    
    def handle_start(self, update, context):
        """معالجة أمر /start"""
        user = update.message.from_user
        user_id = str(user.id)
        
        self.users[user_id] = {
            'name': user.first_name or 'مستخدم',
            'username': user.username or 'لا يوجد',
            'start_time': datetime.now().isoformat(),
            'message_count': 0
        }
        
        welcome = f"""
🎉 **مرحباً {user.first_name}!**

🤖 **البوت يعمل بنجاح على Render**

✅ **النشر ناجح!**

**الأوامر المتاحة:**
/start - هذه الرسالة
/help - المساعدة
/status - حالة النظام
/ping - فحص الاتصال

💡 **اكتب أي رسالة للتفاعل**
        """
        
        update.message.reply_text(welcome)
        logger.info(f"مستخدم جديد: {user.first_name} (ID: {user_id})")

    def handle_help(self, update, context):
        """معالجة أمر /help"""
        help_text = """
🆘 **مركز المساعدة**

**الأوامر:**
• /start - بدء البوت
• /help - عرض هذه الرسالة
• /status - معلومات النظام
• /ping - فحص الاتصال

**معلومات التقنية:**
• يعمل على Render.com
• Python 3.10+
• نسخة مستقرة 100%

🔧 **كل شيء يعمل بشكل مثالي!**
        """
        
        update.message.reply_text(help_text)

    def handle_status(self, update, context):
        """معالجة أمر /status"""
        try:
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            status_text = f"""
📊 **حالة النظام**

**🖥️ الخادم:**
• النظام: {platform.system()} {platform.release()}
• الذاكرة: {memory.percent}% مستخدم
• التخزين: {disk.percent}% مستخدم

**🤖 البوت:**
• المستخدمين: {len(self.users)}
• الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**✅ الحالة: ممتازة**
            """
            
            update.message.reply_text(status_text)
            
        except Exception as e:
            update.message.reply_text(f"❌ خطأ في الحصول على الحالة: {e}")

    def handle_ping(self, update, context):
        """معالجة أمر /ping"""
        update.message.reply_text("🏓 **pong!**\n\n✅ البوت يعمل بشكل ممتاز!")
        
        # تسجيل النشاط
        user_id = str(update.message.from_user.id)
        if user_id in self.users:
            self.users[user_id]['message_count'] += 1

    def handle_message(self, update, context):
        """معالجة الرسائل العادية"""
        user = update.message.from_user
        user_id = str(user.id)
        text = update.message.text
        
        # تحديث إحصائيات المستخدم
        if user_id in self.users:
            self.users[user_id]['message_count'] += 1
        else:
            self.users[user_id] = {
                'name': user.first_name or 'مستخدم',
                'start_time': datetime.now().isoformat(),
                'message_count': 1
            }
        
        # ردود ذكية
        responses = [
            f"👋 مرحباً {user.first_name}! جرب /help لرؤية الأوامر",
            "💡 أنا هنا لمساعدتك!",
            "🤖 هذا بوت تلقرام يعمل على Render",
            f"🔍 لقد أرسلت: {text[:50]}...",
            "🎯 جرب الأمر /status لرؤية حالة النظام"
        ]
        
        # اختيار رد عشوائي
        import random
        response = random.choice(responses)
        
        update.message.reply_text(response)
        logger.info(f"رسالة من {user.first_name}: {text[:30]}...")

    def run(self):
        """تشغيل البوت"""
        from telegram.ext import Updater
        
        logger.info("🚀 بدء تشغيل البوت...")
        
        # استخدام Updater بالطريقة الصحيحة للإصدار 13.7
        updater = Updater(self.token, use_context=True)
        dispatcher = updater.dispatcher
        
        # إعداد المعالجات
        self.setup_handlers(dispatcher)
        
        # البدء
        updater.start_polling()
        logger.info("✅ البوت يعمل الآن على Render!")
        
        # البقاء في الحلقة
        updater.idle()

def main():
    """الدالة الرئيسية"""
    try:
        logger.info("=== بدء تشغيل تطبيق Telegram Bot ===")
        
        # فحص المتغيرات البيئية
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not token:
            logger.error("❌ TELEGRAM_BOT_TOKEN غير معروف")
            return
        
        logger.info(f"✅ Token موجود: {token[:10]}...")
        
        # فحص المتطلبات
        try:
            import telegram
            logger.info(f"✅ telegram version: {telegram.__version__}")
        except ImportError as e:
            logger.error(f"❌ حزمة telegram غير مثبتة: {e}")
            return
        
        # تشغيل البوت
        bot = TelegramBot()
        bot.run()
        
    except Exception as e:
        logger.error(f"❌ خطأ رئيسي: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()
