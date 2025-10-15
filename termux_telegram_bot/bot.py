import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
import asyncio
from telegram.constants import ChatMemberStatus
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler, ConversationHandler, ChatMemberHandler
from yt_dlp import YoutubeDL
import requests
from dotenv import load_dotenv
from duckduckgo_images_api import search as ddg_search
import mediafire_dl

# Muat variabel dari file .env
load_dotenv()

# Token Bot Telegram
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Konfigurasi logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# States untuk ConversationHandlers
GET_VIDEO_QUERY, GET_GAMBAR_QUERY, GET_AZAN_QUERY = range(3)

# --- Fitur Keamanan Grup ---
async def admin_protector(update: Update, context: CallbackContext) -> None:
    """Mendeteksi saat seorang admin diturunkan pangkatnya dan mengirim peringatan."""
    # Ekstrak informasi dari update
    demoted_user = update.chat_member.new_chat_member.user
    old_status = update.chat_member.old_chat_member.status
    new_status = update.chat_member.new_chat_member.status

    # Kondisi yang kita cari: admin diturunkan menjadi member
    was_admin = old_status == ChatMemberStatus.ADMINISTRATOR
    is_now_member = new_status == ChatMemberStatus.MEMBER

    if was_admin and is_now_member:
        logging.info(f"Admin demotion detected in chat {update.effective_chat.id}. User demoted: {demoted_user.id}")
        try:
            # Kirim pesan peringatan ke grup
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=(
                    f"🚨 **PERINGATAN KEAMANAN** 🚨\n\n"
                    f"Admin {demoted_user.mention_html()} telah diturunkan dari jabatannya.\n\n"
                    f"Mohon periksa log audit grup untuk melihat siapa yang melakukan tindakan ini."
                ),
                parse_mode='HTML'
            )
        except Exception as e:
            logging.error(f"Gagal mengirim pesan peringatan demosi: {e}")

# --- Navigasi Menu ---
async def start_unduh_from_menu(update: Update, context: CallbackContext) -> int:
    """Memulai alur unduh dari menu."""
    await update.callback_query.edit_message_text("Silakan kirimkan judul atau URL untuk diunduh:")
    return GET_VIDEO_QUERY

async def start_foto_from_menu(update: Update, context: CallbackContext) -> int:
    """Memulai alur pencarian foto dari menu."""
    await update.callback_query.edit_message_text("Silakan masukkan kata kunci foto yang ingin Anda cari:")
    return GET_GAMBAR_QUERY

async def start_azan_from_menu(update: Update, context: CallbackContext) -> int:
    """Memulai alur jadwal azan dari menu."""
    await update.callback_query.edit_message_text("Masukkan nama kota di Indonesia (contoh: Jakarta):")
    return GET_AZAN_QUERY

async def downloader_menu(update: Update, context: CallbackContext) -> None:
    """Menampilkan menu untuk fitur downloader."""
    keyboard = [
        [InlineKeyboardButton("▶️ Mulai Unduh", callback_data='start_unduh')],
        [InlineKeyboardButton("Kembali", callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "Anda berada di menu Downloader. Fitur ini dapat mengunduh media dari berbagai sumber seperti YouTube, TikTok, dll."
    await update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)

async def search_menu(update: Update, context: CallbackContext) -> None:
    """Menampilkan menu untuk fitur pencarian."""
    keyboard = [
        [InlineKeyboardButton("▶️ Mulai Cari Foto", callback_data='start_foto')],
        [InlineKeyboardButton("Kembali", callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "Anda berada di menu Pencarian. Fitur ini dapat mencari gambar berdasarkan kata kunci."
    await update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)

async def islamic_menu(update: Update, context: CallbackContext) -> None:
    """Menampilkan menu untuk fitur Islami."""
    keyboard = [
        [InlineKeyboardButton("▶️ Mulai Jadwal Azan", callback_data='start_azan')],
        [InlineKeyboardButton("Kembali", callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "Anda berada di menu Islami. Fitur ini dapat menampilkan jadwal salat untuk kota di Indonesia."
    await update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)

async def button_callback_handler(update: Update, context: CallbackContext) -> None:
    """Menangani semua klik tombol dari menu inline."""
    query = update.callback_query
    await query.answer()

    if query.data == 'main_menu':
        await main_menu(query, context)
    elif query.data == 'menu_downloader':
        await downloader_menu(query, context)
    elif query.data == 'menu_search':
        await search_menu(query, context)
    elif query.data == 'menu_islamic':
        await islamic_menu(query, context)

# Fungsi bantuan dan selamat datang
async def start(update: Update, context: CallbackContext):
    user = update.effective_user
    await update.message.reply_html(
        f"👋 Halo {user.mention_html()}!\n\n"
        "Saya adalah bot asisten Termux Anda. Gunakan /help untuk melihat daftar perintah yang tersedia."
    )

async def main_menu(update: Update, context: CallbackContext):
    """Kirim pesan menu utama."""
    keyboard = [
        [InlineKeyboardButton("📥 Downloader", callback_data='menu_downloader')],
        [InlineKeyboardButton("🖼️ Pencarian", callback_data='menu_search')],
        [InlineKeyboardButton("🕌 Islami", callback_data='menu_islamic')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Periksa apakah ini dari command atau callback
    if update.callback_query:
        await update.callback_query.edit_message_text("👋 Halo! Silakan pilih kategori dari menu di bawah ini:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("👋 Halo! Silakan pilih kategori dari menu di bawah ini:", reply_markup=reply_markup)

# Fungsi untuk unduh
async def unduh_command(update: Update, context: CallbackContext):
    if context.args:
        query = " ".join(context.args)
        await process_unduh_request(update.message, query, context)
        return ConversationHandler.END
    await update.message.reply_text("Silakan masukkan judul atau URL untuk diunduh:")
    return GET_VIDEO_QUERY

async def get_unduh_query(update: Update, context: CallbackContext):
    await process_unduh_request(update.message, update.message.text, context)
    return ConversationHandler.END

# Fungsi untuk cari foto
async def cari_foto_command(update: Update, context: CallbackContext):
    if context.args:
        query = " ".join(context.args)
        await process_foto_request(update.message, query, context)
        return ConversationHandler.END
    await update.message.reply_text("Silakan masukkan kata kunci foto yang ingin Anda cari:")
    return GET_GAMBAR_QUERY

async def get_foto_query(update: Update, context: CallbackContext):
    await process_foto_request(update.message, update.message.text, context)
    return ConversationHandler.END

def search_images_sync(query: str):
    """Fungsi sinkron untuk menjalankan pencarian gambar."""
    results = ddg_search(query, max_results=5)
    return [r['image'] for r in results]

async def process_foto_request(message, query: str, context: CallbackContext):
    status_msg = await message.reply_text(f"🖼️ Mencari gambar untuk `{query}`...", parse_mode='Markdown')
    try:
        # Menjalankan fungsi sinkron di thread terpisah
        image_urls = await asyncio.to_thread(search_images_sync, query)
        await status_msg.delete()

        if image_urls:
            media_group = [InputMediaPhoto(media=url) for url in image_urls]
            await message.reply_media_group(media=media_group)
        else:
            await message.reply_text('Tidak ada gambar yang ditemukan!')
    except Exception as e:
        logging.error(f"Error saat mencari gambar: {e}")
        await status_msg.edit_text("Terjadi kesalahan saat mencari gambar.")

# Fungsi untuk Jadwal Azan
async def jadwal_azan(update: Update, context: CallbackContext):
    if context.args:
        city = " ".join(context.args)
        await perform_azan_search(update.message, city)
        return ConversationHandler.END
    await update.message.reply_text("Masukkan nama kota di Indonesia (contoh: Jakarta):")
    return GET_AZAN_QUERY

async def get_azan_query(update: Update, context: CallbackContext):
    await perform_azan_search(update.message, update.message.text)
    return ConversationHandler.END

async def perform_azan_search(message, city: str):
    status_msg = await message.reply_text(f"🕌 Mencari jadwal salat untuk `{city}`...", parse_mode='Markdown')
    url = f"http://api.aladhan.com/v1/timingsByCity?city={city}&country=Indonesia&method=20"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if data['code'] == 200:
            timings = data['data']['timings']
            hijri_date = data['data']['date']['hijri']['date']
            gregorian_date = data['data']['date']['gregorian']['date']

            pesan = (
                f"🕌 *Jadwal Salat untuk {city}*\n"
                f"📅 {gregorian_date} M / {hijri_date} H\n\n"
                f"Imsak: {timings['Imsak']}\n"
                f"Subuh: {timings['Fajr']}\n"
                f"Terbit: {timings['Sunrise']}\n"
                f"Zuhur: {timings['Dhuhr']}\n"
                f"Asar: {timings['Asr']}\n"
                f"Magrib: {timings['Maghrib']}\n"
                f"Isya: {timings['Isha']}\n"
            )
            await status_msg.edit_text(pesan, parse_mode='Markdown')
        else:
            await status_msg.edit_text(f"Tidak dapat menemukan jadwal untuk kota `{city}`. Pastikan nama kota benar.")

    except requests.exceptions.RequestException as e:
        logging.error(f"Error saat request API Al-Adhan: {e}")
        await status_msg.edit_text("Gagal terhubung ke layanan jadwal salat.")
    except Exception as e:
        logging.error(f"Error saat memproses jadwal azan: {e}")
        await status_msg.edit_text("Terjadi kesalahan saat memproses permintaan Anda.")

def search_videos_sync(query: str):
    """
    Fungsi sinkron untuk memproses URL atau mencari video.
    Jika query adalah URL, ia akan mengambil info.
    Jika bukan, ia akan mencari satu video teratas di YouTube.
    """
    ydl_opts = {
        'format': 'best',
        'noplaylist': True,
        'quiet': True,
    }

    # Tentukan apakah query adalah URL atau kata kunci pencarian
    search_query = query if query.strip().startswith('http') else f"ytsearch1:{query}"

    with YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(search_query, download=False)

async def process_unduh_request(message, query: str, context: CallbackContext):
    status_msg = await message.reply_text(f"🔎 Memproses `{query}`...", parse_mode='Markdown')
    try:
        if "mediafire.com" in query:
            await status_msg.edit_text("🔗 Link Mediafire terdeteksi. Mengunduh file...")
            output_path = await asyncio.to_thread(mediafire_dl.download, query, 'downloads/', quiet=True)
            await context.bot.send_document(
                chat_id=message.chat_id,
                document=open(output_path, 'rb'),
                filename=os.path.basename(output_path)
            )
            os.remove(output_path)
            await status_msg.delete()
            return

        result = await asyncio.to_thread(search_videos_sync, query)
        await status_msg.delete()

        # Handle kasus di mana URL langsung menghasilkan satu video (bukan dalam 'entries')
        entries = result.get('entries', [])
        if not entries and result.get('id'):
            entries = [result]

        if entries:
            await message.reply_text("Berikut adalah hasilnya:")
            for entry in entries:
                title = entry.get('title', 'N/A')
                video_url = entry.get('webpage_url', entry.get('original_url', ''))
                thumbnail_url = entry.get('thumbnail')

                # Buat caption
                caption = f"Judul: {title}"

                keyboard = [
                    [
                        InlineKeyboardButton("Unduh Video", callback_data=f"unduh_video|{video_url}"),
                        InlineKeyboardButton("Unduh Audio", callback_data=f"unduh_audio|{video_url}"),
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                if thumbnail_url:
                    await context.bot.send_photo(
                        chat_id=message.chat_id,
                        photo=thumbnail_url,
                        caption=caption,
                        reply_markup=reply_markup
                    )
                else:
                    await context.bot.send_message(
                        chat_id=message.chat_id,
                        text=caption,
                        reply_markup=reply_markup
                    )
        else:
            await message.reply_text('Tidak ada hasil yang ditemukan atau URL tidak valid!')
    except Exception as e:
        logging.error(f"Error saat memproses permintaan: {e}")
        await status_msg.edit_text("Terjadi kesalahan saat memproses permintaan Anda.")

# Fungsi untuk unduh video
async def unduh_video(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    video_url = query.data.split('|')[1]
    logging.info(f"Mengunduh video dari {video_url}")
    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'noplaylist': True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=True)
        filename = ydl.prepare_filename(info_dict)
        await context.bot.send_video(
            chat_id=query.message.chat_id,
            video=open(filename, 'rb'),
            caption=info_dict.get('title')
        )

# Fungsi untuk unduh audio
async def unduh_audio(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    video_url = query.data.split('|')[1]
    logging.info(f"Mengunduh audio dari {video_url}")
    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'noplaylist': True,
        'format': 'bestaudio/best',
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}],
    }
    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=True)
        filename = ydl.prepare_filename(info_dict)
        filename = os.path.splitext(filename)[0] + '.mp3'
        await context.bot.send_audio(
            chat_id=query.message.chat_id,
            audio=open(filename, 'rb'),
            caption=info_dict.get('title')
        )

def main():
    application = Application.builder().token(TOKEN).read_timeout(30).write_timeout(30).build()

    # Conversation handler untuk pencarian video
    video_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("unduh", unduh_command), CallbackQueryHandler(start_unduh_from_menu, pattern='^start_unduh$')],
        states={
            GET_VIDEO_QUERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_unduh_query)]
        },
        fallbacks=[CommandHandler("start", start)],
    )

    # Conversation handler untuk pencarian gambar
    gambar_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("cari_foto", cari_foto_command), CallbackQueryHandler(start_foto_from_menu, pattern='^start_foto$')],
        states={
            GET_GAMBAR_QUERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_foto_query)]
        },
        fallbacks=[CommandHandler("start", start)],
    )

    # Conversation handler untuk jadwal azan
    azan_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("jadwal_azan", jadwal_azan), CallbackQueryHandler(start_azan_from_menu, pattern='^start_azan$')],
        states={
            GET_AZAN_QUERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_azan_query)]
        },
        fallbacks=[CommandHandler("start", start)],
    )

    # Tambahkan handler
    application.add_handler(ChatMemberHandler(admin_protector, ChatMemberHandler.CHAT_MEMBER))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", main_menu))
    application.add_handler(CallbackQueryHandler(button_callback_handler))
    application.add_handler(video_conv_handler)
    application.add_handler(gambar_conv_handler)
    application.add_handler(azan_conv_handler)
    application.add_handler(CallbackQueryHandler(unduh_video, pattern='^unduh_video\\|'))
    application.add_handler(CallbackQueryHandler(unduh_audio, pattern='^unduh_audio\\|'))

    # Jalankan bot
    application.run_polling()

if __name__ == '__main__':
    main()