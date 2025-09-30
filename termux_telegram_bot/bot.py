# -*- coding: utf-8 -*-
import os
import logging
import asyncio
import json
from pathlib import Path
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
from telegram.constants import ParseMode
from duckduckgo_search import DDGS

# --- Konfigurasi Awal ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()
TOKEN = os.getenv('YOUR_TOKEN_HERE')

WELCOME_MESSAGE = """
🤖 **Selamat Datang di Bot Serbaguna!** 🤖

Saya bisa membantu Anda melakukan banyak hal:

📥 **/start** - Memulai bot.
🎵 **/carilagu** `[judul]` - Mencari 5 lagu teratas di YouTube.
⚡ **/caricepat** `[judul]` - Langsung mengunduh audio dari hasil pertama.
🖼️ **/cari_gambar** `[kata kunci]` - Mencari 5 gambar di web.
🔗 Kirim **link apa saja** untuk mengunduhnya sebagai video atau audio.
"""

# --- Fungsi Handler Utama ---

async def start(update: Update, context: CallbackContext) -> None:
    """Mengirim pesan selamat datang."""
    await update.message.reply_text(WELCOME_MESSAGE, parse_mode=ParseMode.MARKDOWN)

async def handle_url(update: Update, context: CallbackContext) -> None:
    """Menangani URL yang dikirim pengguna."""
    url = update.message.text
    logger.info(f"Menerima URL: {url}")
    keyboard = [[
        InlineKeyboardButton("🎬 Video", callback_data=f"download|video|{url}"),
        InlineKeyboardButton("🎵 Audio (Cepat)", callback_data=f"download|audio|{url}"),
    ]]
    await update.message.reply_text("Pilih format yang Anda inginkan:", reply_markup=InlineKeyboardMarkup(keyboard))

async def search_youtube(update: Update, context: CallbackContext) -> None:
    """Mencari 5 video teratas di YouTube."""
    query = ' '.join(context.args)
    if not query:
        await update.message.reply_text("Contoh: `/carilagu Tulus Monokrom`")
        return

    message = await update.message.reply_text(f"🔎 Mencari lagu *{query}*...", parse_mode=ParseMode.MARKDOWN)
    try:
        command = ['yt-dlp', '--dump-json', '--no-playlist', '--match-filter', 'duration < 600', f"ytsearch5:{query}"]
        process = await asyncio.create_subprocess_exec(*command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30.0)

        if process.returncode != 0:
            raise Exception(stderr.decode())

        results = [json.loads(line) for line in stdout.decode().strip().split('\n')]
        if not results:
            await message.edit_text(f"Maaf, tidak ada hasil untuk *{query}*.", parse_mode=ParseMode.MARKDOWN)
            return

        await message.delete()
        for video in results:
            url = video.get('webpage_url')
            caption = f"**{video.get('title', 'Tanpa Judul')}**\nDurasi: {video.get('duration_string', 'N/A')}"
            keyboard = [[
                InlineKeyboardButton("🎬 Video", callback_data=f"download|video|{url}"),
                InlineKeyboardButton("🎵 Audio (Cepat)", callback_data=f"download|audio|{url}")
            ]]
            if video.get('thumbnail'):
                await update.message.reply_photo(photo=video['thumbnail'], caption=caption, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logger.error(f"Error di search_youtube: {e}")
        await message.edit_text("Maaf, terjadi kesalahan saat mencari.")

async def search_youtube_quick(update: Update, context: CallbackContext) -> None:
    """Mencari dan langsung mengunduh audio dari hasil pertama."""
    query = ' '.join(context.args)
    if not query:
        await update.message.reply_text("Contoh: `/caricepat Tulus Monokrom`")
        return

    message = await update.message.reply_text(f"⚡ Mencari & menyiapkan audio untuk *{query}*...", parse_mode=ParseMode.MARKDOWN)
    try:
        command = ['yt-dlp', '--dump-json', '--no-playlist', f"ytsearch1:{query}"]
        process = await asyncio.create_subprocess_exec(*command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30.0)

        if process.returncode != 0:
            raise Exception(stderr.decode())

        result = json.loads(stdout)
        url = result.get('webpage_url')
        await message.edit_text(f"✅ Ditemukan! Mengunduh *{result.get('title', 'Tanpa Judul')}*...", parse_mode=ParseMode.MARKDOWN)
        await download_and_send(update.message.chat_id, 'audio', url, context, message)
    except Exception as e:
        logger.error(f"Error di search_youtube_quick: {e}")
        await message.edit_text("Gagal menemukan atau mengunduh lagu.")

async def search_images(update: Update, context: CallbackContext) -> None:
    """Mencari gambar menggunakan DuckDuckGo."""
    query = ' '.join(context.args)
    if not query:
        await update.message.reply_text("Contoh: `/cari_gambar kucing lucu`")
        return

    message = await update.message.reply_text(f"🖼️ Mencari gambar *{query}*...", parse_mode=ParseMode.MARKDOWN)
    try:
        results = await asyncio.to_thread(DDGS().images, keywords=query, max_results=5)
        if not results:
            await message.edit_text("Maaf, tidak ada gambar yang ditemukan.")
            return

        media_group = [InputMediaPhoto(media=res['image']) for res in results]
        await message.delete()
        await update.message.reply_media_group(media=media_group)
    except Exception as e:
        logger.error(f"Error di search_images: {e}")
        await message.edit_text("Maaf, terjadi kesalahan saat mencari gambar.")

# --- Fungsi Helper & Callback ---

async def button_callback(update: Update, context: CallbackContext) -> None:
    """Menangani klik tombol inline."""
    query = update.callback_query
    await query.answer()
    try:
        action, media_type, url = query.data.split('|', 2)
        if action == "download":
            await query.edit_message_text(text=f"🚀 Siap! Memproses permintaan {media_type}...")
            await download_and_send(query.message.chat_id, media_type, url, context, query.message)
    except Exception as e:
        logger.error(f"Error di button_callback: {e}")
        await query.edit_message_text("Maaf, terjadi kesalahan tak terduga.")

async def download_and_send(chat_id, media_type, url, context, message_to_edit):
    """Fungsi inti untuk mengunduh dan mengirim file (dengan optimasi audio)."""
    download_dir = Path("downloads")
    download_dir.mkdir(exist_ok=True)

    try:
        # Perintah dasar untuk mendapatkan nama file output
        base_command = ['yt-dlp', '--no-playlist', '--print', 'filename']

        # --- KUNCI PERBAIKAN TIMEOUT AUDIO ---
        if media_type == 'audio':
            # Langsung ambil format audio terbaik, tanpa konversi ulang. Sangat cepat.
            options = ['-f', 'bestaudio/best']
        else: # media_type == 'video'
            # Ambil format video MP4 terbaik
            options = ['-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', '--recode-video', 'mp4']

        output_template = str(download_dir / '%(title)s.%(ext)s')
        command = base_command + options + ['-o', output_template, url]

        # Jalankan yt-dlp untuk mengunduh dan mendapatkan nama file
        process = await asyncio.create_subprocess_exec(*command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300.0) # Timeout 5 menit

        if process.returncode != 0:
            raise Exception(stderr.decode())

        filepath_str = stdout.decode().strip().split('\n')[-1] # Ambil baris terakhir jika ada output lain
        if not filepath_str:
            raise FileNotFoundError("yt-dlp tidak mengembalikan nama file.")

        filepath = Path(filepath_str)
        if not filepath.exists():
            raise FileNotFoundError(f"File yang diunduh tidak ditemukan di: {filepath}")

        # Kirim file
        await message_to_edit.edit_text("✅ Download selesai! Mengirim file...")

        if media_type == 'audio':
            await context.bot.send_audio(chat_id=chat_id, audio=filepath.open('rb'), write_timeout=60)
        else:
            await context.bot.send_video(chat_id=chat_id, video=filepath.open('rb'), write_timeout=60)

        # Hapus file setelah dikirim
        filepath.unlink()
        await message_to_edit.delete()

    except asyncio.TimeoutError:
        await message_to_edit.edit_text("Download terlalu lama dan dibatalkan. Coba lagi dengan koneksi yang lebih stabil.")
    except Exception as e:
        logger.error(f"Error di download_and_send: {e}")
        await message_to_edit.edit_text(f"Gagal mengunduh atau mengirim file.\nInfo: {e}")
    finally:
        try:
            await message_to_edit.delete()
        except:
            pass

async def error_handler(update: object, context: CallbackContext) -> None:
    """Log error dan beritahu pengguna."""
    logger.error("Exception while handling an update:", exc_info=context.error)
    if update and update.effective_message:
        await update.effective_message.reply_text(f"Aduh, maaf, ada kesalahan teknis nih. Coba lagi nanti ya.\n\nInfo Error:\n{context.error}")

def main() -> None:
    """Jalankan bot."""
    if not TOKEN:
        logger.critical("Token bot tidak ditemukan. Pastikan file .env sudah ada dan berisi TOKEN.")
        return

    application = Application.builder().token(TOKEN).connect_timeout(60).read_timeout(60).build()

    # Daftarkan semua handler
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("carilagu", search_youtube))
    application.add_handler(CommandHandler("caricepat", search_youtube_quick))
    application.add_handler(CommandHandler("cari_gambar", search_images))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_error_handler(error_handler)

    logger.info("Bot mulai berjalan dengan unduhan audio yang dioptimalkan...")
    application.run_polling()

if __name__ == '__main__':
    main()