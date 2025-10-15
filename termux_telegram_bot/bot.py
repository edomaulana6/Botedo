import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
from yt_dlp import YoutubeDL
import requests
from dotenv import load_dotenv
from duckduckgo_images_api import search as ddg_search

# Muat variabel dari file .env
load_dotenv()

# Token Bot Telegram
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Konfigurasi logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


# Fungsi bantuan dan selamat datang
async def start(update: Update, context: CallbackContext):
    user = update.effective_user
    await update.message.reply_html(
        f"👋 Halo {user.mention_html()}!\n\n"
        "Saya adalah bot asisten Termux Anda. Gunakan /help untuk melihat daftar perintah yang tersedia."
    )

async def help_command(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Gunakan perintah /menu untuk melihat semua fitur yang tersedia dalam bentuk tombol interaktif."
    )

async def main_menu(update: Update, context: CallbackContext):
    """Mengirim atau mengedit pesan untuk menampilkan menu utama."""
    keyboard = [
        [InlineKeyboardButton("📥 Downloader", callback_data='menu_downloader')],
        [InlineKeyboardButton("🖼️ Pencarian", callback_data='menu_search')],
        [InlineKeyboardButton("🕌 Islami", callback_data='menu_islamic')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "👋 Halo! Silakan pilih kategori dari menu di bawah ini:"

    if update.callback_query:
        # Jika dipanggil dari callback (tombol), edit pesan yang ada
        await update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)
    else:
        # Jika dipanggil dari perintah, kirim pesan baru
        await update.message.reply_text(text=text, reply_markup=reply_markup)


async def downloader_menu(update: Update, context: CallbackContext) -> None:
    """Menampilkan menu untuk fitur downloader."""
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("▶️ Mulai Cari Video", callback_data='start_video')],
        [InlineKeyboardButton("Kembali", callback_data='main_menu_back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "Anda berada di menu Downloader. Fitur ini dapat mencari dan mengunduh video atau audio dari YouTube."
    await query.edit_message_text(text=text, reply_markup=reply_markup)

async def search_menu(update: Update, context: CallbackContext) -> None:
    """Menampilkan menu untuk fitur pencarian."""
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("▶️ Mulai Cari Gambar", callback_data='start_gambar')],
        [InlineKeyboardButton("Kembali", callback_data='main_menu_back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "Anda berada di menu Pencarian. Fitur ini dapat mencari gambar dari internet."
    await query.edit_message_text(text=text, reply_markup=reply_markup)

async def islamic_menu(update: Update, context: CallbackContext) -> None:
    """Menampilkan menu untuk fitur Islami."""
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("▶️ Mulai Jadwal Azan", callback_data='start_azan')],
        [InlineKeyboardButton("Kembali", callback_data='main_menu_back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "Anda berada di menu Islami. Fitur ini dapat menampilkan jadwal salat untuk kota di Indonesia."
    await query.edit_message_text(text=text, reply_markup=reply_markup)

async def button_callback_handler(update: Update, context: CallbackContext) -> None:
    """Menangani semua klik tombol dari menu inline."""
    query = update.callback_query
    await query.answer()

    # Router untuk callback data
    if query.data == 'menu_downloader':
        await downloader_menu(update, context)
    elif query.data == 'menu_search':
        await search_menu(update, context)
    elif query.data == 'menu_islamic':
        await islamic_menu(update, context)
    elif query.data == 'main_menu_back':
        await main_menu(update, context)
    elif query.data == 'start_video':
        await start_video_search_from_menu(update, context)
    elif query.data == 'start_gambar':
        await start_image_search_from_menu(update, context)
    elif query.data == 'start_azan':
        await start_azan_search_from_menu(update, context)

async def handle_next_action(update: Update, context: CallbackContext):
    """Menangani pesan teks berdasarkan status yang tersimpan di user_data."""
    next_action = context.user_data.get('next_action')
    if not next_action:
        return

    query = update.message.text

    if next_action == 'cari_video':
        await perform_search(update.message, query, context)
    elif next_action == 'cari_gambar':
        await perform_gambar_search(update.message, query, context)
    elif next_action == 'jadwal_azan':
        await perform_azan_search(update.message, query)

    # Hapus status setelah selesai
    del context.user_data['next_action']

async def start_video_search_from_menu(update: Update, context: CallbackContext):
    """Memulai alur pencarian video dari menu."""
    query = update.callback_query
    context.user_data['next_action'] = 'cari_video'
    await query.edit_message_text("Silakan kirimkan judul video yang ingin Anda cari:")

async def start_image_search_from_menu(update: Update, context: CallbackContext):
    """Memulai alur pencarian gambar dari menu."""
    query = update.callback_query
    context.user_data['next_action'] = 'cari_gambar'
    await query.edit_message_text("Silakan masukkan kata kunci gambar yang ingin Anda cari:")

async def start_azan_search_from_menu(update: Update, context: CallbackContext):
    """Memulai alur jadwal azan dari menu."""
    query = update.callback_query
    context.user_data['next_action'] = 'jadwal_azan'
    await query.edit_message_text("Masukkan nama kota di Indonesia (contoh: Jakarta):")

# --- Fungsi Perintah Utama ---

async def cari_video(update: Update, context: CallbackContext):
    if context.args:
        query = " ".join(context.args)
        await perform_search(update.message, query, context)
    else:
        context.user_data['next_action'] = 'cari_video'
        await update.message.reply_text("Silakan masukkan judul video yang ingin Anda cari:")

async def cari_gambar(update: Update, context: CallbackContext):
    if context.args:
        query = " ".join(context.args)
        await perform_gambar_search(update.message, query, context)
    else:
        context.user_data['next_action'] = 'cari_gambar'
        await update.message.reply_text("Silakan masukkan kata kunci gambar yang ingin Anda cari:")

def search_images_sync(query: str):
    """Fungsi sinkron untuk menjalankan pencarian gambar."""
    results = ddg_search(query, max_results=5)
    return [r['image'] for r in results]

async def perform_gambar_search(message, query: str, context: CallbackContext):
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
    else:
        context.user_data['next_action'] = 'jadwal_azan'
        await update.message.reply_text("Masukkan nama kota di Indonesia (contoh: Jakarta):")

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

async def perform_search(message, query: str, context: CallbackContext):
    status_msg = await message.reply_text(f"🔎 Mencari `{query}`...", parse_mode='Markdown')
    try:
        ydl_opts = {
            'format': 'best',
            'noplaylist': True,
            'default_search': 'ytsearch5',
            'quiet': True,
        }
        with YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(f"ytsearch5:{query}", download=False)
            await status_msg.delete()
            if 'entries' in result and result['entries']:
                await message.reply_text("Berikut adalah hasil pencarian teratas:")
                for entry in result['entries']:
                    title = entry.get('title', 'N/A')
                    video_url = entry.get('webpage_url', '')
                    thumbnail_url = entry.get('thumbnail')
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
                            caption=title,
                            reply_markup=reply_markup
                        )
                    else:
                        await context.bot.send_message(
                            chat_id=message.chat_id,
                            text=title,
                            reply_markup=reply_markup
                        )
            else:
                await message.reply_text('Tidak ada hasil yang ditemukan!')
    except Exception as e:
        logging.error(f"Error saat mencari: {e}")
        await status_msg.edit_text("Terjadi kesalahan saat melakukan pencarian.")

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
    application = Application.builder().token(TOKEN).build()

    # Tambahkan handler
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("menu", main_menu))
    application.add_handler(CommandHandler("cari_video", cari_video))
    application.add_handler(CommandHandler("cari_gambar", cari_gambar))
    application.add_handler(CommandHandler("jadwal_azan", jadwal_azan))

    application.add_handler(CallbackQueryHandler(button_callback_handler))
    application.add_handler(CallbackQueryHandler(unduh_video, pattern='^unduh_video\\|'))
    application.add_handler(CallbackQueryHandler(unduh_audio, pattern='^unduh_audio\\|'))

    # Handler untuk memproses input teks setelah tombol menu ditekan
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_next_action))


    # Jalankan bot
    application.run_polling()

if __name__ == '__main__':
    main()