from groq import Groq
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

# --- КОНФИГУРАЦИЯ ---
TELEGRAM_TOKEN = "8575370146:AAESq4FQkSaDw-HR3cH7icD5L8RJNb0-lfs"
GROQ_API_KEY = "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"
ADMIN_ID = 8352089240 

client = Groq(api_key=GROQ_API_KEY)

# 📌 START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Сәлем! 🛒 Бұл дүкеннің кері байланыс боты.\n"
        "Пікіріңізді жазыңыз, біз оны ИИ арқылы талдап, әкімшіге жібереміз."
    )

# 📌 НЕГІЗГІ ФУНКЦИЯ
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text.strip()

    # 1. АДМИН ЖАУАП БЕРГЕН КЕЗДЕ (REPLY ТЕКСЕРУ)
    if user_id == ADMIN_ID and update.message.reply_to_message:
        try:
            # Админге келген хабарламаның мәтінін аламыз
            reply_text = update.message.reply_to_message.text
            
            # Мәтін ішінен "ID: " деген сөзден кейінгі сандарды табамыз
            import re
            found_ids = re.findall(r"ID: (\d+)", reply_text)
            
            if found_ids:
                target_user_id = int(found_ids[-1])
                await context.bot.send_message(
                    chat_id=target_user_id,
                    text=f"🏪 **Дүкен әкімшісінің жауабы:**\n\n{user_text}"
                )
                await update.message.reply_text("✅ Жауап тұтынушыға сәтті жіберілді!")
            else:
                await update.message.reply_text("❌ Хабарламадан пайдаланушы ID-і табылмады.")
            return
        except Exception as e:
            await update.message.reply_text(f"❌ Қате: {str(e)}")
            return

    # 2. ТҰТЫНУШЫ ПІКІР ЖАЗҒАН КЕЗДЕ
    system_instruction = (
        "Сен — дүкендегі пікірлерді талдаушысың. "
        "Талдау форматы: Тональділік, Баға (1-5), Түйіндеме. "
        "Тек қазақ тілінде жауап бер."
    )

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        # ИИ-ден жауап алу (Түзетілген формат)
        chat_completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_text}
            ]
        )
        ai_analysis = chat_completion.choices[0].message.content

        # Тұтынушыға жауап
        await update.message.reply_text("✅ Рахмет! Сіздің пікіріңіз қабылданды және әкімшіге жеткізілді.")

        # Админге (саған) есеп жіберу (Осы хабарламаға Reply жасау керек!)
        admin_report = (
            f"🔔 **ЖАҢА ПІКІР!**\n\n"
            f"👤 **Кімнен:** {update.effective_user.first_name}\n"
            f"📝 **Мәтін:** {user_text}\n\n"
            f"🤖 **ИИ АНАЛИЗІ:**\n{ai_analysis}\n\n"
            f"👉 Жауап беру үшін осыны 'Reply' етіңіз.\n"
            f"ID: {user_id}"
        )
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_report)

    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text("Кешіріңіз, ИИ өңдеуде қате шықты.")

# 🚀 ІСКЕ ҚОСУ
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🚀 Бот іске қосылды! Тексеріп көріңіз.")
    app.run_polling()

if __name__ == "__main__":
    main()