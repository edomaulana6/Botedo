import logging
import os
import subprocess
import uuid
import json
import traceback
from pathlib import Path
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InputMediaPhoto
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import html
import requests
import re
import httpx

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Helper Functions ---

def format_seconds(seconds: int) -> str:
    """Converts seconds to HH:MM:SS or MM:SS format."""
    if seconds is None:
        return "N/A"
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    else:
        return f"{m:02d}:{s:02d}"

# --- Core Logic ---

async def download_and_send(chat_id: int, url: str, format_choice: str, context: ContextTypes.DEFAULT_TYPE, status_message=None):
    """Downloads a file and sends it, with conversational status updates."""
    edit_message = status_message.edit_text if status_message else context.bot.send_message

    try:
        await edit_message(text=f"Oke, sabar ya... Lagi proses download {format_choice}-nya nih... ⏳")

        download_dir = Path(f"./downloads/{uuid.uuid4()}")
        download_dir.mkdir(parents=True, exist_ok=True)

        if format_choice == 'audio':
            command = ['yt-dlp', '-f', 'bestaudio', '-x', '--audio-format', 'mp3', '--external-downloader', 'aria2c', '-o', f'{download_dir}/%(title)s.%(ext)s', '--ffmpeg-location', '/data/data/com.termux/files/usr/bin/ffmpeg', url]
        else:
            command = ['yt-dlp', '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', '--recode-video', 'mp4', '--external-downloader', 'aria2c', '-o', f'{download_dir}/%(title)s.%(ext)s', '--ffmpeg-location', '/data/data/com.termux/files/usr/bin/ffmpeg', url]

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
                "`pip install --upgrade \"https://github.com/yt-dlp/yt-dlp/archive/master.zip\"`\n"
                "3. Nyalakan lagi botnya.\n\n"
                "Kalau cara di atas gak berhasil, berarti link-nya mungkin emang gak didukung saat ini."
            )
            await edit_message(text=error_message, parse_mode='Markdown')
        else:
            error_message = (
                "Waduh, link yang kamu kasih sepertinya tidak bisa di-download. 🙁\n\n"
                "Ini bisa terjadi karena beberapa alasan:\n"
                "• Link-nya salah ketik atau tidak lengkap.\n"
                "• Video/kontennya bersifat pribadi (private).\n"
                "• Kontennya dibatasi untuk negara tertentu.\n"
                "• Situs web tersebut memang tidak didukung.\n\n"
                f"*Detail Teknis:*\n`{e.stderr[:150]}`"
            )
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
        await query.edit_message_reply_markup(reply_markup=None)
        status_message = await query.message.reply_text(f"Oke, aku siapin unduhan {format_choice}-nya ya...")
        await download_and_send(query.message.chat_id, url, format_choice, context, status_message=status_message)
    elif data.startswith("retry_search:"):
        search_query = data.split(":", 1)[1]
        await _perform_youtube_search(update, context, search_query, is_retry=True)
    elif data.startswith("retry_quick_search:"):
        search_query = data.split(":", 1)[1]
        await _perform_quick_search(update, context, search_query, is_retry=True)
    elif data == "cancel_search":
        await query.edit_message_text("Oke, pencarian dibatalkan. ✅")


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

# --- YouTube Search Core Functions ---

async def _perform_youtube_search(update, context, query, is_retry=False):
    """Core logic for performing a standard YouTube search."""
    if is_retry:
        status_msg = await update.callback_query.message.edit_text(f"Oke, aku coba lagi cari \"{html.escape(query)}\" dengan waktu lebih lama... 🔎")
    else:
        status_msg = await update.message.reply_text(f"Oke, aku cariin \"{html.escape(query)}\" di YouTube ya... 🔎")

    timeout = 180 if is_retry else 90
    process = None
    try:
        command = ['yt-dlp', '-4', '--user-agent', 'Mozilla/5.0', f"ytsearch5:{query}", '--dump-json']
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')

        found_results = False
        for line in iter(process.stdout.readline, ''):
            if not line and process.poll() is not None: break
            if not line: continue

            if not found_results:
                await status_msg.delete()
                found_results = True

            video = json.loads(line)
            if video.get('duration', 0) < 600:
                duration = format_seconds(video.get('duration'))
                caption = (f"<b>{html.escape(video.get('title', 'No Title'))}</b>\n\n"
                           f"🕒 Durasi: {duration}\n"
                           f"👤 Channel: {html.escape(video.get('channel', 'N/A'))}")
                keyboard = [[
                    InlineKeyboardButton("🎬 Video", callback_data=f"dl_video:{video.get('webpage_url')}"),
                    InlineKeyboardButton("🎵 Audio", callback_data=f"dl_audio:{video.get('webpage_url')}")
                ]]
                await update.effective_chat.send_photo(
                    photo=video.get('thumbnail'), caption=caption,
                    reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML'
                )

        process.wait(timeout=timeout)
        if process.returncode != 0:
            stderr = process.stderr.read()
            logger.error(f"yt-dlp search error for '{query}': {stderr}")
            if not found_results:
                await status_msg.edit_text(f"Waduh, ada error dari mesin pencari.\n\n*Detail:*\n`{stderr[:200]}`", parse_mode='Markdown')
            else:
                await update.effective_chat.send_message(f"Waduh, ada error dari mesin pencari.\n\n*Detail:*\n`{stderr[:200]}`", parse_mode='Markdown')
            return

        if not found_results:
            await status_msg.edit_text("Yah, lagu yang kamu cari gak ketemu. Coba pake kata kunci lain. 😕")
        else:
            await update.effective_chat.send_message("✅ Pencarian selesai!")

    except subprocess.TimeoutExpired:
        logger.error(f"YouTube search for '{query}' timed out.")
        if process: process.kill()

        if is_retry:
            await status_msg.edit_text("Waduh, udah ditunggu 3 menit tetep macet. Maaf, pencarian gagal. 😥")
        else:
            keyboard = [[
                InlineKeyboardButton("✅ Ya, tunggu lagi", callback_data=f"retry_search:{query}"),
                InlineKeyboardButton("❌ Tidak, batalkan", callback_data="cancel_search")
            ]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await status_msg.edit_text(
                "Waduh, pencarian ini macet lebih dari 90 detik. Kayaknya jaringan lagi lambat. 🐌\n\nMau aku coba tunggu lebih lama lagi (3 menit)?",
                reply_markup=reply_markup
            )
    except Exception as e:
        logger.error(f"Error in _perform_youtube_search: {e}")
        error_details = f"Waduh, ada error pas nyari di YouTube. Maaf ya. 😥\n\n*Pesan Error Detail:*\n`{str(e)}`"
        try:
            await status_msg.edit_text(error_details, parse_mode='Markdown')
        except:
             await update.effective_chat.send_message(error_details, parse_mode='Markdown')

async def _perform_quick_search(update, context, query, is_retry=False):
    """Core logic for performing a quick YouTube search."""
    chat_id = update.effective_chat.id
    if is_retry:
        status_msg = await update.callback_query.message.edit_text(f"Oke, aku coba lagi cari \"{html.escape(query)}\" dengan waktu lebih lama... 🚀")
    else:
        status_msg = await update.message.reply_text(f"Cari cepet buat \"{html.escape(query)}\"... 🚀")

    timeout = 180 if is_retry else 90
    try:
        command = ['yt-dlp', '-4', '--user-agent', 'Mozilla/5.0', f"ytsearch1:{query}", '--dump-json']
        process = subprocess.run(command, capture_output=True, text=True, check=True, timeout=timeout)

        top_result = json.loads(process.stdout)
        if not top_result:
            await status_msg.edit_text("Yah, gak ketemu lagunya. Coba judul lain. 😕")
            return

        await status_msg.delete()
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=top_result.get('thumbnail'),
            caption=f"Ketemu! Ini lagunya:\n<b>{html.escape(top_result.get('title', 'No Title'))}</b>",
            parse_mode='HTML'
        )

        download_status_msg = await context.bot.send_message(chat_id, "Siap-siap, aku unduh audionya...")
        await download_and_send(chat_id, top_result.get('webpage_url'), 'audio', context, status_message=download_status_msg)

    except subprocess.TimeoutExpired:
        logger.error(f"Quick search for '{query}' timed out.")
        if is_retry:
            await status_msg.edit_text("Waduh, udah ditunggu 3 menit tetep macet. Maaf, pencarian gagal. 😥")
        else:
            keyboard = [[
                InlineKeyboardButton("✅ Ya, tunggu lagi", callback_data=f"retry_quick_search:{query}"),
                InlineKeyboardButton("❌ Tidak, batalkan", callback_data="cancel_search")
            ]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await status_msg.edit_text(
                "Waduh, pencarian ini macet lebih dari 90 detik. Kayaknya jaringan lagi lambat. 🐌\n\nMau aku coba tunggu lebih lama lagi (3 menit)?",
                reply_markup=reply_markup
            )
    except subprocess.CalledProcessError as e:
        logger.error(f"yt-dlp quick search error for '{query}': {e.stderr}")
        await status_msg.edit_text(f"Waduh, ada error dari mesin pencari.\n\n*Detail:*\n`{e.stderr[:200]}`", parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error quick search with yt-dlp: {e}")
        error_details = f"Aduh, ada error pas lagi cari cepet. Maaf ya. 😥\n\n*Pesan Error Detail:*\n`{str(e)}`"
        await status_msg.edit_text(error_details, parse_mode='Markdown')

# --- Handlers that call the core functions ---

async def handle_youtube_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _perform_youtube_search(update, context, update.message.text)

async def handle_quick_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _perform_quick_search(update, context, update.message.text)

# --- Pinterest Search ---

async def handle_pinterest_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Scrapes Pinterest for images and sends top 5."""
    query = update.message.text
    status_msg = await update.message.reply_text(f"Sip, aku cariin gambar \"{html.escape(query)}\" di Pinterest... 🎨")

    try:
        url = f"https://www.pinterest.com/search/pins/?q={requests.utils.quote(query)}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Coba cari gambar kualitas terbaik (originals) dulu
        image_urls = re.findall(r'"url":"(https://i\.pinimg\.com/originals/[^"]+\.jpg)"', response.text)

        # Jika tidak ketemu, coba cari kualitas 736x
        if not image_urls:
            logger.info("Tidak ada gambar kualitas 'originals', mencoba '736x'.")
            image_urls = re.findall(r'"url":"(https://i\.pinimg\.com/736x/[^"]+\.jpg)"', response.text)

        # Jika masih tidak ketemu, coba kualitas 564x
        if not image_urls:
            logger.info("Tidak ada gambar kualitas '736x', mencoba '564x'.")
            image_urls = re.findall(r'"url":"(https://i\.pinimg\.com/564x/[^"]+\.jpg)"', response.text)

        unique_urls = list(dict.fromkeys(image_urls))

        if not unique_urls:
            await status_msg.edit_text("Hmm, gambarnya gak ketemu. Coba kata kunci yang lain. 😕")
            return

        await status_msg.edit_text(f"Dapet {len(unique_urls[:5])} gambar! Aku kirim ya...")
        media_group = [InputMediaPhoto(media=url) for url in unique_urls[:5]]
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
    """Catat Error dan kirim pesan yang lebih spesifik ke pengguna."""
    error = context.error
    logger.error("Exception while handling an update:", exc_info=error)

    error_message = "Waduh, sepertinya ada error serius di belakang layar. 😥"

    if isinstance(error, httpx.ReadTimeout):
        error_message = "Koneksi ke server Telegram putus di tengah jalan. Coba lagi nanti, ini biasanya masalah sementara. 🔌"
    elif isinstance(error, httpx.ConnectTimeout):
        error_message = "Gagal terhubung ke server Telegram. Cek koneksi internet kamu, atau mungkin Telegram lagi ada gangguan. 🛰️"
    else:
        # Untuk error lainnya, kirim traceback
        tb_list = traceback.format_exception(None, error, error.__traceback__)
        tb_string = "".join(tb_list)
        error_message = (
            "Waduh, sepertinya ada error serius di belakang layar. 😥\n\n"
            "Tolong teruskan pesan ini kepada developer agar bisa diperbaiki:\n\n"
            "```\n"
            f"Error: {error}\n\n"
            f"Traceback:\n{tb_string[:3000]}"
            "\n```"
        )

    # Kirim pesan ke pengguna
    if isinstance(update, Update) and update.effective_chat:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=error_message,
            parse_mode='Markdown'
        )

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

    # Naikkan batas waktu koneksi untuk membuatnya lebih sabar
    application = (
        Application.builder()
        .token(token)
        .connect_timeout(60)
        .read_timeout(60)
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("caricepat", caricepat))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    application.add_error_handler(error_handler)

    logger.info("Bot mulai jalan...")
    application.run_polling()

if __name__ == "__main__":
    main()