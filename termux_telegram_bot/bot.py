import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler, ConversationHandler
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

# Mengatur level log untuk library yang "berisik" agar tidak membanjiri log
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("telegram.ext").setLevel(logging.WARNING)

# States untuk ConversationHandlers
GET_VIDEO_QUERY, GET_GAMBAR_QUERY, GET_AZAN_QUERY = range(3)

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
        "/cari_video <judul> - Mencari 5 video YouTube teratas.\n"
        "/cari_gambar <kata_kunci> - Mencari 5 gambar teratas dari DuckDuckGo.\n"
        "/jadwal_azan <daerah> - Menampilkan jadwal azan untuk daerah tertentu.\n"
        "/help - Menampilkan pesan bantuan ini.\n\n"
        "Fitur jadwal JKT48 untuk sementara dinonaktifkan karena tidak ada sumber data yang stabil.\n"
        "Anda bisa menjalankan perintah tanpa argumen, dan saya akan menanyakannya.",
        parse_mode='Markdown'
    )

# Fungsi untuk cari video
async def cari_video(update: Update, context: CallbackContext):
    if context.args:
        query = " ".join(context.args)
        await perform_search(update.message, query, context)
        return ConversationHandler.END
    await update.message.reply_text("Silakan masukkan judul video yang ingin Anda cari:")
    return GET_VIDEO_QUERY

async def get_video_query(update: Update, context: CallbackContext):
    await perform_search(update.message, update.message.text, context)
    return ConversationHandler.END

# Fungsi untuk cari gambar
async def cari_gambar(update: Update, context: CallbackContext):
    if context.args:
        query = " ".join(context.args)
        await perform_gambar_search(update.message, query, context)
        return ConversationHandler.END
    await update.message.reply_text("Silakan masukkan kata kunci gambar yang ingin Anda cari:")
    return GET_GAMBAR_QUERY

async def get_gambar_query(update: Update, context: CallbackContext):
    await perform_gambar_search(update.message, update.message.text, context)
    return ConversationHandler.END

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

    # Conversation handler untuk pencarian video
    video_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("cari_video", cari_video)],
        states={
            GET_VIDEO_QUERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_video_query)]
        },
        fallbacks=[CommandHandler("start", start)],
    )

    # Conversation handler untuk pencarian gambar
    gambar_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("cari_gambar", cari_gambar)],
        states={
            GET_GAMBAR_QUERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_gambar_query)]
        },
        fallbacks=[CommandHandler("start", start)],
    )

    # Conversation handler untuk jadwal azan
    azan_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("jadwal_azan", jadwal_azan)],
        states={
            GET_AZAN_QUERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_azan_query)]
        },
        fallbacks=[CommandHandler("start", start)],
    )

    # Tambahkan handler
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(video_conv_handler)
    application.add_handler(gambar_conv_handler)
    application.add_handler(azan_conv_handler)
    application.add_handler(CallbackQueryHandler(unduh_video, pattern='^unduh_video\\|'))
    application.add_handler(CallbackQueryHandler(unduh_audio, pattern='^unduh_audio\\|'))

    # Jalankan bot
    application.run_polling()

if __name__ == '__main__':
    main()