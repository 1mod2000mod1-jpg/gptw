#!/usr/bin/env python3
"""
Telegram Auto-GPT Bot - النسخة الكاملة على Render
مدمج مع جميع الميزات: الذاكرة، الأوامر، التحديات، الـ Plugins، نظام الاختبارات
"""

import os
import asyncio
import json
import logging
import platform
import psutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
import yaml
import requests
from bs4 import BeautifulSoup

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("FullTelegramAutoGPT")

# =============================================================================
# نظام الذاكرة المتكامل (مطور) - محفوظ بالكامل
# =============================================================================

class MemoryItem:
    """عنصر ذاكرة متقدم"""
    def __init__(self, content: str, summary: str, metadata: dict):
        self.content = content
        self.summary = summary
        self.metadata = metadata
        
    @staticmethod
    def from_text(text: str, source_type: str, metadata: dict = None):
        summary = text[:200] + "..." if len(text) > 200 else text
        return MemoryItem(text, summary, metadata or {})

class EnhancedMemorySystem:
    """نظام ذاكرة محسن مع البحث المتقدم"""
    
    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path
        self.memory_file = workspace_path / "memory" / "telegram_memory.json"
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)
        self.memories: List[MemoryItem] = []
        self.load_memories()
    
    def load_memories(self):
        """تحميل الذكريات من الملف"""
        try:
            if self.memory_file.exists():
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.memories = [MemoryItem(**item) for item in data]
        except Exception as e:
            logger.error(f"خطأ في تحميل الذاكرة: {e}")
    
    def add_memory(self, content: str, metadata: dict = None):
        """إضافة ذاكرة جديدة"""
        memory_item = MemoryItem.from_text(content, "user", metadata)
        self.memories.append(memory_item)
        self.save_memories()
    
    def search_memories(self, query: str, limit: int = 5) -> List[MemoryItem]:
        """بحث متقدم في الذاكرة"""
        results = []
        for memory in reversed(self.memories):
            if query.lower() in memory.content.lower():
                results.append(memory)
                if len(results) >= limit:
                    break
        return results
    
    def save_memories(self):
        """حفظ الذكريات"""
        try:
            data = [{"content": m.content, "summary": m.summary, "metadata": m.metadata} 
                   for m in self.memories]
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"خطأ في حفظ الذاكرة: {e}")
    
    def __len__(self):
        return len(self.memories)

# =============================================================================
# نظام الأوامر المتكامل (مطور) - محفوظ بالكامل
# =============================================================================

class Command:
    """أمر متقدم"""
    def __init__(self, name: str, description: str, method: callable, parameters: list = None):
        self.name = name
        self.description = description
        self.method = method
        self.parameters = parameters or []
    
    async def execute(self, **kwargs):
        """تنفيذ الأمر"""
        return await self.method(**kwargs) if asyncio.iscoroutinefunction(self.method) else self.method(**kwargs)

class AdvancedCommandRegistry:
    """سجل أوامر متقدم"""
    
    def __init__(self, memory_system: EnhancedMemorySystem):
        self.memory_system = memory_system
        self.commands: Dict[str, Command] = {}
    
    def register_command(self, command: Command):
        """تسجيل أمر جديد"""
        self.commands[command.name] = command
    
    async def execute_command(self, command_name: str, **kwargs):
        """تنفيذ أمر"""
        if command_name in self.commands:
            return await self.commands[command_name].execute(**kwargs)
        raise ValueError(f"الأمر {command_name} غير موجود")
    
    async def register_all_commands(self):
        """تسجيل جميع الأوامر المتاحة"""
        
        # أمر سرد الملفات
        list_files_cmd = Command(
            name="list_files",
            description="سرد الملفات في مجلد",
            method=self.list_files_command
        )
        self.register_command(list_files_cmd)
        
        # أمر كتابة ملف
        write_file_cmd = Command(
            name="write_file",
            description="كتابة محتوى إلى ملف",
            method=self.write_file_command
        )
        self.register_command(write_file_cmd)
        
        # أمر البحث في الذاكرة
        search_memory_cmd = Command(
            name="search_memory", 
            description="البحث في الذاكرة",
            method=self.search_memory_command
        )
        self.register_command(search_memory_cmd)
        
        # أمر معلومات النظام
        system_info_cmd = Command(
            name="system_info",
            description="معلومات النظام",
            method=self.system_info_command
        )
        self.register_command(system_info_cmd)
        
        # أمر البحث على الويب
        web_search_cmd = Command(
            name="web_search",
            description="البحث على الويب",
            method=self.web_search_command
        )
        self.register_command(web_search_cmd)
    
    async def list_files_command(self, directory: str = ".") -> str:
        """سرد الملفات"""
        try:
            path = Path(directory)
            if path.exists():
                files = [f.name for f in path.iterdir() if f.is_file()]
                dirs = [d.name for d in path.iterdir() if d.is_dir()]
                return f"📁 المحتويات:\n\n📂 المجلدات: {', '.join(dirs)}\n📄 الملفات: {', '.join(files)}"
            return "❌ المسار غير موجود"
        except Exception as e:
            return f"❌ خطأ: {str(e)}"
    
    async def write_file_command(self, filename: str, text: str) -> str:
        """كتابة ملف"""
        try:
            file_path = Path(filename)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(text)
            return f"✅ تم كتابة الملف: {filename}"
        except Exception as e:
            return f"❌ خطأ في الكتابة: {str(e)}"
    
    async def search_memory_command(self, query: str) -> str:
        """البحث في الذاكرة"""
        if not query:
            return "❌ يرجى تقديم استعلام للبحث"
        
        results = self.memory_system.search_memories(query)
        if results:
            response = f"🔍 **نتائج البحث عن '{query}':**\n\n"
            for i, memory in enumerate(results[:3], 1):
                response += f"{i}. {memory.summary}\n"
            return response
        else:
            return f"❌ لا توجد نتائج لـ '{query}'"
    
    async def system_info_command(self) -> str:
        """معلومات النظام"""
        try:
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return f"""
💻 **معلومات النظام:**

**النظام:** {platform.system()} {platform.release()}
**المعالج:** {platform.processor() or 'غير معروف'}
**الذاكرة:** {memory.percent}% مستخدم ({memory.used//1024//1024}MB / {memory.total//1024//1024}MB)
**التخزين:** {disk.percent}% مستخدم

**بايثون:** {platform.python_version()}
**الذاكرة المخزنة:** {len(self.memory_system)} عنصر
**الوقت:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
        except Exception as e:
            return f"❌ خطأ في معلومات النظام: {str(e)}"
    
    async def web_search_command(self, query: str, num_results: int = 3) -> str:
        """البحث على الويب"""
        try:
            from duckduckgo_search import DDGS
            
            results = []
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=num_results):
                    results.append(f"• **{r['title']}**\n  {r['href']}")
            
            if results:
                return f"🔍 **نتائج البحث عن '{query}':**\n\n" + "\n".join(results)
            else:
                return f"❌ لم يتم العثور على نتائج لـ '{query}'"
                
        except Exception as e:
            return f"❌ خطأ في البحث: {str(e)}"

# =============================================================================
# نظام الـ Plugins المبسط لـ Render
# =============================================================================

class PluginTemplate:
    """قالب Plugin مبسط"""
    def __init__(self):
        self.name = self.__class__.__name__
    
    async def on_message(self, user_id: str, message: str, context: Dict) -> Dict:
        return context
    
    async def before_response(self, user_id: str, response: str, context: Dict) -> str:
        return response

class ArabicLanguagePlugin(PluginTemplate):
    """Plugin للغة العربية المحسن"""
    async def on_message(self, user_id: str, message: str, context: Dict) -> Dict:
        arabic_chars = 'ءآأؤإئابةتثجحخدذرزسشصضطظعغفقكلمنهوي'
        if any(char in message for char in arabic_chars):
            context["language"] = "arabic"
        return context
    
    async def before_response(self, user_id: str, response: str, context: Dict) -> str:
        if context.get("language") == "arabic":
            response = response.replace('ه ', 'ه‏ ').replace('ة ', 'ة‏ ')
        return response

class EnhancedPluginManager:
    """مدير Plugins محسن"""
    def __init__(self):
        self.plugins: List[PluginTemplate] = []
    
    async def load_plugins(self):
        """تحميل الـ Plugins"""
        self.plugins.append(ArabicLanguagePlugin())
    
    async def process_message(self, user_id: str, message: str, context: Dict) -> Dict:
        """معالجة الرسالة عبر جميع الـ Plugins"""
        for plugin in self.plugins:
            context = await plugin.on_message(user_id, message, context)
        return context
    
    async def process_response(self, user_id: str, response: str, context: Dict) -> str:
        """معالجة الرد عبر جميع الـ Plugins"""
        for plugin in self.plugins:
            response = await plugin.before_response(user_id, response, context)
        return response

# =============================================================================
# نظام التحديات المبسط لـ Render
# =============================================================================

class SimpleChallengeSystem:
    """نظام تحديات مبسط"""
    
    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path
        self.scores_file = workspace_path / "challenges" / "scores.json"
        self.scores_file.parent.mkdir(parents=True, exist_ok=True)
        self.scores = self.load_scores()
    
    def load_scores(self) -> Dict:
        """تحميل النقاط"""
        if self.scores_file.exists():
            try:
                with open(self.scores_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"خطأ في تحميل النقاط: {e}")
        return {}
    
    async def start_memory_challenge(self, user_id: str, level: int = 1) -> Dict:
        """بدء تحدي الذاكرة"""
        challenges = {
            1: "تذكر 3 أرقام عشوائية",
            2: "تذكر 5 كلمات في جملة", 
            3: "تذكر تسلسل 7 عناصر"
        }
        
        return {
            "success": True,
            "challenge": "memory",
            "level": level,
            "instructions": challenges.get(level, "تحدي غير معروف"),
            "message": f"🎯 بدء تحدي الذاكرة المستوى {level}"
        }

# =============================================================================
# البوت الرئيسي الكامل على Render
# =============================================================================

class FullTelegramAutoGPT:
    """البوت الكامل مع جميع الميزات"""
    
    def __init__(self):
        # التحقق من المتغيرات البيئية
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
        if not self.telegram_token or not self.openai_api_key:
            raise Exception("❌ متغيرات بيئية مفقودة. تأكد من تعيين TELEGRAM_BOT_TOKEN و OPENAI_API_KEY")
        
        # مساحة العمل على Render
        self.workspace_base = Path("/tmp/autogpt_workspace")
        self.workspace_base.mkdir(parents=True, exist_ok=True)
        
        # الأنظمة المتكاملة
        self.memory_system = None
        self.command_registry = None
        self.plugin_manager = None
        self.challenge_system = None
        self.ai_service = None
        
        # بيانات المستخدمين
        self.user_sessions: Dict[str, Dict] = {}
        
        self.setup_bot()

    def setup_bot(self):
        """إعداد البوت"""
        from telegram.ext import Application, CommandHandler, MessageHandler, filters
        
        self.application = Application.builder().token(self.telegram_token).build()
        self.setup_handlers()

    def setup_handlers(self):
        """إعداد جميع معالجات الأوامر"""
        # الأوامر الأساسية
        self.application.add_handler(CommandHandler("start", self.handle_start))
        self.application.add_handler(CommandHandler("help", self.handle_help))
        self.application.add_handler(CommandHandler("status", self.handle_status))
        
        # أوامر Auto-GPT المتقدمة
        self.application.add_handler(CommandHandler("cmd", self.handle_autogpt_command))
        
        # الأوامر الجديدة
        self.application.add_handler(CommandHandler("search", self.handle_search))
        self.application.add_handler(CommandHandler("challenge", self.handle_challenge))
        
        # معالجة الرسائل العامة
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    async def initialize(self):
        """تهيئة جميع الأنظمة"""
        logger.info("🚀 جاري تهيئة النظام المتكامل على Render...")
        
        try:
            # تهيئة نظام الذاكرة
            self.memory_system = EnhancedMemorySystem(self.workspace_base)
            
            # تهيئة نظام الأوامر
            self.command_registry = AdvancedCommandRegistry(self.memory_system)
            await self.command_registry.register_all_commands()
            
            # تهيئة نظام الـ Plugins
            self.plugin_manager = EnhancedPluginManager()
            await self.plugin_manager.load_plugins()
            
            # تهيئة نظام التحديات
            self.challenge_system = SimpleChallengeSystem(self.workspace_base)
            
            # تهيئة خدمات الذكاء الاصطناعي
            await self.initialize_ai_services()
            
            logger.info("✅ التهيئة اكتملت بنجاح على Render!")
            
        except Exception as e:
            logger.error(f"❌ فشل التهيئة: {e}")
            raise

    async def initialize_ai_services(self):
        """تهيئة خدمات الذكاء الاصطناعي"""
        try:
            import openai
            self.ai_service = openai.AsyncOpenAI(api_key=self.openai_api_key)
            logger.info("✅ خدمات AI مهيأة")
        except Exception as e:
            logger.error(f"⚠️ خطأ في تهيئة AI: {e}")
            # يمكن للبوت العمل بدون AI

    # معالجات الأوامر المحفوظة بالكامل
    async def handle_start(self, update, context):
        """معالجة أمر /start الكامل"""
        user_id = str(update.effective_user.id)
        user_name = update.effective_user.first_name or "مستخدم"
        
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {
                'message_count': 0,
                'created_at': datetime.now().isoformat(),
                'user_name': user_name
            }
        
        welcome_msg = f"""
🎊 **مرحباً {user_name} في Auto-GPT المتكامل على Render!**

🤖 **الأنظمة النشطة:**
✅ نظام الذاكرة المتقدم ({len(self.memory_system)} عنصر)
✅ نظام الأوامر الكامل ({len(self.command_registry.commands)} أمر)
✅ نظام الـ Plugins ({len(self.plugin_manager.plugins)} plugin)
✅ نظام التحديات التفاعلي
✅ {'خدمات الذكاء الاصطناعي' if self.ai_service else 'الوضع الأساسي'}

🚀 **الأوامر المتاحة:**
/start - بدء الجلسة
/help - المساعدة والأوامر
/status - حالة النظام
/search [استعلام] - البحث على الويب
/challenge [مستوى] - بدء تحدي

💡 **أوامر Auto-GPT المتقدمة:**
`/cmd list_files` - سرد الملفات
`/cmd write_file` - كتابة ملف
`/cmd search_memory` - البحث في الذاكرة
`/cmd system_info` - معلومات النظام

🔧 **اكتب أي شيء للبدء في محادثة ذكية!**
        """
        
        await update.message.reply_text(welcome_msg, parse_mode='Markdown')

    async def handle_help(self, update, context):
        """معالجة أمر /help الكامل"""
        help_msg = """
🆘 **مركز المساعدة الكامل**

**أوامر البوت الأساسية:**
/start - بدء النظام
/help - هذه القائمة
/status - حالة النظام
/search [كلمات] - البحث على الويب
/challenge [مستوى] - بدء تحدي

**أوامر Auto-GPT المتقدمة:**
`/cmd list_files [مسار]` - سرد الملفات
`/cmd write_file "اسم.ملف" "محتوى"` - كتابة ملف
`/cmd search_memory "بحث"` - البحث في الذاكرة
`/cmd system_info` - معلومات النظام
`/cmd web_search "استعلام"` - البحث على الويب

**أمثلة:**
/cmd list_files .
/cmd write_file "test.txt" "Hello World"
/search "الذكاء الاصطناعي"
/challenge 1
        """
        
        await update.message.reply_text(help_msg, parse_mode='Markdown')

    async def handle_status(self, update, context):
        """عرض حالة النظام الكاملة"""
        status_msg = await self.get_system_status()
        await update.message.reply_text(status_msg, parse_mode='Markdown')

    async def get_system_status(self) -> str:
        """الحصول على حالة النظام الكاملة"""
        try:
            total_users = len(self.user_sessions)
            total_messages = sum(session.get('message_count', 0) for session in self.user_sessions.values())
            
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            status = f"""
📊 **حالة النظام المتكامل على Render**

👥 **المستخدمين:** {total_users}
💬 **الرسائل:** {total_messages}
🧠 **الذكريات:** {len(self.memory_system)}

💻 **الأداء:**
- الذاكرة: {memory.percent}% مستخدم
- التخزين: {disk.percent}% مستخدم
- النظام: {platform.system()} {platform.release()}

🔧 **الأنظمة:**
- الذاكرة: {'✅' if self.memory_system else '❌'}
- الأوامر: {'✅' if self.command_registry else '❌'} 
- الـ Plugins: {'✅' if self.plugin_manager else '❌'}
- التحديات: {'✅' if self.challenge_system else '❌'}
- AI: {'✅' if self.ai_service else '❌'}

🕒 **آخر تحديث:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            return status
            
        except Exception as e:
            return f"❌ خطأ في الحصول على الحالة: {str(e)}"

    async def handle_autogpt_command(self, update, context):
        """معالجة أوامر Auto-GPT المتقدمة"""
        user_id = str(update.effective_user.id)
        command_text = update.message.text.replace('/cmd', '').strip()
        
        if not command_text:
            await update.message.reply_text("""
⚡ **استخدام الأوامر المتقدمة:**

/cmd اسم_الأمر [معاملات]

**الأوامر المتاحة:**
- `list_files [مسار]` - سرد الملفات
- `write_file "اسم.ملف" "محتوى"` - كتابة ملف  
- `search_memory "بحث"` - البحث في الذاكرة
- `system_info` - معلومات النظام
- `web_search "استعلام"` - البحث على الويب

**أمثلة:**
/cmd list_files .
/cmd write_file "test.txt" "Hello World"
/cmd search_memory "الذكاء الاصطناعي"
/cmd web_search "أحدث التقنيات"
            """)
            return
        
        try:
            parts = command_text.split()
            command_name = parts[0]
            args = parts[1:]
            
            processing_msg = await update.message.reply_text(f"🔄 جاري تنفيذ: {command_name}")
            
            # تحويل الوسائط
            kwargs = {}
            if command_name == "write_file" and len(args) >= 2:
                kwargs = {'filename': args[0], 'text': ' '.join(args[1:])}
            elif command_name == "search_memory" and args:
                kwargs = {'query': ' '.join(args)}
            elif command_name == "list_files" and args:
                kwargs = {'directory': args[0]}
            elif command_name == "web_search" and args:
                kwargs = {'query': ' '.join(args)}
            
            # تنفيذ الأمر
            result = await self.command_registry.execute_command(command_name, **kwargs)
            
            await context.bot.edit_message_text(
                chat_id=processing_msg.chat_id,
                message_id=processing_msg.message_id,
                text=str(result),
                parse_mode='Markdown'
            )
            
        except Exception as e:
            await update.message.reply_text(f"❌ خطأ في التنفيذ: {str(e)}")

    async def handle_search(self, update, context):
        """معالجة أمر البحث المبسط"""
        if not context.args:
            await update.message.reply_text("⚠️ يرجى تقديم استعلام للبحث\nمثال: `/search الذكاء الاصطناعي`", parse_mode='Markdown')
            return

        query = ' '.join(context.args)
        try:
            result = await self.command_registry.execute_command("web_search", query=query)
            await update.message.reply_text(result, parse_mode='Markdown')
        except Exception as e:
            await update.message.reply_text(f"❌ خطأ في البحث: {str(e)}")

    async def handle_challenge(self, update, context):
        """معالجة أمر التحدي"""
        level = int(context.args[0]) if context.args and context.args[0].isdigit() else 1
        
        try:
            result = await self.challenge_system.start_memory_challenge(
                str(update.effective_user.id), level
            )
            
            response = f"✅ **{result['message']}**\n\n"
            response += f"📋 **التعليمات:** {result['instructions']}\n"
            response += "💡 استخدم الذاكرة جيداً!"
            
            await update.message.reply_text(response, parse_mode='Markdown')
        except Exception as e:
            await update.message.reply_text(f"❌ خطأ في التحدي: {str(e)}")

    async def handle_message(self, update, context):
        """معالجة الرسائل النصية مع الذكاء الاصطناعي"""
        user_id = str(update.effective_user.id)
        message_text = update.message.text
        
        if not message_text.strip():
            return
        
        try:
            # تحديث جلسة المستخدم
            if user_id not in self.user_sessions:
                self.user_sessions[user_id] = {
                    'message_count': 0,
                    'created_at': datetime.now().isoformat(),
                    'user_name': update.effective_user.first_name or 'مستخدم'
                }
            self.user_sessions[user_id]['message_count'] += 1
            
            processing_msg = await update.message.reply_text("🔄 جاري المعالجة...")
            
            # معالجة عبر الـ Plugins
            message_context = {
                'user_id': user_id, 
                'timestamp': datetime.now().isoformat()
            }
            message_context = await self.plugin_manager.process_message(user_id, message_text, message_context)
            
            # توليد الرد باستخدام AI إذا كان متاحاً
            if self.ai_service:
                response_text = await self.generate_ai_response(user_id, message_text, message_context)
                # معالجة الرد عبر الـ Plugins
                response_text = await self.plugin_manager.process_response(user_id, response_text, message_context)
            else:
                response_text = "💡 أنا هنا لمساعدتك! استخدم الأوامر مثل /help للبدء."
            
            # تخزين المحادثة في الذاكرة
            self.memory_system.add_memory(
                f"المستخدم: {message_text}\nالمساعد: {response_text}",
                {'user_id': user_id, 'type': 'conversation'}
            )
            
            await context.bot.edit_message_text(
                chat_id=processing_msg.chat_id,
                message_id=processing_msg.message_id,
                text=response_text,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"❌ خطأ في المعالجة: {e}")
            await update.message.reply_text(f"⚠️ حدث خطأ: {str(e)}")

    async def generate_ai_response(self, user_id: str, message: str, context: Dict) -> str:
        """توليد رد باستخدام الذكاء الاصطناعي"""
        try:
            if self.ai_service:
                prompt = self.build_ai_prompt(user_id, message, context)
                
                response = await self.ai_service.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system", 
                            "content": "أنت مساعد ذكي يتحدث العربية بطلاقة. قدم إجابات مفيدة ودقيقة."
                        },
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()
            else:
                return "أنا هنا لمساعدتك! 💡"
                
        except Exception as e:
            logger.error(f"❌ خطأ في توليد الرد: {e}")
            return "⚠️ عذراً، حدث خطأ في المعالجة."

    def build_ai_prompt(self, user_id: str, message: str, context: Dict) -> str:
        """بناء الـ Prompt للذكاء الاصطناعي"""
        user_session = self.user_sessions.get(user_id, {})
        
        prompt_parts = [f"الرسالة: {message}"]
        
        if user_session:
            prompt_parts.append(f"\nالمستخدم: {user_session.get('user_name', 'مستخدم')}")
        
        # إضافة سياق من الذاكرة
        recent_memories = self.memory_system.search_memories(message, limit=2)
        if recent_memories:
            prompt_parts.append("\nالسياق السابق:")
            for i, memory in enumerate(recent_memories, 1):
                prompt_parts.append(f"{i}. {memory.summary}")
        
        return "\n".join(prompt_parts)

    async def run(self):
        """تشغيل البوت"""
        await self.initialize()
        logger.info("🤖 البوت الكامل يعمل الآن على Render...")
        await self.application.run_polling()

# =============================================================================
# التشغيل الرئيسي
# =============================================================================

async def main():
    """الدالة الرئيسية"""
    try:
        bot = FullTelegramAutoGPT()
        await bot.run()
    except Exception as e:
        logger.error(f"❌ فشل تشغيل البوت: {e}")
        # إعادة المحاولة بعد فترة
        await asyncio.sleep(10)
        await main()

if __name__ == "__main__":
    # فحص المتطلبات
    try:
        import telegram
        import openai
        import psutil
        import yaml
        from duckduckgo_search import DDGS
        logger.info("✅ جميع المتطلبات مثبتة")
    except ImportError as e:
        logger.error(f"❌ متطلب مفقود: {e}")
        exit(1)
    
    # التشغيل
    asyncio.run(main())
