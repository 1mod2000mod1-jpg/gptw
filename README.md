# Telegram Auto-GPT Bot on Render

بوت تلقرام ذكي يعمل على استضافة Render.com مع ميزات الذكاء الاصطناعي المتقدمة.

## 🚀 النشر السريع

[![نشر على Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

## ⚙️ الإعداد المطلوب

### 1. متغيرات البيئة (Environment Variables)

يجب تعيين المتغيرات التالية في Render:

- `TELEGRAM_BOT_TOKEN`: رمز بوت تلقرام من @BotFather
- `OPENAI_API_KEY`: مفتاح API من OpenAI

### 2. النشر من GitHub

1. انسخ هذا المستودع
2. سجل الدخول إلى [Render.com](https://render.com)
3. انقر على "New Web Service"
4. اختر مستودعك
5. عين المتغيرات البيئية
6. انقر "Create Web Service"

## 🎯 الأوامر المتاحة

- `/start` - بدء البوت
- `/help` - المساعدة
- `/search [query]` - البحث على الويب
- `/memory [query]` - البحث في الذاكرة
- `/status` - حالة النظام

## 🔧 البنية التقنية

- **Python 3.10**
- **python-telegram-bot**
- **DuckDuckGo Search**
- **Lightweight Memory System**
- **Render Web Services**

## 📞 الدعم

إذا واجهتك أي مشاكل، راجع [وثائق Render](https://render.com/docs).
