from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from collections import defaultdict
import logging

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)  # Mengubah level ke DEBUG untuk mendapatkan log lebih detail
logger = logging.getLogger(__name__)

# Data penyimpanan pesan (menggunakan dictionary)
user_message_count = defaultdict(int)

# ID grup yang valid
valid_group_id = -1002276525006

# Fungsi untuk memeriksa apakah pengguna adalah admin
async def is_admin(update: Update) -> bool:
    # Mendapatkan daftar anggota admin dari grup
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
        await update.message.reply_text(message, parse_mode="MarkdownV2")  # Menggunakan MarkdownV2 untuk format mention
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
        await update.message.reply_text("Jumlah pesan telah direset!")
    else:
        await update.message.reply_text("Bot hanya bekerja di grup ini!")

# Fungsi untuk menghitung pesan yang diterima dari user di grup
async def count_user_message(update: Update, context: CallbackContext) -> None:
    logger.debug(f"Received message: {update.message.text} from user: {update.message.from_user.username}")
    if update.effective_chat.id == valid_group_id:
        user = update.message.from_user
        if user.username:
            user_name = user.username
        else:
            user_name = f"{user.first_name} {user.last_name}" if user.last_name else user.first_name
        
        user_message_count[user_name] += 1

# Fungsi untuk /banbbc hanya bisa dijalankan oleh admin
async def banbbc(update: Update, context: CallbackContext) -> None:
    if not await is_admin(update):
        await update.message.reply_text("Hanya admin yang bisa menjalankan perintah ini!")
        return
    
    if update.effective_chat.id != valid_group_id:
        await update.message.reply_text("Perintah ini hanya berlaku di grup yang valid!")
        return

    # Perintah /banbbc: Kick semua orang yang pesan lebih sedikit dari 100
    users_to_ban = [user for user, count in user_message_count.items() if count < 100]
    
    if users_to_ban:
        for user_name in users_to_ban:
            try:
                # Mengambil ID pengguna berdasarkan username
                user = await context.bot.get_chat_member(update.effective_chat.id, user_name)
                
                # Kick pengguna yang ditemukan
                await context.bot.kick_chat_member(update.effective_chat.id, user.user.id)
                
                # Memberi tahu admin atau yang menjalankan perintah
                await update.message.reply_text(f"{user_name} telah dibanned karena jumlah pesan mereka di bawah 100.")
            except Exception as e:
                logger.error(f"Error while banning {user_name}: {e}")
                await update.message.reply_text(f"Gagal menendang {user_name}.")
    else:
        await update.message.reply_text("Tidak ada pengguna dengan pesan di bawah 100.")

# Fungsi utama untuk menangani kesalahan
async def error(update: Update, context: CallbackContext) -> None:
    logger.warning(f'Update {update} caused error {context.error}')

def main() -> None:
    # Token dari bot Telegram Anda
    token = '7954498975:AAEEaHZq73pgHsswcq-ywncy1CZozNIdZrE'  # Ganti dengan token bot Anda

    # Buat application dan dispatcher
    application = Application.builder().token(token).build()

    # Handler untuk perintah /startbbc
    application.add_handler(CommandHandler("startbbc", startbbc))
    
    # Handler untuk perintah /cekbbc
    application.add_handler(CommandHandler("cekbbc", cekbbc))

    # Handler untuk perintah /resetbbc
    application.add_handler(CommandHandler("resetbbc", resetbbc))

    # Handler untuk perintah /banbbc
    application.add_handler(CommandHandler("banbbc", banbbc))

    # Handler untuk menangani semua pesan yang dikirim di grup
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, count_user_message))

    # Handler untuk menangani error
    application.add_error_handler(error)

    # Mulai bot
    application.run_polling()

if __name__ == '__main__':
    main()
