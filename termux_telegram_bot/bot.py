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
from ddgs import DDGS
import itertools

# --- Konfigurasi Awal ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')

WELCOME_MESSAGE = """
🤖 **Selamat Datang di Bot Serbaguna!** 🤖

Saya bisa membantu Anda melakukan banyak hal:

📥 **/start** - Memulai bot.
🎵 **/carilagu** `[judul]` - Mencari 5 lagu teratas di YouTube.
⚡ **/caricepat** `[judul]` - Langsung mengunduh audio dari hasil pertama.
🖼️ **/cari_gambar** `[kata kunci]` - Mencari 5 gambar teratas.
🔗 Kirim **link apa saja** untuk mengunduhnya sebagai video atau audio.
"""

# Kunci untuk menyimpan state dalam context.user_data
WAITING_FOR = 'waiting_for_input'

# --- Fungsi Logika Inti ---

def sync_image_search(query):
    """Fungsi sinkron untuk menjalankan pencarian gambar."""
    results = DDGS().images(query, max_results=10)
    # Ambil 5 URL gambar pertama yang valid
    image_urls = [r.get('image') for r in results if r.get('image')][:5]
    return image_urls

async def execute_search_images(query: str, update: Update, context: CallbackContext):
    """Fungsi logika untuk mencari dan mengirim gambar."""
    message = await update.message.reply_text(f"🖼️ Mencari gambar untuk *{query}*...", parse_mode=ParseMode.MARKDOWN)
    try:
        # Jalankan fungsi sinkron di thread terpisah agar tidak memblokir
        image_urls = await asyncio.to_thread(sync_image_search, query)

        if not image_urls:
            await message.edit_text("Maaf, tidak ada gambar yang ditemukan.")
            return

        media_group = [InputMediaPhoto(media=url) for url in image_urls]

        await context.bot.send_media_group(chat_id=update.effective_chat.id, media=media_group)
        await message.delete()

    except Exception as e:
        logger.error(f"Error di execute_search_images: {e}")
        await message.edit_text("Maaf, terjadi kesalahan saat mencari gambar.")


async def execute_search_youtube(query: str, update: Update, context: CallbackContext):
    """Fungsi logika untuk mencari 5 video YouTube teratas."""
    message = await update.message.reply_text(f"🔎 Mencari lagu *{query}*...", parse_mode=ParseMode.MARKDOWN)
    try:
        # Filter durasi dihapus karena bisa tidak stabil
        command = ['yt-dlp', '--dump-json', '--no-playlist', f"ytsearch5:{query}"]
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
        logger.error(f"Error di execute_search_youtube: {e}")
        await message.edit_text("Maaf, terjadi kesalahan saat mencari.")


async def execute_search_youtube_quick(query: str, update: Update, context: CallbackContext):
    """Fungsi logika untuk mencari dan mengunduh audio dari hasil pertama."""
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
        logger.error(f"Error di execute_search_youtube_quick: {e}")
        await message.edit_text("Gagal menemukan atau mengunduh lagu.")

# --- Handler Perintah Interaktif ---

async def search_images(update: Update, context: CallbackContext) -> None:
    """Memulai pencarian gambar. Meminta input jika tidak ada query."""
    if context.args:
        query = ' '.join(context.args)
        await execute_search_images(query, update, context)
    else:
        await update.message.reply_text("Mau cari gambar apa?")
        context.user_data[WAITING_FOR] = 'cari_gambar'

async def search_youtube(update: Update, context: CallbackContext) -> None:
    """Memulai pencarian lagu. Meminta input jika tidak ada query."""
    if context.args:
        query = ' '.join(context.args)
        await execute_search_youtube(query, update, context)
    else:
        await update.message.reply_text("Lagu apa yang ingin Anda cari?")
        context.user_data[WAITING_FOR] = 'carilagu'

async def search_youtube_quick(update: Update, context: CallbackContext) -> None:
    """Memulai pencarian cepat. Meminta input jika tidak ada query."""
    if context.args:
        query = ' '.join(context.args)
        await execute_search_youtube_quick(query, update, context)
    else:
        await update.message.reply_text("Lagu apa yang ingin Anda unduh cepat?")
        context.user_data[WAITING_FOR] = 'caricepat'

async def handle_response(update: Update, context: CallbackContext) -> None:
    """Menangani input teks dari pengguna saat bot menunggu."""
    if WAITING_FOR in context.user_data:
        command = context.user_data.pop(WAITING_FOR)
        query = update.message.text

        if command == 'carilagu':
            await execute_search_youtube(query, update, context)
        elif command == 'caricepat':
            await execute_search_youtube_quick(query, update, context)
        elif command == 'cari_gambar':
            await execute_search_images(query, update, context)
    else:
        # Jika tidak menunggu input spesifik, anggap sebagai URL
        await handle_url(update, context)


# --- Handler Umum & Helper ---

async def start(update: Update, context: CallbackContext) -> None:
    """Mengirim pesan selamat datang."""
    await update.message.reply_text(WELCOME_MESSAGE, parse_mode=ParseMode.MARKDOWN)

async def handle_url(update: Update, context: CallbackContext) -> None:
    """Menangani URL yang dikirim pengguna."""
    url = update.message.text
    # Filter sederhana untuk memastikan itu terlihat seperti URL
    if "http" not in url and "://" not in url:
        await update.message.reply_text("Maaf, saya tidak mengerti. Jika Anda ingin mengunduh, kirimkan link. Jika ingin mencari sesuatu, gunakan perintah seperti `/carilagu`.")
        return

    logger.info(f"Menerima URL: {url}")
    keyboard = [[
        InlineKeyboardButton("🎬 Video", callback_data=f"download|video|{url}"),
        InlineKeyboardButton("🎵 Audio (Cepat)", callback_data=f"download|audio|{url}"),
    ]]
    await update.message.reply_text("Pilih format yang Anda inginkan:", reply_markup=InlineKeyboardMarkup(keyboard))

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
        base_command = ['yt-dlp', '--no-playlist', '--print', 'filename']

        if media_type == 'audio':
            options = ['-f', 'bestaudio/best']
        else:
            # Opsi yang lebih kuat untuk memilih video & audio terbaik dari sumber mana pun
            options = ['-f', 'bv*+ba/b', '--recode-video', 'mp4']

        output_template = str(download_dir / '%(title)s.%(ext)s')
        command = base_command + options + ['-o', output_template, url]

        process = await asyncio.create_subprocess_exec(*command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300.0)

        if process.returncode != 0:
            raise Exception(stderr.decode())

        filepath_str = stdout.decode().strip().split('\n')[-1]
        if not filepath_str:
            raise FileNotFoundError("yt-dlp tidak mengembalikan nama file.")

        filepath = Path(filepath_str)
        if not filepath.exists():
            raise FileNotFoundError(f"File yang diunduh tidak ditemukan di: {filepath}")

        await message_to_edit.edit_text("✅ Download selesai! Mengirim file...")

        if media_type == 'audio':
            await context.bot.send_audio(chat_id=chat_id, audio=filepath.open('rb'), write_timeout=60)
        else:
            await context.bot.send_video(chat_id=chat_id, video=filepath.open('rb'), write_timeout=60)

        filepath.unlink()
        await message_to_edit.delete()

    except asyncio.TimeoutError:
        await message_to_edit.edit_text("Download terlalu lama dan dibatalkan.")
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

    # Handler Perintah
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("carilagu", search_youtube))
    application.add_handler(CommandHandler("caricepat", search_youtube_quick))
    application.add_handler(CommandHandler("cari_gambar", search_images))

    # Handler untuk respons interaktif dan URL
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_response))

    # Handler Lainnya
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_error_handler(error_handler)

    logger.info("Bot mulai berjalan dengan fitur interaktif...")
    application.run_polling()

if __name__ == '__main__':
    main()