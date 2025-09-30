# -*- coding: utf-8 -*-
import os
import logging
import asyncio
import json
from pathlib import Path
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Application, ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
from telegram.constants import ParseMode
from duckduckgo_search import DDGS

# Konfigurasi logging untuk memantau bot
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Muat variabel lingkungan dari file .env
load_dotenv()
TOKEN = os.getenv('YOUR_TOKEN_HERE')
PROXY_URL = os.getenv('PROXY_URL') # URL Proxy, contoh: socks5://user:pass@host:port

# Pesan selamat datang dan bantuan
WELCOME_MESSAGE = """
🤖 **Selamat Datang di Bot Serbaguna!** 🤖

Hai! Saya adalah bot yang bisa membantu kamu melakukan banyak hal langsung dari Telegram.

Berikut adalah beberapa perintah yang bisa kamu gunakan:

📥 **/start** - Untuk memulai bot dan melihat pesan ini.
🎵 **/carilagu** `[judul lagu]` - Cari 5 lagu teratas dari YouTube.
⚡ **/caricepat** `[judul lagu]` - Langsung unduh audio dari hasil pencarian pertama.
🖼️ **/cari_gambar** `[kata kunci]` - Cari 5 gambar dari web. (Tambahkan `site:pinterest.com` untuk mencari di Pinterest).
🔗 Kirim saya **link apa saja** (YouTube, TikTok, dll.) dan saya akan bantu mengunduhnya sebagai video atau audio.

Ketik perintah atau kirim link untuk memulai!
"""

# --- FUNGSI UTAMA ---

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(WELCOME_MESSAGE, parse_mode=ParseMode.MARKDOWN)

async def handle_url(update: Update, context: CallbackContext) -> None:
    url = update.message.text
    logger.info(f"Menerima URL dari pengguna: {url}")
    keyboard = [[
        InlineKeyboardButton("🎬 Video", callback_data=f"download|video|{url}"),
        InlineKeyboardButton("🎵 Audio", callback_data=f"download|audio|{url}"),
    ]]
    await update.message.reply_text("Pilih format yang kamu inginkan:", reply_markup=InlineKeyboardMarkup(keyboard))

async def search_youtube(update: Update, context: CallbackContext) -> None:
    query = ' '.join(context.args)
    if not query:
        await update.message.reply_text("Contoh: `/carilagu Tulus Monokrom`")
        return
    message = await update.message.reply_text(f"🔎 Mencari lagu *{query}*...", parse_mode=ParseMode.MARKDOWN)
    try:
        command = ['yt-dlp', '-4', '--dump-json', '--no-playlist', '--match-filter', 'duration < 600', f"ytsearch5:{query}"]
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
            keyboard = [[InlineKeyboardButton("🎬 Video", callback_data=f"download|video|{url}"), InlineKeyboardButton("🎵 Audio", callback_data=f"download|audio|{url}")]]
            if video.get('thumbnail'):
                await update.message.reply_photo(photo=video['thumbnail'], caption=caption, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logger.error(f"Error di search_youtube: {e}")
        await message.edit_text("Maaf, terjadi kesalahan saat mencari.")

async def search_youtube_quick(update: Update, context: CallbackContext) -> None:
    query = ' '.join(context.args)
    if not query:
        await update.message.reply_text("Contoh: `/caricepat Tulus Monokrom`")
        return
    message = await update.message.reply_text(f"⚡ Mencari & menyiapkan audio untuk *{query}*...", parse_mode=ParseMode.MARKDOWN)
    try:
        command = ['yt-dlp', '-4', '--dump-json', '--no-playlist', f"ytsearch1:{query}"]
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

async def button_callback(update: Update, context: CallbackContext) -> None:
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
    download_dir = Path("downloads")
    download_dir.mkdir(exist_ok=True)
    try:
        base_command = ['yt-dlp', '-4', '--no-playlist', '--print', 'filename']
        if media_type == 'audio':
            options = ['-f', 'bestaudio/best', '-x', '--audio-format', 'mp3']
        else:
            options = ['-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', '--recode-video', 'mp4']
        output_template = str(download_dir / '%(id)s.%(ext)s')
        command = base_command + options + ['-o', output_template, url]
        process = await asyncio.create_subprocess_exec(*command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300.0)
        if process.returncode != 0:
            raise Exception(stderr.decode())
        filepath = Path(stdout.decode().strip())
        if not filepath.exists():
            raise FileNotFoundError(f"File tidak ditemukan di: {filepath}")
        await message_to_edit.edit_text("✅ Download selesai! Mengirim file...")
        if media_type == 'audio':
            await context.bot.send_audio(chat_id=chat_id, audio=filepath.open('rb'), write_timeout=60)
        else:
            await context.bot.send_video(chat_id=chat_id, video=filepath.open('rb'), write_timeout=60)
        filepath.unlink()
        await message_to_edit.delete()
    except Exception as e:
        logger.error(f"Error di download_and_send: {e}")
        await message_to_edit.edit_text(f"Gagal mengunduh atau mengirim file.\nError: {e}")

async def error_handler(update: object, context: CallbackContext) -> None:
    logger.error("Exception while handling an update:", exc_info=context.error)

def main() -> None:
    if not TOKEN:
        logger.critical("Token bot tidak ditemukan. Pastikan file .env sudah ada dan berisi TOKEN.")
        return

    builder = Application.builder().token(TOKEN).connect_timeout(60).read_timeout(60)

    # --- KONFIGURASI PROXY ---
    if PROXY_URL:
        logger.info(f"Menggunakan proxy: {PROXY_URL}")
        builder.proxy_url(PROXY_URL)
        builder.get_updates_proxy_url(PROXY_URL)
    else:
        logger.info("Tidak ada proxy yang dikonfigurasi. Menjalankan koneksi langsung.")

    application = builder.build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("carilagu", search_youtube))
    application.add_handler(CommandHandler("caricepat", search_youtube_quick))
    application.add_handler(CommandHandler("cari_gambar", search_images))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_error_handler(error_handler)

    logger.info("Bot mulai berjalan...")
    application.run_polling()

if __name__ == '__main__':
    main()