import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, BotCommand
import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler, ConversationHandler
from yt_dlp import YoutubeDL
import requests
from dotenv import load_dotenv
from bing_image_downloader import downloader
import shutil
from pathlib import Path

# Muat variabel dari file .env
load_dotenv()

# Token Bot Telegram
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Konfigurasi logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Mengatur level log untuk library yang "berisik" agar tidak membanjiri log
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("telegram.ext").setLevel(logging.WARNING)

# States untuk ConversationHandlers
GET_UNDUH_QUERY, GET_FOTO_QUERY, GET_AZAN_QUERY = range(3)

def format_duration(seconds: int) -> str:
    """Memformat durasi dari detik menjadi string HH:MM:SS."""
    if not seconds:
        return "N/A"
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"

# Fungsi bantuan dan selamat datang
async def start(update: Update, context: CallbackContext):
    user = update.effective_user
    await update.message.reply_html(
        f"👋 Halo {user.mention_html()}!\n\n"
        "Saya adalah bot asisten Termux Anda. Gunakan /help untuk melihat daftar perintah yang tersedia."
    )

async def help_command(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "📚 *Daftar Perintah:*\n\n"
        "/unduh <judul/URL> - Mengunduh video atau audio dari YouTube.\n"
        "/cari_foto <kata_kunci> - Mencari 5 foto teratas dari DuckDuckGo.\n"
        "/jadwal_azan <daerah> - Menampilkan jadwal azan untuk daerah tertentu.\n"
        "/help - Menampilkan pesan bantuan ini.\n\n"
        "Fitur jadwal JKT48 untuk sementara dinonaktifkan karena tidak ada sumber data yang stabil.\n"
        "Anda bisa menjalankan perintah tanpa argumen, dan saya akan menanyakannya.",
        parse_mode='Markdown'
    )

# --- Fungsi untuk Unduh Video/Audio ---
async def unduh(update: Update, context: CallbackContext):
    if context.args:
        query = " ".join(context.args)
        await perform_search(update.message, query, context)
        return ConversationHandler.END
    await update.message.reply_text("Silakan masukkan judul atau URL YouTube yang ingin Anda unduh:")
    return GET_UNDUH_QUERY

async def get_unduh_query(update: Update, context: CallbackContext):
    await perform_search(update.message, update.message.text, context)
    return ConversationHandler.END

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

async def perform_search(message, query: str, context: CallbackContext):
    status_msg = await message.reply_text(f"🔎 Mencari `{query}`...", parse_mode='Markdown')
    try:
        result = await asyncio.to_thread(search_videos_sync, query)
        await status_msg.delete()

        if 'entries' in result and result['entries']:
            await message.reply_text("Berikut adalah hasil pencarian teratas:")
            for entry in result['entries']:
                title = entry.get('title', 'N/A')
                video_url = entry.get('webpage_url', '')
                thumbnail_url = entry.get('thumbnail')
                duration_seconds = entry.get('duration')
                duration_formatted = format_duration(duration_seconds)

                caption = f"{title}\n\nDurasi: {duration_formatted}"

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
            await message.reply_text('Tidak ada hasil yang ditemukan!')
    except Exception as e:
        logging.error(f"Error saat mencari: {e}")
        await status_msg.edit_text("Terjadi kesalahan saat melakukan pencarian.")

# --- Fungsi untuk Cari Foto ---
async def cari_foto(update: Update, context: CallbackContext):
    if context.args:
        query = " ".join(context.args)
        await perform_gambar_search(update.message, query, context)
        return ConversationHandler.END
    await update.message.reply_text("Silakan masukkan kata kunci foto yang ingin Anda cari:")
    return GET_FOTO_QUERY

async def get_foto_query(update: Update, context: CallbackContext):
    await perform_gambar_search(update.message, update.message.text, context)
    return ConversationHandler.END

def search_images_sync(query: str, output_dir: Path) -> list[Path]:
    """Fungsi sinkron untuk mengunduh gambar menggunakan bing-image-downloader."""
    downloader.download(query, limit=5, output_dir=output_dir, adult_filter_off=True, force_replace=False, timeout=60, verbose=False)
    # Dapatkan path dari semua file gambar yang diunduh
    image_dir = output_dir / query
    if not image_dir.exists():
        return []
    return list(image_dir.glob('*'))

async def perform_gambar_search(message, query: str, context: CallbackContext):
    status_msg = await message.reply_text(f"🖼️ Mencari foto untuk `{query}`...", parse_mode='Markdown')

    # Buat direktori unik untuk unduhan ini
    output_dir = Path(f"downloads/images_{message.chat_id}_{message.message_id}")

    try:
        # Menjalankan fungsi sinkron di thread terpisah
        image_paths = await asyncio.to_thread(search_images_sync, query, output_dir)
        await status_msg.delete()

        if image_paths:
            media_group = [InputMediaPhoto(media=p.open('rb')) for p in image_paths]
            await message.reply_media_group(media=media_group)
        else:
            await message.reply_text('Tidak ada foto yang ditemukan!')

    except Exception as e:
        logging.error(f"Error saat mencari foto: {e}")
        await status_msg.edit_text("Terjadi kesalahan saat mencari foto.")
    finally:
        # Selalu pastikan untuk membersihkan direktori unduhan
        if output_dir.exists():
            shutil.rmtree(output_dir)

# --- Fungsi untuk Jadwal Azan ---
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

def get_azan_times_sync(city: str):
    """Fungsi sinkron untuk mengambil data jadwal salat."""
    url = f"http://api.aladhan.com/v1/timingsByCity?city={city}&country=Indonesia&method=20"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

async def perform_azan_search(message, city: str):
    status_msg = await message.reply_text(f"🕌 Mencari jadwal salat untuk `{city}`...", parse_mode='Markdown')
    try:
        data = await asyncio.to_thread(get_azan_times_sync, city)

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

# --- Fungsi untuk Unduh Video & Audio ---
def download_video_sync(video_url: str):
    """Fungsi sinkron untuk mengunduh video."""
    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'noplaylist': True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=True)
        filename = ydl.prepare_filename(info_dict)
        return filename, info_dict.get('title')

async def unduh_video(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    video_url = query.data.split('|')[1]

    original_caption = query.message.caption
    await query.edit_message_caption(caption=f"⏳ Mengunduh video...\n\n{original_caption}")

    try:
        filename, title = await asyncio.to_thread(download_video_sync, video_url)
        await context.bot.send_video(
            chat_id=query.message.chat_id,
            video=open(filename, 'rb'),
            caption=title
        )
        await query.delete_message()
    except Exception as e:
        logging.error(f"Error saat mengunduh video: {e}")
        await query.edit_message_caption(caption=f"❌ Gagal mengunduh video.\n\n{original_caption}")

def download_audio_sync(video_url: str):
    """Fungsi sinkron untuk mengunduh audio."""
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
        return filename, info_dict.get('title')

async def unduh_audio(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    video_url = query.data.split('|')[1]

    original_caption = query.message.caption
    await query.edit_message_caption(caption=f"⏳ Mengunduh audio...\n\n{original_caption}")

    try:
        filename, title = await asyncio.to_thread(download_audio_sync, video_url)
        await context.bot.send_audio(
            chat_id=query.message.chat_id,
            audio=open(filename, 'rb'),
            caption=title
        )
        await query.delete_message()
    except Exception as e:
        logging.error(f"Error saat mengunduh audio: {e}")
        await query.edit_message_caption(caption=f"❌ Gagal mengunduh audio.\n\n{original_caption}")

def main():
    application = Application.builder().token(TOKEN).build()

    # Conversation handlers
    conv_handlers = {
        "unduh": ConversationHandler(
            entry_points=[CommandHandler("unduh", unduh)],
            states={GET_UNDUH_QUERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_unduh_query)]},
            fallbacks=[CommandHandler("start", start)],
        ),
        "cari_foto": ConversationHandler(
            entry_points=[CommandHandler("cari_foto", cari_foto)],
            states={GET_FOTO_QUERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_foto_query)]},
            fallbacks=[CommandHandler("start", start)],
        ),
        "jadwal_azan": ConversationHandler(
            entry_points=[CommandHandler("jadwal_azan", jadwal_azan)],
            states={GET_AZAN_QUERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_azan_query)]},
            fallbacks=[CommandHandler("start", start)],
        )
    }

    # Tambahkan handler
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    for handler in conv_handlers.values():
        application.add_handler(handler)
    application.add_handler(CallbackQueryHandler(unduh_video, pattern='^unduh_video\\|'))
    application.add_handler(CallbackQueryHandler(unduh_audio, pattern='^unduh_audio\\|'))

    # Atur perintah bot saat inisialisasi
    async def post_init(application: Application):
        commands = [
            BotCommand("unduh", "Mengunduh video atau audio dari YouTube"),
            BotCommand("cari_foto", "Mencari foto berdasarkan kata kunci"),
            BotCommand("jadwal_azan", "Mendapatkan jadwal salat untuk sebuah kota"),
            BotCommand("help", "Menampilkan pesan bantuan"),
        ]
        await application.bot.set_my_commands(commands)

    application.post_init = post_init
    application.run_polling()

if __name__ == '__main__':
    main()