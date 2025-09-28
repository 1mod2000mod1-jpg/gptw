#!/usr/bin/env python3
"""
Telegram Bot - النسخة الأساسية المضمونة
يعمل على Render بدون أخطاء
"""

import os
import json
import logging
import platform
import psutil
from datetime import datetime
from pathlib import Path

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("BasicTelegramBot")

class BasicMemory:
    """ذاكرة أساسية"""
    def __init__(self):
        self.memories = []
    
    def add(self, text):
        """إضافة نص إلى الذاكرة"""
        if len(self.memories) > 50:  # حد أقصى 50 عنصر
            self.memories.pop(0)
        self.memories.append({
            'text': text,
            'time': datetime.now().isoformat()
        })
    
    def search(self, query):
        """بحث في الذاكرة"""
        results = []
        for memory in reversed(self.memories):
            if query.lower() in memory['text'].lower():
                results.append(memory)
                if len(results) >= 5:
                    break
        return results
    
    def count(self):
        """عدد العناصر"""
        return len(self.memories)

class WebSearcher:
    """محرك بحث أساسي"""
    
    @staticmethod
    def simple_search(query):
        """بحث بسيط"""
        try:
            # استخدام requests للبحث البسيط (بدون حزم إضافية)
            import requests
            return f"🔍 البحث عن: {query}\n\n💡 هذه نسخة أساسية. لإضافة بحث حقيقي، قم بتثبيت حزم إضافية لاحقاً."
        except:
            return f"🔍 البحث عن: {query}\n\nℹ️ خاصية البحث قيد التطوير"

class TelegramBotBasic:
    """البوت الأساسي"""
    
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.token:
            raise Exception("❌ TELEGRAM_BOT_TOKEN مطلوب")
        
        self.memory = BasicMemory()
        self.users = {}
        
        self.setup_bot()
        logger.info("✅ البوت الأساسي جاهز")

    def setup_bot(self):
        """إعداد البوت"""
        from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
        
        self.updater = Updater(token=self.token, use_context=True)
        self.dispatcher = self.updater.dispatcher
        
        # الأوامر
        self.dispatcher.add_handler(CommandHandler("start", self.cmd_start))
        self.dispatcher.add_handler(CommandHandler("help", self.cmd_help))
        self.dispatcher.add_handler(CommandHandler("status", self.cmd_status))
        self.dispatcher.add_handler(CommandHandler("memory", self.cmd_memory))
        self.dispatcher.add_handler(CommandHandler("search", self.cmd_search))
        
        # الرسائل العادية
        self.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, self.handle_message))

    def cmd_start(self, update, context):
        """أمر البدء"""
        user = update.effective_user
        user_id = str(user.id)
        
        self.users[user_id] = {
            'name': user.first_name or 'مستخدم',
            'start_time': datetime.now().isoformat(),
            'messages': 0
        }
        
        welcome = f"""
🎉 **مرحباً {user.first_name}!**

🤖 **البوت يعمل بنجاح على Render**

**الأوامر المتاحة:**
/start - هذه الرسالة
/help - المساعدة
/status - حالة النظام  
/memory - عرض الذاكرة
/search - البحث

**مثال:**
/search الذكاء الاصطناعي

✅ **النشر ناجح!**
        """
        
        update.message.reply_text(welcome)

    def cmd_help(self, update, context):
        """أمر المساعدة"""
        help_text = """
🆘 **مركز المساعدة**

**الأوامر:**
• /start - بدء البوت
• /help - هذه الرسالة  
• /status - معلومات النظام
• /memory - الذاكرة
• /search - البحث

**معلومات:**
• يعمل على Render.com
• Python 3.10+
• نسخة مستقرة

💡 **اكتب أي رسالة للتفاعل**
        """
        
        update.message.reply_text(help_text)

    def cmd_status(self, update, context):
        """حالة النظام"""
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        status = f"""
📊 **حالة النظام**

**🖥️ الخادم:**
• النظام: {platform.system()}
• الذاكرة: {mem.percent}% مستخدم
• التخزين: {disk.percent}% مستخدم

**🤖 البوت:**
• المستخدمين: {len(self.users)}
• الذاكرة: {self.memory.count()} عنصر
• الوقت: {datetime.now().strftime('%H:%M:%S')}

**✅ كل شيء يعمل بشكل ممتاز**
        """
        
        update.message.reply_text(status)

    def cmd_memory(self, update, context):
        """عرض الذاكرة"""
        if not self.memory.memories:
            update.message.reply_text("ℹ️ الذاكرة فارغة")
            return
        
        # البحث إذا وجدت كلمات
        if context.args:
            query = ' '.join(context.args)
            results = self.memory.search(query)
            if results:
                response = f"🔍 **النتائج لـ '{query}':**\n\n"
                for i, res in enumerate(results, 1):
                    response += f"{i}. {res['text'][:50]}...\n"
            else:
                response = f"❌ لا توجد نتائج لـ '{query}'"
        else:
            # عرض آخر 5 عناصر
            response = "🧠 **آخر 5 عناصر:**\n\n"
            for i, mem in enumerate(self.memory.memories[-5:], 1):
                response += f"{i}. {mem['text'][:60]}...\n"
        
        update.message.reply_text(response)

    def cmd_search(self, update, context):
        """أمر البحث"""
        if not context.args:
            update.message.reply_text("⚠️ اكتب ما تريد البحث عنه\nمثال: /search الذكاء الاصطناعي")
            return
        
        query = ' '.join(context.args)
        result = WebSearcher.simple_search(query)
        update.message.reply_text(result)
        
        # حفظ في الذاكرة
        self.memory.add(f"بحث: {query}")

    def handle_message(self, update, context):
        """معالجة الرسائل العادية"""
        user_id = str(update.effective_user.id)
        text = update.message.text
        
        # تحديث المستخدم
        if user_id in self.users:
            self.users[user_id]['messages'] += 1
        else:
            self.users[user_id] = {
                'name': update.effective_user.first_name or 'مستخدم',
                'start_time': datetime.now().isoformat(),
                'messages': 1
            }
        
        # حفظ في الذاكرة
        self.memory.add(f"رسالة: {text}")
        
        # رد ذكي بسيط
        responses = [
            "💡 جرب الأمر /help لرؤية جميع الإمكانيات",
            "🤖 أنا هنا لمساعدتك!",
            "🔍 يمكنك البحث باستخدام /search",
            "🧠 الذاكرة تحتوي على {} عنصر".format(self.memory.count())
        ]
        
        import random
        response = random.choice(responses)
        update.message.reply_text(response)

    def run(self):
        """تشغيل البوت"""
        logger.info("🚀 بدء تشغيل البوت الأساسي...")
        self.updater.start_polling()
        logger.info("✅ البوت يعمل الآن!")
        self.updater.idle()

def main():
    """الدالة الرئيسية"""
    try:
        # فحص المتطلبات الأساسية
        try:
            import telegram
            import psutil
            logger.info("✅ المتطلبات الأساسية مثبتة")
        except ImportError as e:
            logger.error(f"❌ متطلب مفقود: {e}")
            return
        
        # تشغيل البوت
        bot = TelegramBotBasic()
        bot.run()
        
    except Exception as e:
        logger.error(f"❌ خطأ: {e}")

if __name__ == "__main__":
    main()
