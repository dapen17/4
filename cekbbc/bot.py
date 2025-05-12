from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from collections import defaultdict
import logging
import json
import os

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Path file untuk simpan data
DATA_FILE = 'data.json'

# Fungsi untuk load data dari file
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            return defaultdict(int, data)
    return defaultdict(int)

# Fungsi untuk simpan data ke file
def save_data():
    with open(DATA_FILE, 'w') as f:
        json.dump(user_message_count, f)

# Load data saat awal
user_message_count = load_data()

# ID grup yang valid
valid_group_id = -1002276525006

# Fungsi untuk memeriksa apakah pengguna adalah admin
async def is_admin(update: Update) -> bool:
    chat_member = await update.effective_chat.get_member(update.message.from_user.id)
    return chat_member.status in ['administrator', 'creator']

# Fungsi untuk mulai menghitung pesan
async def startbbc(update: Update, context: CallbackContext) -> None:
    if not await is_admin(update):
        await update.message.reply_text("Hanya admin yang bisa menjalankan perintah ini!")
        return

    logger.debug(f"startbbc called from chat_id: {update.effective_chat.id}")
    if update.effective_chat.id == valid_group_id:
        await update.message.reply_text("Bot mulai menghitung pesan di grup ini!")
    else:
        await update.message.reply_text("Bot hanya bekerja di grup ini!")

# Fungsi untuk melihat daftar user dan jumlah pesan mereka
async def cekbbc(update: Update, context: CallbackContext) -> None:
    if not await is_admin(update):
        await update.message.reply_text("Hanya admin yang bisa menjalankan perintah ini!")
        return

    logger.debug(f"cekbbc called from chat_id: {update.effective_chat.id}")
    if update.effective_chat.id == valid_group_id:
        message = "Daftar Pengguna dan Jumlah Pesan:\n"
        for user, count in user_message_count.items():
            message += f"@{user}: {count} pesan\n"
        await update.message.reply_text(message)
    else:
        await update.message.reply_text("Bot hanya bekerja di grup ini!")

# Fungsi untuk mereset jumlah pesan
async def resetbbc(update: Update, context: CallbackContext) -> None:
    if not await is_admin(update):
        await update.message.reply_text("Hanya admin yang bisa menjalankan perintah ini!")
        return

    logger.debug(f"resetbbc called from chat_id: {update.effective_chat.id}")
    if update.effective_chat.id == valid_group_id:
        user_message_count.clear()
        save_data()
        await update.message.reply_text("Jumlah pesan telah direset!")
    else:
        await update.message.reply_text("Bot hanya bekerja di grup ini!")

# Fungsi untuk menghitung pesan dari user
async def count_user_message(update: Update, context: CallbackContext) -> None:
    logger.debug(f"Received message: {update.message.text} from user: {update.message.from_user.username}")
    if update.effective_chat.id == valid_group_id:
        user = update.message.from_user
        user_name = user.username if user.username else f"{user.first_name} {user.last_name}" if user.last_name else user.first_name
        user_message_count[str(user.id)] = user_message_count.get(str(user.id), 0) + 1
        context.chat_data[f"user_{user.id}_username"] = user_name  # Simpan nama pengguna
        save_data()

# Fungsi untuk /banbbc (ban user dengan pesan < 200)
async def banbbc(update: Update, context: CallbackContext) -> None:
    if not await is_admin(update):
        await update.message.reply_text("Hanya admin yang bisa menjalankan perintah ini!")
        return

    if update.effective_chat.id != valid_group_id:
        await update.message.reply_text("Perintah ini hanya berlaku di grup yang valid!")
        return

    users_to_ban = [int(uid) for uid, count in user_message_count.items() if count < 200]

    if users_to_ban:
        for user_id in users_to_ban:
            try:
                await context.bot.ban_chat_member(update.effective_chat.id, user_id)
                username = context.chat_data.get(f"user_{user_id}_username", f"ID {user_id}")
                await update.message.reply_text(f"🚫 {username} telah dibanned karena jumlah pesan mereka di bawah 200.")
            except Exception as e:
                logger.error(f"Error while banning {user_id}: {e}")
                await update.message.reply_text(f"Gagal menendang user dengan ID {user_id}.")
    else:
        await update.message.reply_text("Tidak ada pengguna dengan pesan di bawah 200.")

# Fungsi untuk menangani error
async def error(update: Update, context: CallbackContext) -> None:
    logger.warning(f'Update {update} caused error {context.error}')

# Fungsi utama
def main() -> None:
    token = '7954498975:AAEEaHZq73pgHsswcq-ywncy1CZozNIdZrE'  # Ganti dengan token bot Anda
    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("startbbc", startbbc))
    application.add_handler(CommandHandler("cekbbc", cekbbc))
    application.add_handler(CommandHandler("resetbbc", resetbbc))
    application.add_handler(CommandHandler("banbbc", banbbc))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, count_user_message))
    application.add_error_handler(error)

    application.run_polling()

if __name__ == '__main__':
    main()
