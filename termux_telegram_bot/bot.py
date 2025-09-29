import logging
import os
import subprocess
import uuid
from pathlib import Path
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from youtubesearchpython import VideosSearch
import html
import requests
import re
from telegram import InputMediaPhoto

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Helper Functions ---

def parse_duration_to_seconds(duration_str: str) -> int:
    """Safely parses a duration string (e.g., '1:23:45', '12:34', '56') into seconds."""
    if not duration_str:
        return float('inf')
    parts = duration_str.split(':')
    seconds = 0
    try:
        if len(parts) == 3:
            seconds = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        elif len(parts) == 2:
            seconds = int(parts[0]) * 60 + int(parts[1])
        elif len(parts) == 1:
            seconds = int(parts[0])
        return seconds
    except (ValueError, IndexError):
        return float('inf')

# --- Core Logic ---

async def download_and_send(chat_id: int, url: str, format_choice: str, context: ContextTypes.DEFAULT_TYPE, status_message=None):
    """
    Downloads a file from a URL using yt-dlp and sends it to the chat.
    Edits a status message to show progress.
    """
    edit_message = status_message.edit_text if status_message else context.bot.send_message

    try:
        await edit_message(text=f"⏳ Mengunduh {format_choice}, harap tunggu...")

        download_dir = Path(f"./downloads/{uuid.uuid4()}")
        download_dir.mkdir(parents=True, exist_ok=True)

        if format_choice == 'audio':
            command = [
                'yt-dlp', '-x', '--audio-format', 'mp3',
                '-o', f'{download_dir}/%(title)s.%(ext)s',
                '--ffmpeg-location', '/data/data/com.termux/files/usr/bin/ffmpeg', url
            ]
        else:
            command = [
                'yt-dlp', '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                '-o', f'{download_dir}/%(title)s.%(ext)s', url
            ]

        process = subprocess.run(command, capture_output=True, text=True, check=True)
        logger.info(f"yt-dlp stdout: {process.stdout}")

        downloaded_files = list(download_dir.iterdir())
        if not downloaded_files:
            raise FileNotFoundError("File tidak ditemukan setelah proses unduhan.")

        file_path = downloaded_files[0]

        await edit_message(text=f"📤 Mengirim {format_choice}...")

        if format_choice == 'audio':
            await context.bot.send_audio(chat_id=chat_id, audio=open(file_path, 'rb'), filename=file_path.name)
        else:
            await context.bot.send_video(chat_id=chat_id, video=open(file_path, 'rb'), filename=file_path.name)

        await edit_message(text="✅ Berhasil dikirim!")

    except subprocess.CalledProcessError as e:
        error_message = f"❌ Gagal mengunduh file.\nError: {e.stderr[:200]}"
        logger.error(f"yt-dlp error for {url}: {e.stderr}")
        await edit_message(text=error_message)

    except Exception as e:
        error_message = f"❌ Terjadi kesalahan.\nError: {str(e)}"
        logger.error(f"Error downloading {url}: {e}")
        await edit_message(text=error_message)

    finally:
        try:
            for item in download_dir.iterdir():
                item.unlink()
            download_dir.rmdir()
        except Exception as e:
            logger.error(f"Error cleaning up directory {download_dir}: {e}")

# --- Command Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message with a welcome text and a main menu keyboard."""
    keyboard = [
        [InlineKeyboardButton("⬇️ Unduh dari URL", callback_data='menu_download_url')],
        [InlineKeyboardButton("🎵 Cari Lagu YouTube", callback_data='menu_search_youtube')],
        [InlineKeyboardButton("🖼️ Cari Foto Pinterest", callback_data='menu_search_pinterest')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 Halo! Saya adalah bot asisten Anda.\n\nPilih salah satu opsi di bawah ini untuk memulai:",
        reply_markup=reply_markup
    )

async def caricepat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Asks the user for a song title for a quick search."""
    context.user_data['state'] = 'awaiting_quick_search'
    await update.message.reply_text("🎵 Silakan kirimkan judul lagu untuk diunduh cepat (audio).")

# --- Callback Query & Message Handlers ---

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses all CallbackQuery updates."""
    query = update.callback_query
    await query.answer()

    data = query.data

    if data.startswith('menu_'):
        if data == 'menu_download_url':
            context.user_data['state'] = 'awaiting_url'
            await query.edit_message_text(text="▶️ Silakan kirimkan URL yang ingin Anda unduh.")
        elif data == 'menu_search_youtube':
            context.user_data['state'] = 'awaiting_youtube_search'
            await query.edit_message_text(text="🎵 Silakan kirimkan judul lagu yang ingin Anda cari.")
        elif data == 'menu_search_pinterest':
            context.user_data['state'] = 'awaiting_pinterest_search'
            await query.edit_message_text(text="🖼️ Silakan kirimkan kata kunci untuk mencari gambar.")

    elif data.startswith('dl_'):
        _, format_choice, url = data.split(':', 2)
        await download_and_send(query.message.chat_id, url, format_choice, context, status_message=query.message)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles text messages based on the bot's current state."""
    state = context.user_data.get('state')
    if not state:
        return

    # Clear state after processing
    context.user_data['state'] = None

    if state == 'awaiting_url':
        await handle_url_input(update, context)
    elif state == 'awaiting_youtube_search':
        await handle_youtube_search(update, context)
    elif state == 'awaiting_quick_search':
        await handle_quick_search(update, context)
    elif state == 'awaiting_pinterest_search':
        await handle_pinterest_search(update, context)

async def handle_url_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Processes a URL sent by the user and shows download options."""
    url = update.message.text
    if not (url.startswith('http://') or url.startswith('https://')):
        await update.message.reply_text("⚠️ URL tidak valid. Harap kirimkan URL yang benar.")
        return

    keyboard = [
        [
            InlineKeyboardButton("🎬 Video", callback_data=f'dl_video:{url}'),
            InlineKeyboardButton("🎵 Audio", callback_data=f'dl_audio:{url}'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Pilih format unduhan:", reply_markup=reply_markup)

async def handle_youtube_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Searches YouTube and displays the top 5 results."""
    query = update.message.text
    await update.message.reply_text(f"🔎 Mencari lagu: \"{html.escape(query)}\"...", parse_mode='HTML')

    try:
        videos_search = VideosSearch(query, limit=5)
        results = [v for v in videos_search.result()['result'] if parse_duration_to_seconds(v.get('duration')) < 600]

        if not results:
            await update.message.reply_text("😕 Maaf, tidak ada lagu yang cocok ditemukan dengan durasi di bawah 10 menit.")
            return

        for video in results:
            caption = (
                f"<b>{html.escape(video['title'])}</b>\n\n"
                f"<b>Durasi:</b> {video['duration']}\n"
                f"<b>Channel:</b> {html.escape(video['channel']['name'])}"
            )
            keyboard = [[
                InlineKeyboardButton("🎬 Video", callback_data=f"dl_video:{video['link']}"),
                InlineKeyboardButton("🎵 Audio", callback_data=f"dl_audio:{video['link']}")
            ]]
            await update.message.reply_photo(
                photo=video['thumbnails'][0]['url'],
                caption=caption,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )
    except Exception as e:
        logger.error(f"Error during YouTube search: {e}")
        await update.message.reply_text("❌ Terjadi kesalahan saat melakukan pencarian YouTube.")

async def handle_quick_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Finds the top YouTube result and downloads it as audio."""
    query = update.message.text
    chat_id = update.message.chat_id
    status_message = await update.message.reply_text(f"🔎 Mencari lagu: \"{html.escape(query)}\"...", parse_mode='HTML')

    try:
        videos_search = VideosSearch(query, limit=1)
        results = videos_search.result()['result']

        if not results:
            await status_message.edit_text("😕 Maaf, tidak ada lagu yang cocok ditemukan.")
            return

        top_result = results[0]
        await status_message.delete() # Clean up "Searching..." message

        await update.message.reply_photo(
            photo=top_result['thumbnails'][0]['url'],
            caption=f"✅ Lagu ditemukan: <b>{html.escape(top_result['title'])}</b>",
            parse_mode='HTML'
        )

        download_status_msg = await update.message.reply_text("🚀 Mempersiapkan unduhan...")
        await download_and_send(chat_id, top_result['link'], 'audio', context, status_message=download_status_msg)

    except Exception as e:
        logger.error(f"Error during quick search: {e}")
        await status_message.edit_text("❌ Terjadi kesalahan saat melakukan pencarian.")


async def handle_pinterest_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Searches Pinterest for images by scraping and sends the top 5."""
    query = update.message.text
    status_message = await update.message.reply_text(f"🖼️ Mencari gambar di Pinterest untuk: \"{html.escape(query)}\"...")

    try:
        url = f"https://www.pinterest.com/search/pins/?q={requests.utils.quote(query)}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Regex to find high-quality image URLs in the HTML/JSON content
        image_urls = re.findall(r'"url":"(https://i\.pinimg\.com/originals/[^"]+\.jpg)"', response.text)

        unique_urls = list(dict.fromkeys(image_urls)) # Remove duplicates while preserving order

        if not unique_urls:
            await status_message.edit_text("😕 Maaf, tidak ada gambar yang ditemukan untuk kata kunci tersebut.")
            return

        await status_message.edit_text(f"✅ Ditemukan {len(unique_urls[:5])} gambar! Mengirim...")

        media_group = [InputMediaPhoto(media=url) for url in unique_urls[:5]]

        # Add a caption to the first image
        media_group[0].caption = f"Berikut adalah hasil pencarian untuk: \"{html.escape(query)}\""

        await context.bot.send_media_group(chat_id=update.effective_chat.id, media=media_group)
        await status_message.delete()

    except requests.RequestException as e:
        logger.error(f"Error fetching Pinterest page: {e}")
        await status_message.edit_text("❌ Gagal terhubung ke Pinterest. Silakan coba lagi nanti.")
    except Exception as e:
        logger.error(f"Error during Pinterest search: {e}")
        await status_message.edit_text("❌ Terjadi kesalahan saat mencari gambar di Pinterest.")


# --- Main Application Setup ---

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main() -> None:
    """Start the bot."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token or token == "YOUR_TOKEN_HERE":
        logger.error("FATAL: TELEGRAM_BOT_TOKEN is not set or is still the default value.")
        print("\n" + "="*50)
        print("🛑 Error: Bot token tidak ditemukan atau belum diatur.")
        print("Silakan edit file .env dan masukkan token bot Anda.")
        print("="*50 + "\n")
        return

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("caricepat", caricepat))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    application.add_error_handler(error_handler)

    logger.info("Bot is starting...")
    application.run_polling()

if __name__ == "__main__":
    main()