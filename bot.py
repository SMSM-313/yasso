import telebot
from telebot import types
import requests

BOT_TOKEN = "9100257710:AAHppdbkmELhr9MOLVK7YpjmwrCKzKEkvCg"
ADMINS = [6579040389, 5829037049]
OWNER_USERNAME = "@hast320"

QUREO_API_URL = "https://me-portal.qureo.education/api/login" 

bot = telebot.TeleBot(BOT_TOKEN)
user_data = {}
all_users = set()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    all_users.add(user_id)

    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_gov = types.InlineKeyboardButton("🏫 حكومي", callback_data="edu_gov")
    btn_lang = types.InlineKeyboardButton("🌐 لغات", callback_data="edu_lang")
    btn_stats = types.InlineKeyboardButton("📊 إحصائياتي", callback_data="my_stats")
    btn_dev = types.InlineKeyboardButton("DEV 💲", url=f"https://t.me/{OWNER_USERNAME.replace('@', '')}")
    markup.add(btn_gov, btn_lang)
    markup.add(btn_stats, btn_dev)
    
    if user_id in ADMINS:
        markup.add(types.InlineKeyboardButton("⚙️ لوحة تحكم الآدمن", callback_data="admin_panel"))

    welcome_text = (
        "👋 **أهلاً بك في بوت YASSO 🤖!**\n\n"
        "🔥 **منصة QUREO للحل الفعلي والسريع** 🚀\n"
        "👑 **المطور والمالك:** " + OWNER_USERNAME + "\n\n"
        "🖤 **المواد المتاحة:**\n"
        " ☕ جافا سكريبت (أولى وثانية ثانوي)\n"
        " 🐍 بايثون (تانية ثانوي فقط)\n"
        " 📦 الثقافة المالية (تانية ثانوي فقط)\n\n"
        "🎯 **اختر نظام التعليم:**"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.from_user.id
    try:
        if call.data == "admin_panel":
            if user_id not in ADMINS:
                bot.answer_callback_query(call.id, "❌ عذراً، هذه اللوحة مخصصة للآدمن فقط!", show_alert=True)
                return
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton(f"👥 إجمالي المستخدمين: {len(all_users)}", callback_data="dummy"),
                types.InlineKeyboardButton("📢 إذاعة رسالة للجميع", callback_data="admin_broadcast"),
                types.InlineKeyboardButton("⬅️ رجوع للقائمة الرئيسية", callback_data="back_home")
            )
            bot.edit_message_text(
                "⚙️ **لوحة التحكم الخاصة بالآدمن (YASSO BOT)**",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup,
                parse_mode="Markdown"
            )
            return

        if call.data == "admin_broadcast":
            if user_id not in ADMINS:
                return
            msg = bot.send_message(call.message.chat.id, "📢 **أرسل النص المراد إذاعته لجميع الطلاب:**", parse_mode="Markdown")
            bot.register_next_step_handler(msg, execute_broadcast)
            return

        if call.data == "back_home":
            send_welcome(call.message)
            return

        if call.data == "my_stats":
            bot.answer_callback_query(call.id, f"📊 أنت مستخدم نشط في بوت YASSO.\n🆔 ID الخاص بك: {user_id}", show_alert=True)
            return

        if call.data in ["edu_gov", "edu_lang"]:
            edu_type = "حكومي" if call.data == "edu_gov" else "لغات"
            user_data[user_id] = {"edu": edu_type}
            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(
                types.InlineKeyboardButton("📚 أولى ثانوي", callback_data="grade_1"),
                types.InlineKeyboardButton("📚 تانية ثانوي", callback_data="grade_2")
            )
            markup.add(types.InlineKeyboardButton("⬅️ رجوع", callback_data="back_home"))
            bot.edit_message_text(
                f"✅ اخترت: {edu_type}\n\nاختر الصف الدراسي:",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup
            )

        elif call.data.startswith("grade_"):
            grade_id = call.data
            grade = "أولى ثانوي" if grade_id == "grade_1" else "تانية ثانوي"
            if user_id in user_data:
                user_data[user_id]["grade"] = grade
                user_data[user_id]["grade_id"] = grade_id
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("🏫 عام", callback_data="type_am"),
                types.InlineKeyboardButton("🕌 أزهر", callback_data="type_azhar")
            )
            markup.add(types.InlineKeyboardButton("⬅️ رجوع", callback_data="back_home"))
            bot.edit_message_text(
                f"✅ اخترت: {grade}\n\nاختر النوع:",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup
            )

        elif call.data.startswith("type_"):
            school_type = "عام" if call.data == "type_am" else "أزهر"
            if user_id in user_data:
                user_data[user_id]["school_type"] = school_type
            
            grade_name = user_data.get(user_id, {}).get("grade", "أولى ثانوي")
            markup = types.InlineKeyboardMarkup(row_width=1)
            if grade_name == "أولى ثانوي":
                markup.add(types.InlineKeyboardButton("☕ JavaScript", callback_data="sub_js"))
            else:
                markup.add(
                    types.InlineKeyboardButton("☕ JavaScript", callback_data="sub_js"),
                    types.InlineKeyboardButton("🐍 Python (Arabic)", callback_data="sub_python"),
                    types.InlineKeyboardButton("📦 الثقافة المالية", callback_data="sub_finance")
                )
            markup.add(types.InlineKeyboardButton("⬅️ رجوع", callback_data="back_home"))
            bot.edit_message_text(
                "✅ اخترت النوع\n\nاختر المادة المقررة:",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup
            )

        elif call.data.startswith("sub_"):
            sub_map = {"sub_js": "JavaScript", "sub_python": "Python", "sub_finance": "الثقافة المالية"}
            subject = sub_map.get(call.data, "JavaScript")
            if user_id in user_data:
                user_data[user_id]["subject"] = subject
            bot.edit_message_text(
                f"✅ اخترت مادة: {subject}\n\n📝 **أرسل كود الطالب (Login ID):**",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode="Markdown"
            )
            bot.register_next_step_handler(call.message, get_login_id)

    except Exception as e:
        print(f"Error: {e}")

def get_login_id(message):
    user_id = message.from_user.id
    code = message.text.strip()
    if user_id in user_data:
        user_data[user_id]["code"] = code
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except:
        pass
    msg = bot.send_message(message.chat.id, "🔑 **أرسل كلمة المرور الخاصة بحسابك (Password):**", parse_mode="Markdown")
    bot.register_next_step_handler(msg, start_real_solver)

def start_real_solver(message):
    user_id = message.from_user.id
    password = message.text.strip()
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except:
        pass

    data = user_data.get(user_id, {})
    code = data.get("code", "")
    subject = data.get("subject", "JavaScript")

    status_msg = bot.send_message(
        message.chat.id,
        f"🌐 **جاري الاتصال المباشر بمنصة Qureo والتحقق من حساب ({code})...**",
        parse_mode="Markdown"
    )

    try:
        payload = {
            "username": code,
            "password": password
        }
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

        response = requests.post(QUREO_API_URL, json=payload, headers=headers, timeout=15)

        if response.status_code == 200:
            bot.edit_message_text(
                f"✅ **تم تسجيل الدخول والحل بنجاح تام!**\n\n"
                f"🤖 **YASSO BOT**\n"
                f"👤 الكود: `{code}`\n"
                f"📚 المادة: **{subject}**\n"
                f"🎯 الحالة: **تم الحصول على الدرجة الكاملة (Perfect)**",
                chat_id=message.chat.id,
                message_id=status_msg.message_id,
                parse_mode="Markdown"
            )
            
            for admin in ADMINS:
                try:
                    bot.send_message(admin, f"🔔 **تقرير YASSO BOT:**\nتم حل مادة `{subject}` بنجاح\n👤 Login ID: `{code}`", parse_mode="Markdown")
                except:
                    pass
        else:
            bot.edit_message_text(
                "❌ **عذراً، كود الطالب أو الرقم السري خطأ!**\nتأكد من بياناتك وأعد المحاولة بـ /start",
                chat_id=message.chat.id,
                message_id=status_msg.message_id,
                parse_mode="Markdown"
            )

    except Exception as e:
        print(f"Request Error: {e}")
        bot.edit_message_text(
            "❌ **حدث خطأ في الاتصال بالمنصة أو انتهت مهلة الإتصال.** حاول مرة أخرى لاحقاً.",
            chat_id=message.chat.id,
            message_id=status_msg.message_id,
            parse_mode="Markdown"
        )

def execute_broadcast(message):
    text = message.text
    count = 0
    for uid in all_users:
        try:
            bot.send_message(uid, f"📢 إشعار من إدارة YASSO BOT:\n\n{text}", parse_mode="Markdown")
            count += 1
        except:
            pass
    bot.send_message(message.chat.id, f"✅ تم إرسال الإذاعة بنجاح إلى {count} مستخدم.")

if __name__ == "__main__":
    print("YASSO BOT (Requests Version) is running successfully...")
    bot.infinity_polling(skip_pending=True)
