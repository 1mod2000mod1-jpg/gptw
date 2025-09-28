#!/usr/bin/env python3
"""
Telegram Bot - أبسط نسخة ممكنة
"""

import os
import logging
from telegram.ext import Updater, CommandHandler

# التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SimpleBot")

class SimpleBot:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.token:
            raise Exception("TELEGRAM_BOT_TOKEN مطلوب")
        
        self.setup()
    
    def setup(self):
        self.updater = Updater(token=self.token, use_context=True)
        dp = self.updater.dispatcher
        
        # أمر واحد فقط للتأكد من العمل
        dp.add_handler(CommandHandler("start", self.start))
        dp.add_handler(CommandHandler("ping", self.ping))
    
    def start(self, update, context):
        update.message.reply_text("🎉 البوت يعمل! /ping للتحقق")
    
    def ping(self, update, context):
        update.message.reply_text("🏓 pong! البوت يعمل بشكل ممتاز")
    
    def run(self):
        logger.info("بدء البوت...")
        self.updater.start_polling()
        self.updater.idle()

if __name__ == "__main__":
    try:
        bot = SimpleBot()
        bot.run()
    except Exception as e:
        logger.error(f"خطأ: {e}")
