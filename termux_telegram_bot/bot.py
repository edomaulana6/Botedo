import logging
import os
import subprocess
import uuid
from pathlib import Path
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InputMediaPhoto
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from youtubesearchpython import VideosSearch
import html
import requests
import re

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Helper Functions ---

def parse_duration_to_seconds(duration_str: str) -> int:
    """Safely parses a duration string into seconds."""
    if not duration_str: return float('inf')
    parts = duration_str.split(':')
    seconds = 0
    try:
        if len(parts) == 3: seconds = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        elif len(parts) == 2: seconds = int(parts[0]) * 60 + int(parts[1])
        elif len(parts) == 1: seconds = int(parts[0])
        return seconds
    except (ValueError, IndexError): return float('inf')

# --- Core Logic ---

async def download_and_send(chat_id: int, url: str, format_choice: str, context: ContextTypes.DEFAULT_TYPE, status_message=None):
    """Downloads a file and sends it, with conversational status updates."""
    edit_message = status_message.edit_text if status_message else context.bot.send_message

    try:
        await edit_message(text=f"Oke, sabar ya... Lagi proses download {format_choice}-nya nih... ⏳")

        download_dir = Path(f"./downloads/{uuid.uuid4()}")
        download_dir.mkdir(parents=True, exist_ok=True)

        if format_choice == 'audio':
            command = ['yt-dlp', '-x', '--audio-format', 'mp3', '-o', f'{download_dir}/%(title)s.%(ext)s', '--ffmpeg-location', '/data/data/com.termux/files/usr/bin/ffmpeg', url]
        else:
            command = ['yt-dlp', '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', '-o', f'{download_dir}/%(title)s.%(ext)s', url]

        process = subprocess.run(command, capture_output=True, text=True, check=True)
        logger.info(f"yt-dlp stdout: {process.stdout}")

        downloaded_files = list(download_dir.iterdir())
        if not downloaded_files: raise FileNotFoundError("Duh, filenya gak ketemu setelah di-download.")

        file_path = downloaded_files[0]

        await edit_message(text=f"Sip, udah ke-download! Sekarang lagi ngirim filenya... 📤")

        if format_choice == 'audio':
            await context.bot.send_audio(chat_id=chat_id, audio=open(file_path, 'rb'), filename=file_path.name)
        else:
            await context.bot.send_video(chat_id=chat_id, video=open(file_path, 'rb'), filename=file_path.name)

        await edit_message(text="Nih, filenya udah kekirim! ✅")

    except subprocess.CalledProcessError as e:
        stderr_lower = e.stderr.lower()
        logger.error(f"yt-dlp error for {url}: {e.stderr}")

        if "unable to extract" in stderr_lower or "report this issue" in stderr_lower:
            error_message = (
                "Waduh, gagal download dari link itu. 😥\n\n"
                "Ini biasanya karena website (seperti TikTok/Instagram) baru saja update, jadi botnya perlu penyesuaian.\n\n"
                "**Solusi Cepat:**\n"
                "1. Matikan bot ini dulu (tekan `Ctrl` + `C`).\n"
                "2. Jalankan perintah ini di Termux:\n"
                "`pip install --upgrade yt-dlp`\n"
                "3. Nyalakan lagi botnya.\n\n"
                "Kalau cara di atas gak berhasil, berarti link-nya mungkin emang gak didukung saat ini."
            )
            await edit_message(text=error_message, parse_mode='Markdown')
        else:
            error_message = f"Waduh, gagal download nih. Kayaknya ada masalah sama link atau formatnya.\n\n*Pesan Error:*\n`{e.stderr[:200]}`"
            await edit_message(text=error_message, parse_mode='Markdown')

    except Exception as e:
        error_message = f"Aduh, maaf, ada kesalahan teknis nih. Coba lagi nanti ya.\n\n*Info Error:*\n`{str(e)}`"
        logger.error(f"Error downloading {url}: {e}")
        await edit_message(text=error_message, parse_mode='Markdown')
    finally:
        try:
            for item in download_dir.iterdir(): item.unlink()
            download_dir.rmdir()
        except Exception as e:
            logger.error(f"Gagal hapus folder sementara {download_dir}: {e}")

# --- Command Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Greets the user and shows the main menu."""
    keyboard = [
        [InlineKeyboardButton("⬇️ Download dari Link", callback_data='menu_download_url')],
        [InlineKeyboardButton("🎵 Cari Lagu YouTube", callback_data='menu_search_youtube')],
        [InlineKeyboardButton("🖼️ Cari Foto Pinterest", callback_data='menu_search_pinterest')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 Halo! Aku bot serbaguna.\n\nMau aku bantu apa hari ini? Tinggal pencet tombol di bawah ya!",
        reply_markup=reply_markup
    )

async def caricepat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Asks for a song title for quick search."""
    context.user_data['state'] = 'awaiting_quick_search'
    await update.message.reply_text("Oke, mau cari lagu apa? Kirim judulnya aja, nanti aku langsung jadiin audio. 🎵")

# --- Callback Query & Message Handlers ---

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles all button presses."""
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == 'menu_download_url':
        context.user_data['state'] = 'awaiting_url'
        await query.edit_message_text(text="Oke, sini kasih aku link-nya. Nanti aku download-in. ▶️")
    elif data == 'menu_search_youtube':
        context.user_data['state'] = 'awaiting_youtube_search'
        await query.edit_message_text(text="Sip, mau cari lagu apa di YouTube? Ketik judulnya di sini. 🎵")
    elif data == 'menu_search_pinterest':
        context.user_data['state'] = 'awaiting_pinterest_search'
        await query.edit_message_text(text="Asik, mau cari gambar apa di Pinterest? Kasih tau kata kuncinya ya. 🖼️")
    elif data.startswith('dl_'):
        _, format_choice, url = data.split(':', 2)
        await download_and_send(query.message.chat_id, url, format_choice, context, status_message=query.message)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles text messages based on bot's state."""
    state = context.user_data.get('state')
    if not state: return

    context.user_data['state'] = None # Reset state after processing
    if state == 'awaiting_url': await handle_url_input(update, context)
    elif state == 'awaiting_youtube_search': await handle_youtube_search(update, context)
    elif state == 'awaiting_quick_search': await handle_quick_search(update, context)
    elif state == 'awaiting_pinterest_search': await handle_pinterest_search(update, context)

async def handle_url_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Asks for download format after receiving a URL."""
    url = update.message.text
    if not (url.startswith('http://') or url.startswith('https://')):
        await update.message.reply_text("Hmm, link-nya kayaknya gak bener deh. Coba cek lagi ya. ⚠️")
        return

    keyboard = [[
        InlineKeyboardButton("🎬 Video", callback_data=f'dl_video:{url}'),
        InlineKeyboardButton("🎵 Audio", callback_data=f'dl_audio:{url}'),
    ]]
    await update.message.reply_text("Link diterima! Mau dijadiin video atau audio nih?", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_youtube_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Searches YouTube and shows top 5 results."""
    query = update.message.text
    status_msg = await update.message.reply_text(f"Oke, aku cariin \"{html.escape(query)}\" di YouTube ya... 🔎")

    try:
        videos_search = VideosSearch(query, limit=5)
        results = [v for v in videos_search.result()['result'] if parse_duration_to_seconds(v.get('duration')) < 600]

        if not results:
            await status_msg.edit_text("Yah, lagu yang kamu cari gak ketemu. Coba pake kata kunci lain. 😕")
            return

        await status_msg.delete()
        for video in results:
            caption = (f"<b>{html.escape(video['title'])}</b>\n\n"
                       f"🕒 Durasi: {video['duration']}\n"
                       f"👤 Channel: {html.escape(video['channel']['name'])}")
            keyboard = [[
                InlineKeyboardButton("🎬 Video", callback_data=f"dl_video:{video['link']}"),
                InlineKeyboardButton("🎵 Audio", callback_data=f"dl_audio:{video['link']}")
            ]]
            await update.message.reply_photo(
                photo=video['thumbnails'][0]['url'], caption=caption,
                reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML'
            )
    except Exception as e:
        logger.error(f"Error YouTube search: {e}")
        await status_msg.edit_text("Waduh, ada error pas nyari di YouTube. Maaf ya. 😥")

async def handle_quick_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Finds top YouTube result and downloads audio."""
    query = update.message.text
    chat_id = update.message.chat_id
    status_msg = await update.message.reply_text(f"Cari cepet buat \"{html.escape(query)}\"... 🚀")

    try:
        videos_search = VideosSearch(query, limit=1)
        results = videos_search.result()['result']
        if not results:
            await status_msg.edit_text("Yah, gak ketemu lagunya. Coba judul lain. 😕")
            return

        top_result = results[0]
        await status_msg.delete()

        await update.message.reply_photo(
            photo=top_result['thumbnails'][0]['url'],
            caption=f"Ketemu! Ini lagunya:\n<b>{html.escape(top_result['title'])}</b>",
            parse_mode='HTML'
        )

        download_status_msg = await update.message.reply_text("Siap-siap, aku unduh audionya...")
        await download_and_send(chat_id, top_result['link'], 'audio', context, status_message=download_status_msg)

    except Exception as e:
        logger.error(f"Error quick search: {e}")
        await status_msg.edit_text("Aduh, ada error pas lagi cari cepet. Maaf ya. 😥")

async def handle_pinterest_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Scrapes Pinterest for images and sends top 5."""
    query = update.message.text
    status_msg = await update.message.reply_text(f"Sip, aku cariin gambar \"{html.escape(query)}\" di Pinterest... 🎨")

    try:
        url = f"https://www.pinterest.com/search/pins/?q={requests.utils.quote(query)}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        image_urls = list(dict.fromkeys(re.findall(r'"url":"(https://i\.pinimg\.com/originals/[^"]+\.jpg)"', response.text)))

        if not image_urls:
            await status_msg.edit_text("Hmm, gambarnya gak ketemu. Coba kata kunci yang lain. 😕")
            return

        await status_msg.edit_text(f"Dapet {len(image_urls[:5])} gambar! Aku kirim ya...")
        media_group = [InputMediaPhoto(media=url) for url in image_urls[:5]]
        media_group[0].caption = f"Ini dia 5 gambar teratas buat \"{html.escape(query)}\""
        await context.bot.send_media_group(chat_id=update.effective_chat.id, media=media_group)
        await status_msg.delete()

    except requests.RequestException as e:
        logger.error(f"Error fetching Pinterest: {e}")
        await status_msg.edit_text("Duh, gagal nyambung ke Pinterest nih. Coba lagi nanti, ya.")
    except Exception as e:
        logger.error(f"Error Pinterest search: {e}")
        await status_msg.edit_text("Waduh, ada error pas nyari gambar. Maaf ya. 😥")

# --- Main Application Setup ---

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Logs errors."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main() -> None:
    """Starts the bot."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token or token == "YOUR_TOKEN_HERE":
        logger.error("TOKEN BOT BELUM DISET!")
        print("\n======================================================")
        print("🛑 WADUH, TOKEN BOT KAMU BELUM DIMASUKIN! 🛑")
        print("Buka file .env, terus ganti YOUR_TOKEN_HERE dengan token bot kamu.")
        print("Bisa dapet token dari @BotFather di Telegram.")
        print("======================================================\n")
        return

    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("caricepat", caricepat))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    application.add_error_handler(error_handler)

    logger.info("Bot mulai jalan...")
    application.run_polling()

if __name__ == "__main__":
    main()