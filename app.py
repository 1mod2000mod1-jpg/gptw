#!/usr/bin/env python3
"""
Telegram Auto-GPT Bot - النسخة النهائية المتوافقة مع Render
إصدار مبسط ومستقر 100%
"""

import os
import json
import logging
import platform
import psutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("StableTelegramBot")

class SimpleMemorySystem:
    """نظام ذاكرة مبسط جداً"""
    
    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path
        self.memory_file = workspace_path / "simple_memory.json"
        self.memories: List[Dict] = []
        self.load_memories()

    def load_memories(self):
        """تحميل الذكريات"""
        try:
            if self.memory_file.exists():
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    self.memories = json.load(f)
        except Exception as e:
            logger.info("ℹ️ لا توجد ذاكرة سابقة، بدء جديد")

    def add_memory(self, content: str, memory_type: str = "general"):
        """إضافة ذاكرة جديدة"""
        memory_item = {
            'content': content,
            'type': memory_type,
            'timestamp': datetime.now().isoformat(),
            'summary': content[:80] + "..." if len(content) > 80 else content
        }
        self.memories.append(memory_item)
        
        # الحفاظ على حد أقصى للذاكرة
        if len(self.memories) > 100:
            self.memories = self.memories[-100:]
            
        self.save_memories()

    def search_memories(self, query: str, limit: int = 5) -> List[Dict]:
        """بحث بسيط في الذاكرة"""
        query = query.lower()
        results = []
        for memory in reversed(self.memories):
            if query in memory['content'].lower():
                results.append(memory)
                if len(results) >= limit:
                    break
        return results

    def save_memories(self):
        """حفظ الذكريات"""
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.memories, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"❌ خطأ في حفظ الذاكرة: {e}")

    def __len__(self):
        return len(self.memories)

class DuckDuckGoSearcher:
    """محرك بحث مبسط باستخدام DuckDuckGo"""
    
    @staticmethod
    def search(query: str, max_results: int = 3) -> List[Dict]:
        """البحث على الويب"""
        try:
            from duckduckgo_search import DDGS
            
            results = []
            with DDGS() as ddgs:
                for result in ddgs.text(query, max_results=max_results):
                    results.append({
                        'title': result.get('title', 'No title'),
                        'url': result.get('href', ''),
                        'description': result.get('body', '')[:150] + '...'
                    })
            return results
        except Exception as e:
            logger.error(f"❌ خطأ في البحث: {e}")
            return []

class StableTelegramBot:
    """البوت المستقر والمتوافق"""
    
    def __init__(self):
        # التحقق من المتغيرات البيئية
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        
        if not self.telegram_token:
            raise Exception("❌ يرجى تعيين TELEGRAM_BOT_TOKEN")
        
        # مساحة العمل على Render
        self.workspace_base = Path("/tmp/telegram_bot")
        self.workspace_base.mkdir(parents=True, exist_ok=True)
        
        # الأنظمة
        self.memory = SimpleMemorySystem(self.workspace_base)
        self.user_sessions: Dict[str, Dict] = {}
        
        self.setup_bot()
        logger.info("✅ البوت مهيأ للعمل")

    def setup_bot(self):
        """إعداد البوت"""
        from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
        
        self.updater = Updater(token=self.telegram_token, use_context=True)
        self.dispatcher = self.updater.dispatcher
        
        # إضافة معالجات الأوامر
        self.setup_handlers()

    def setup_handlers(self):
        """إعداد معالجات الأوامر"""
        # الأوامر الأساسية
        self.dispatcher.add_handler(CommandHandler("start", self.handle_start))
        self.dispatcher.add_handler(CommandHandler("help", self.handle_help))
        self.dispatcher.add_handler(CommandHandler("search", self.handle_search))
        self.dispatcher.add_handler(CommandHandler("memory", self.handle_memory))
        self.dispatcher.add_handler(CommandHandler("status", self.handle_status))
        self.dispatcher.add_handler(CommandHandler("clear", self.handle_clear))
        
        # معالجة الرسائل النصية
        self.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, self.handle_message))

    def handle_start(self, update, context):
        """معالجة أمر البدء"""
        user = update.effective_user
        user_id = str(user.id)
        
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {
                'start_time': datetime.now().isoformat(),
                'message_count': 0,
                'username': user.username or user.first_name or 'مستخدم'
            }
        
        welcome_text = f"""
🤖 **مرحباً {user.first_name}!**

🎯 **البوت يعمل بنجاح على Render!**

**الأوامر المتاحة:**
/start - عرض هذه الرسالة
/help - المساعدة
/search [كلمات] - البحث على الويب
/memory [كلمات] - البحث في الذاكرة
/status - حالة النظام
/clear - مسح الذاكرة

**مثال:**
/search الذكاء الاصطناعي
/memory مشروع

💡 **تم التهيئة بنجاح!**
        """
        
        update.message.reply_text(welcome_text)

    def handle_help(self, update, context):
        """معالجة أمر المساعدة"""
        help_text = """
🆘 **مركز المساعدة**

**أوامر البحث:**
• `/search [كلمات]` - البحث على الويب باستخدام DuckDuckGo
• `/memory [كلمات]` - البحث في الذاكرة المحلية

**أوامر النظام:**
• `/status` - عرض حالة الخادم والنظام
• `/clear` - مسح الذاكرة الحالية

**معلومات تقنية:**
• يعمل على Render.com
• Python 3.10+
• ذاكرة مؤقتة
• بحث حقيقي على الويب

**مثال:**
`/search أحدث أخبار التكنولوجيا`
`/memory بحث سابق`
        """
        
        update.message.reply_text(help_text)

    def handle_search(self, update, context):
        """معالجة أمر البحث"""
        if not context.args:
            update.message.reply_text("⚠️ يرجى كتابة كلمات للبحث\nمثال: /search الذكاء الاصطناعي")
            return
        
        query = ' '.join(context.args)
        update.message.reply_text(f"🔍 جاري البحث عن: {query}")
        
        try:
            results = DuckDuckGoSearcher.search(query)
            
            if results:
                response = f"**نتائج البحث عن '{query}':**\n\n"
                for i, result in enumerate(results, 1):
                    response += f"{i}. **{result['title']}**\n"
                    response += f"   {result['url']}\n"
                    response += f"   {result['description']}\n\n"
            else:
                response = f"❌ لم أجد نتائج لـ '{query}'"
            
            update.message.reply_text(response)
            
            # حفظ في الذاكرة
            self.memory.add_memory(f"بحث: {query} - {len(results)} نتيجة")
            
        except Exception as e:
            update.message.reply_text(f"❌ حدث خطأ في البحث: {str(e)}")

    def handle_memory(self, update, context):
        """معالجة أمر الذاكرة"""
        if not context.args:
            # عرض الذاكرة الحالية
            if self.memory.memories:
                response = "🧠 **آخر 10 عناصر في الذاكرة:**\n\n"
                for i, memory in enumerate(self.memory.memories[-10:], 1):
                    response += f"{i}. {memory['summary']}\n"
            else:
                response = "ℹ️ الذاكرة فارغة حالياً"
            update.message.reply_text(response)
            return
        
        query = ' '.join(context.args)
        results = self.memory.search_memories(query)
        
        if results:
            response = f"🔍 **النتائج لـ '{query}':**\n\n"
            for i, memory in enumerate(results, 1):
                response += f"{i}. {memory['summary']}\n"
                response += f"   ⏰ {memory['timestamp'][:16]}\n\n"
        else:
            response = f"❌ لا توجد نتائج لـ '{query}'"
        
        update.message.reply_text(response)

    def handle_status(self, update, context):
        """عرض حالة النظام"""
        memory_info = psutil.virtual_memory()
        disk_info = psutil.disk_usage('/')
        
        status_text = f"""
📊 **حالة النظام على Render**

**🖥️ معلومات الخادم:**
• النظام: {platform.system()} {platform.release()}
• المعالج: {platform.processor() or 'غير معروف'}
• الذاكرة: {memory_info.percent}% مستخدم
• التخزين: {disk_info.percent}% مستخدم

**🤖 حالة البوت:**
• المستخدمين: {len(self.user_sessions)}
• الذكريات: {len(self.memory)} عنصر
• وقت التشغيل: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**✅ النظام يعمل بشكل طبيعي**
        """
        
        update.message.reply_text(status_text)

    def handle_clear(self, update, context):
        """مسح الذاكرة"""
        self.memory.memories = []
        self.memory.save_memories()
        update.message.reply_text("✅ تم مسح الذاكرة بنجاح")

    def handle_message(self, update, context):
        """معالجة الرسائل العادية"""
        user_id = str(update.effective_user.id)
        message_text = update.message.text
        
        # تحديث إحصائيات المستخدم
        if user_id in self.user_sessions:
            self.user_sessions[user_id]['message_count'] = self.user_sessions[user_id].get('message_count', 0) + 1
        else:
            self.user_sessions[user_id] = {
                'start_time': datetime.now().isoformat(),
                'message_count': 1,
                'username': update.effective_user.first_name or 'مستخدم'
            }
        
        # حفظ الرسالة في الذاكرة
        self.memory.add_memory(f"رسالة من {user_id}: {message_text}")
        
        # رد بسيط
        response = "💡 استخدم الأوامر للتفاعل معي:\n/help - للمساعدة\n/search - للبحث\n/memory - للذاكرة"
        update.message.reply_text(response)

    def run(self):
        """تشغيل البوت"""
        logger.info("🚀 بدء تشغيل البوت المستقر...")
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
            from duckduckgo_search import DDGS
            logger.info("✅ جميع المتطلبات مثبتة")
        except ImportError as e:
            logger.error(f"❌ متطلب مفقود: {e}")
            return
        
        # تشغيل البوت
        bot = StableTelegramBot()
        bot.run()
        
    except Exception as e:
        logger.error(f"❌ فشل تشغيل البوت: {e}")

if __name__ == "__main__":
    main()
