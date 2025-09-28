#!/usr/bin/env python3
"""
Telegram Auto-GPT Bot - نسخة Render المعدلة
بدون متطلبات spacy الثقيلة
"""

import os
import asyncio
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
logger = logging.getLogger("RenderAutoGPT")

class LightweightMemorySystem:
    """نظام ذاكرة خفيف بدون spacy"""
    
    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path
        self.memory_file = workspace_path / "memory.json"
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
            'timestamp': datetime.now().isoformat(),
            'summary': content[:100] + "..." if len(content) > 100 else content
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

    def __len__(self):
        return len(self.memories)

class WebSearchService:
    """خدمة بحث ويب خفيفة"""
    
    @staticmethod
    async def search(query: str, num_results: int = 3) -> str:
        """بحث على الويب"""
        try:
            from duckduckgo_search import DDGS
            
            results = []
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=num_results):
                    results.append({
                        'title': r.get('title', ''),
                        'url': r.get('href', ''),
                        'snippet': r.get('body', '')[:100] + '...'
                    })
            
            if results:
                response = f"🔍 **نتائج البحث عن '{query}':**\n\n"
                for i, result in enumerate(results, 1):
                    response += f"{i}. **{result['title']}**\n"
                    response += f"   {result['url']}\n"
                    response += f"   {result['snippet']}\n\n"
                return response
            else:
                return f"❌ لم يتم العثور على نتائج لـ '{query}'"
                
        except Exception as e:
            logger.error(f"خطأ في البحث: {e}")
            return "⚠️ عذراً، حدث خطأ في البحث."

class AIService:
    """خدمة الذكاء الاصطناعي المبسطة"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = None
        if api_key:
            try:
                import openai
                self.client = openai.AsyncOpenAI(api_key=api_key)
                logger.info("✅ خدمة AI مهيأة")
            except Exception as e:
                logger.warning(f"⚠️ تعطيل خدمة AI: {e}")

    async def generate_response(self, message: str, context: str = "") -> str:
        """توليد رد باستخدام AI"""
        if not self.client:
            return "💡 أنا هنا لمساعدتك! استخدم الأوامر المتاحة."
        
        try:
            prompt = f"""
            {context}
            
            المستخدم: {message}
            المساعد: """
            
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": "أنت مساعد ذكي يتحدث العربية بطلاقة. قدم إجابات مفيدة وموجزة."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"❌ خطأ في AI: {e}")
            return "⚠️ عذراً، حدث خطأ في المعالجة."

class TelegramBotRenderer:
    """البوت المعدل لـ Render"""
    
    def __init__(self):
        # التحقق من المتغيرات البيئية
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
        if not self.telegram_token:
            raise Exception("❌ TELEGRAM_BOT_TOKEN مطلوب")
        
        # مساحة العمل على Render
        self.workspace_base = Path("/tmp/autogpt_workspace")
        self.workspace_base.mkdir(parents=True, exist_ok=True)
        
        # الأنظمة
        self.memory_system = LightweightMemorySystem(self.workspace_base)
        self.ai_service = AIService(self.openai_api_key)
        self.user_sessions: Dict[str, Dict] = {}
        
        self.setup_bot()

    def setup_bot(self):
        """إعداد البوت"""
        from telegram.ext import Application, CommandHandler, MessageHandler, filters
        
        self.application = Application.builder().token(self.telegram_token).build()
        self.setup_handlers()

    def setup_handlers(self):
        """إعداد معالجات الأوامر"""
        # الأوامر الأساسية
        self.application.add_handler(CommandHandler("start", self.handle_start))
        self.application.add_handler(CommandHandler("help", self.handle_help))
        self.application.add_handler(CommandHandler("search", self.handle_search))
        self.application.add_handler(CommandHandler("memory", self.handle_memory))
        self.application.add_handler(CommandHandler("status", self.handle_status))
        self.application.add_handler(CommandHandler("save", self.handle_save))
        
        # معالجة الرسائل العامة
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    async def handle_start(self, update, context):
        """معالجة أمر البدء"""
        user_id = str(update.effective_user.id)
        user_name = update.effective_user.first_name or "مستخدم"
        
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {
                'message_count': 0,
                'created_at': datetime.now().isoformat(),
                'user_name': user_name
            }
        
        welcome_msg = f"""
🤖 **مرحباً {user_name} في Auto-GPT على Render!**

🚀 **الميزات النشطة:**
✅ نظام الذاكرة ({len(self.memory_system)} عنصر)
✅ البحث على الويب
✅ {'الذكاء الاصطناعي (GPT)' if self.ai_service.client else 'الوضع الأساسي'}
✅ إدارة الملفات

🎯 **الأوامر المتاحة:**
/start - عرض هذه الرسالة
/help - المساعدة المفصلة
/search [استعلام] - البحث على الويب
/memory [استعلام] - البحث في الذاكرة
/status - حالة النظام
/save - حفظ البيانات

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
• `/search [كلمات]` - البحث على الويب (DuckDuckGo)
• `/memory [كلمات]` - البحث في الذاكرة المحلية

**أوامر المعلومات:**
• `/status` - حالة النظام والخادم
• `/save` - حفظ البيانات الحالية

**معلومات تقنية:**
• يعمل على Render.com (Python 3.10+)
• ذاكرة مؤقتة في /tmp/
• بحث حقيقي على الويب
• دعم الذكاء الاصطناعي (إذا متوفر)

**مثال للبحث:**
`/search أحدث تقنيات الذكاء الاصطناعي 2024`
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
            result = await WebSearchService.search(query)
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
            # عرض كل الذاكرة إذا لم يكن هناك استعلام
            if self.memory_system.memories:
                response = "🧠 **آخر 5 عناصر في الذاكرة:**\n\n"
                for i, memory in enumerate(self.memory_system.memories[-5:], 1):
                    response += f"{i}. {memory['summary']}\n"
            else:
                response = "ℹ️ الذاكرة فارغة حالياً."
            await update.message.reply_text(response, parse_mode='Markdown')
            return

        query = ' '.join(context.args)
        results = self.memory_system.search_memories(query)

        if results:
            response = f"🧠 **النتائج في الذاكرة لـ '{query}':**\n\n"
            for i, memory in enumerate(results[:3], 1):
                response += f"{i}. {memory['summary']}\n"
                response += f"   ⏰ {memory['timestamp'][:16]}\n\n"
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
• المستخدمين: {len(self.user_sessions)}
• الذكريات: {len(self.memory_system)} عنصر
• الذكاء الاصطناعي: {'✅ نشط' if self.ai_service.client else '❌ غير نشط'}
• المساحة: {self.workspace_base}

**⏰ الوقت:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        await update.message.reply_text(status_msg, parse_mode='Markdown')

    async def handle_save(self, update, context):
        """حفظ البيانات"""
        try:
            self.memory_system.save_memories()
            await update.message.reply_text("✅ تم حفظ البيانات بنجاح!")
        except Exception as e:
            await update.message.reply_text(f"❌ خطأ في الحفظ: {str(e)}")

    async def handle_message(self, update, context):
        """معالجة الرسائل العامة"""
        user_id = str(update.effective_user.id)
        user_message = update.message.text
        
        # تحديث جلسة المستخدم
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {
                'message_count': 0,
                'created_at': datetime.now().isoformat(),
                'user_name': update.effective_user.first_name or 'مستخدم'
            }
        self.user_sessions[user_id]['message_count'] += 1
        
        # حفظ في الذاكرة
        self.memory_system.add_memory(f"المستخدم {user_id}: {user_message}")
        
        processing_msg = await update.message.reply_text("💭 جاري التفكير...")
        
        try:
            # البحث في الذاكرة للسياق
            context_memories = self.memory_system.search_memories(user_message, limit=2)
            context = "السياق السابق:\n" + "\n".join([m['summary'] for m in context_memories]) if context_memories else ""
            
            # توليد الرد
            response = await self.ai_service.generate_response(user_message, context)
            
            await context.bot.edit_message_text(
                chat_id=processing_msg.chat_id,
                message_id=processing_msg.message_id,
                text=response,
                parse_mode='Markdown'
            )
            
            # حفظ الرد في الذاكرة
            self.memory_system.add_memory(f"المساعد: {response}")
            
        except Exception as e:
            logger.error(f"❌ خطأ في المعالجة: {e}")
            await update.message.reply_text("⚠️ عذراً، حدث خطأ في المعالجة.")

    async def run(self):
        """تشغيل البوت"""
        logger.info("🚀 بدء تشغيل البوت على Render...")
        await self.application.run_polling()

# =============================================================================
# التشغيل الرئيسي
# =============================================================================

async def main():
    """الدالة الرئيسية"""
    try:
        bot = TelegramBotRenderer()
        await bot.run()
    except Exception as e:
        logger.error(f"❌ فشل تشغيل البوت: {e}")
        # إعادة المحاولة بعد فترة
        await asyncio.sleep(10)
        await main()

if __name__ == "__main__":
    # فحص المتطلبات الأساسية فقط
    try:
        import telegram
        import psutil
        logger.info("✅ المتطلبات الأساسية مثبتة")
    except ImportError as e:
        logger.error(f"❌ متطلب أساسي مفقود: {e}")
        exit(1)
    
    # التشغيل
    asyncio.run(main())
