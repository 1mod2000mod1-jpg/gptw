#!/usr/bin/env python3
"""
Telegram Auto-GPT Bot - نسخة Render
مدمج مع: الذاكرة، الأوامر، التحديات، الـ Plugins، نظام الاختبارات
"""

import os
import asyncio
import json
import logging
import platform
from pathlib import Path
from typing import Dict, List, Optional, Any
import psutil
import yaml
import requests
from bs4 import BeautifulSoup

# إعداد التسجيل للنشر
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("RenderTelegramAutoGPT")

class RenderConfig:
    """تكوين مخصص لبيئة Render"""
    
    def __init__(self):
        self.workspace_base = Path("/tmp/autogpt_workspace")
        self.workspace_base.mkdir(parents=True, exist_ok=True)
        
        # الحصول على المتغيرات البيئية من Render
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.webhook_url = os.getenv('RENDER_WEBHOOK_URL', '')
        
        # فحص المتطلبات الأساسية
        self.validate_environment()

    def validate_environment(self):
        """التحقق من توفر المتغيرات البيئية الأساسية"""
        missing_vars = []
        if not self.telegram_token:
            missing_vars.append('TELEGRAM_BOT_TOKEN')
        if not self.openai_api_key:
            missing_vars.append('OPENAI_API_KEY')
        
        if missing_vars:
            raise Exception(f"❌ متغيرات بيئية مفقودة: {', '.join(missing_vars)}")

class LightweightMemorySystem:
    """نظام ذاكرة خفيف للاستضافة"""
    
    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path
        self.memory_file = workspace_path / "lightweight_memory.json"
        self.memories: List[Dict] = []
        self.load_memories()

    def load_memories(self):
        """تحميل الذكريات"""
        try:
            if self.memory_file.exists():
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    self.memories = json.load(f)
        except Exception as e:
            logger.warning(f"⚠️ خطأ في تحميل الذاكرة: {e}")

    def add_memory(self, content: str, memory_type: str = "general"):
        """إضافة ذاكرة جديدة"""
        memory_item = {
            'content': content,
            'type': memory_type,
            'timestamp': str(asyncio.get_event_loop().time())
        }
        self.memories.append(memory_item)
        self.save_memories()

    def search_memories(self, query: str, limit: int = 5) -> List[Dict]:
        """بحث بسيط في الذاكرة"""
        results = []
        for memory in reversed(self.memories):
            if query.lower() in memory['content'].lower():
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

class WebSearchService:
    """خدمة بحث ويب خفيفة"""
    
    @staticmethod
    async def simple_search(query: str) -> str:
        """بحث مبسط على الويب"""
        try:
            # استخدام DuckDuckGo للبحث
            from duckduckgo_search import DDGS
            
            results = []
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=3):
                    results.append(f"• {r['title']} - {r['href']}")
            
            if results:
                return f"🔍 **نتائج البحث عن '{query}':**\n\n" + "\n".join(results)
            else:
                return f"❌ لم يتم العثور على نتائج لـ '{query}'"
                
        except Exception as e:
            logger.error(f"خطأ في البحث: {e}")
            return "⚠️ عذراً، حدث خطأ في البحث. يرجى المحاولة لاحقاً."

class TelegramBotRenderer:
    """البوت الرئيسي المعدل لـ Render"""
    
    def __init__(self):
        self.config = RenderConfig()
        self.memory_system = LightweightMemorySystem(self.config.workspace_base)
        self.setup_bot()

    def setup_bot(self):
        """إعداد البوت"""
        from telegram.ext import Application, CommandHandler, MessageHandler, filters
        
        self.application = Application.builder().token(self.config.telegram_token).build()
        
        # تسجيل المعالجات
        self.setup_handlers()

    def setup_handlers(self):
        """إعداد معالجات الأوامر"""
        # الأوامر الأساسية
        self.application.add_handler(CommandHandler("start", self.handle_start))
        self.application.add_handler(CommandHandler("help", self.handle_help))
        self.application.add_handler(CommandHandler("search", self.handle_search))
        self.application.add_handler(CommandHandler("memory", self.handle_memory))
        self.application.add_handler(CommandHandler("status", self.handle_status))
        
        # معالجة الرسائل العامة
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    async def handle_start(self, update, context):
        """معالجة أمر البدء"""
        welcome_msg = """
🤖 **مرحباً! أنا بوت Auto-GPT على Render**

🚀 **الأوامر المتاحة:**
/start - عرض هذه الرسالة
/help - المساعدة المفصلة
/search [استعلام] - البحث على الويب  
/memory [استعلام] - البحث في الذاكرة
/status - حالة النظام

💡 **أمثلة:**
/search "الذكاء الاصطناعي"
/memory "مشروع سابق"

🔧 **النظام يعمل على استضافة Render!**
        """
        await update.message.reply_text(welcome_msg, parse_mode='Markdown')

    async def handle_help(self, update, context):
        """معالجة أمر المساعدة"""
        help_msg = """
🆘 **مركز المساعدة**

**أوامر البحث:**
• `/search [كلمات]` - البحث على الويب
• `/memory [كلمات]` - البحث في الذاكرة

**أوامر المعلومات:**
• `/status` - حالة النظام والخادم

**معلومات تقنية:**
• يعمل على Render.com
• ذاكرة مؤقتة
• بحث حقيقي على الويب
        """
        await update.message.reply_text(help_msg, parse_mode='Markdown')

    async def handle_search(self, update, context):
        """معالجة أمر البحث"""
        if not context.args:
            await update.message.reply_text("⚠️ يرجى تقديم استعلام للبحث\nمثال: `/search الذكاء الاصطناعي`", parse_mode='Markdown')
            return

        query = ' '.join(context.args)
        processing_msg = await update.message.reply_text(f"🔍 جاري البحث عن: {query}")

        try:
            result = await WebSearchService.simple_search(query)
            await context.bot.edit_message_text(
                chat_id=processing_msg.chat_id,
                message_id=processing_msg.message_id,
                text=result,
                parse_mode='Markdown'
            )
            
            # حفظ في الذاكرة
            self.memory_system.add_memory(f"بحث: {query}")
            
        except Exception as e:
            await update.message.reply_text(f"❌ خطأ في البحث: {str(e)}")

    async def handle_memory(self, update, context):
        """معالجة أمر الذاكرة"""
        if not context.args:
            await update.message.reply_text("⚠️ يرجى تقديم استعلام للبحث في الذاكرة")
            return

        query = ' '.join(context.args)
        results = self.memory_system.search_memories(query)

        if results:
            response = f"🧠 **النتائج في الذاكرة لـ '{query}':**\n\n"
            for i, memory in enumerate(results[:3], 1):
                response += f"{i}. {memory['content'][:100]}...\n"
        else:
            response = f"❌ لا توجد نتائج في الذاكرة لـ '{query}'"

        await update.message.reply_text(response, parse_mode='Markdown')

    async def handle_status(self, update, context):
        """عرض حالة النظام"""
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        status_msg = f"""
📊 **حالة النظام على Render:**

**🖥️ الخادم:**
• النظام: {platform.system()} {platform.release()}
• المعالج: {platform.processor() or 'غير معروف'}
• الذاكرة: {memory.percent}% مستخدم
• التخزين: {disk.percent}% مستخدم

**🤖 البوت:**
• الذكريات: {len(self.memory_system.memories)} عنصر
• المساحة: {self.config.workspace_base}
• النشر: Render.com

**⏰ الوقت:** {asyncio.get_event_loop().time():.0f} ثانية
        """
        await update.message.reply_text(status_msg, parse_mode='Markdown')

    async def handle_message(self, update, context):
        """معالجة الرسائل العامة"""
        user_message = update.message.text
        self.memory_system.add_memory(f"المستخدم: {user_message}")
        
        response = "💡 أنا هنا لمساعدتك! استخدم /help لرؤية الأوامر المتاحة."
        await update.message.reply_text(response)

    async def run(self):
        """تشغيل البوت"""
        logger.info("🚀 بدء تشغيل البوت على Render...")
        
        try:
            # تشغيل البوت
            await self.application.run_polling()
        except Exception as e:
            logger.error(f"❌ خطأ في تشغيل البوت: {e}")
            raise

# =============================================================================
# الدالة الرئيسية للتشغيل على Render
# =============================================================================

async def main():
    """الدالة الرئيسية"""
    try:
        bot = TelegramBotRenderer()
        await bot.run()
    except Exception as e:
        logger.error(f"❌ فشل تشغيل البوت: {e}")
        # إعادة المحاولة بعد فترة
        await asyncio.sleep(5)
        await main()

if __name__ == "__main__":
    # فحص المتطلبات
    try:
        import telegram
        import psutil
        import yaml
        import requests
        from duckduckgo_search import DDGS
        logger.info("✅ جميع المتطلبات مثبتة")
    except ImportError as e:
        logger.error(f"❌ متطلب مفقود: {e}")
        exit(1)
    
    # التشغيل
    asyncio.run(main())
