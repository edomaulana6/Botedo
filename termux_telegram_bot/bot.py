import os
import logging
import io
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler, ConversationHandler
from yt_dlp import YoutubeDL
import requests
from dotenv import load_dotenv
from duckduckgo_images_api import search as ddg_search
from googlesearch import search

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
        [InlineKeyboardButton("🎨 Editor Gambar AI", callback_data='menu_ai_editor')],
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
        [InlineKeyboardButton("🖼️ Mulai Cari Gambar", callback_data='start_gambar')],
        [InlineKeyboardButton("🔎 Mulai Pencarian Google", callback_data='start_google')],
        [InlineKeyboardButton("Kembali", callback_data='main_menu_back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "Anda berada di menu Pencarian. Pilih jenis pencarian yang Anda inginkan."
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
        await start_unduh_from_menu(update, context)
    elif query.data == 'start_gambar':
        await start_image_search_from_menu(update, context)
    elif query.data == 'start_google':
        await start_google_search_from_menu(update, context)
    elif query.data == 'start_azan':
        await start_azan_search_from_menu(update, context)
    elif query.data == 'menu_ai_editor':
        await ai_editor_menu(update, context)

async def ai_editor_menu(update: Update, context: CallbackContext) -> None:
    """Menampilkan menu untuk fitur Editor Gambar AI."""
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton("Kembali", callback_data='main_menu_back')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = (
        "Anda berada di menu Editor Gambar AI.\n\n"
        "Balas sebuah gambar dengan salah satu perintah berikut untuk mengeditnya:\n"
        "- `/toanime`\n- `/tofigure`\n- `/cinematic_lift`\n- `/ootd`\n"
        "- `/hitamkan`\n- `/putihkan`\n- `/night`\n- `/pretty`\n"
        "- `/ugly`\n- `/sedih`\n- `/senyum`\n- `/botakin`\n"
        "- `/edit_ai <prompt kustom>`"
    )
    await query.edit_message_text(text=text, reply_markup=reply_markup)

# States untuk ConversationHandlers
GET_UNDUH_QUERY, GET_GAMBAR_QUERY, GET_GOOGLE_QUERY, GET_AZAN_QUERY, GET_AI_IMAGE = range(5)

# --- Fungsi Pemula untuk ConversationHandler dari Menu ---
async def start_unduh_from_menu(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.edit_message_text("Silakan kirimkan URL atau judul untuk diunduh:")
    return GET_UNDUH_QUERY

async def start_image_search_from_menu(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.edit_message_text("Silakan masukkan kata kunci gambar yang ingin Anda cari:")
    return GET_GAMBAR_QUERY

async def start_google_search_from_menu(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.edit_message_text("Silakan masukkan kata kunci pencarian Google:")
    return GET_GOOGLE_QUERY

async def start_azan_search_from_menu(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.edit_message_text("Masukkan nama kota di Indonesia (contoh: Jakarta):")
    return GET_AZAN_QUERY

# --- Fungsi Perintah Utama & State Handlers ---

async def unduh(update: Update, context: CallbackContext) -> int:
    if context.args:
        query = " ".join(context.args)
        await process_download_request(update.message, query, context)
        return ConversationHandler.END
    else:
        await update.message.reply_text("Silakan masukkan URL atau judul untuk diunduh:")
        return GET_UNDUH_QUERY

async def get_unduh_query(update: Update, context: CallbackContext) -> int:
    await process_download_request(update.message, update.message.text, context)
    return ConversationHandler.END

async def cari_gambar(update: Update, context: CallbackContext) -> int:
    if context.args:
        query = " ".join(context.args)
        await perform_gambar_search(update.message, query, context)
        return ConversationHandler.END
    else:
        await update.message.reply_text("Silakan masukkan kata kunci gambar yang ingin Anda cari:")
        return GET_GAMBAR_QUERY

async def get_gambar_query(update: Update, context: CallbackContext) -> int:
    await perform_gambar_search(update.message, update.message.text, context)
    return ConversationHandler.END

async def google_search_command(update: Update, context: CallbackContext) -> int:
    if context.args:
        query = " ".join(context.args)
        await perform_google_search(update.message, query)
        return ConversationHandler.END
    else:
        await update.message.reply_text("Silakan masukkan kata kunci pencarian Google:")
        return GET_GOOGLE_QUERY

async def get_google_query(update: Update, context: CallbackContext) -> int:
    await perform_google_search(update.message, update.message.text)
    return ConversationHandler.END

async def jadwal_azan(update: Update, context: CallbackContext) -> int:
    if context.args:
        city = " ".join(context.args)
        await perform_azan_search(update.message, city)
        return ConversationHandler.END
    else:
        await update.message.reply_text("Masukkan nama kota di Indonesia (contoh: Jakarta):")
        return GET_AZAN_QUERY

async def get_azan_query(update: Update, context: CallbackContext) -> int:
    await perform_azan_search(update.message, update.message.text)
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

import google.generativeai as genai
from PIL import Image

# --- Konfigurasi API Tambahan ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# --- Fitur AI Image Editor (dengan ConversationHandler) ---

async def _process_ai_edit(message, photo_file, prompt: str, context: CallbackContext):
    """Fungsi inti yang stabil untuk memproses gambar dengan AI."""
    status_msg = await message.reply_text("🎨 Sedang memproses gambar dengan AI, ini mungkin memakan waktu...")
    try:
        photo_bytes = await photo_file.download_as_bytearray()
        img = await asyncio.to_thread(Image.open, io.BytesIO(photo_bytes))

        model = genai.GenerativeModel('gemini-2.5-flash-image')
        response = await asyncio.to_thread(model.generate_content, [prompt, img])

        image_data = response.parts[0].inline_data.data

        await context.bot.send_photo(
            chat_id=message.chat_id,
            photo=image_data,
            caption=f"Berikut adalah hasil edit dengan prompt: \"{prompt}\""
        )
        await status_msg.delete()
    except Exception as e:
        logging.error(f"Error saat mengedit gambar dengan AI: {e}")
        await status_msg.edit_text(f"Terjadi kesalahan saat memproses gambar dengan AI: {e}")

async def _ai_command_entry_point(update: Update, context: CallbackContext, prompt: str, ask_message: str) -> int:
    """Titik masuk untuk semua perintah AI, menentukan alur percakapan."""
    if not GEMINI_API_KEY:
        await update.message.reply_text("Fitur AI tidak aktif. Kunci API Gemini belum diatur.")
        return ConversationHandler.END

    if update.message.reply_to_message and update.message.reply_to_message.photo:
        photo_file = await update.message.reply_to_message.photo[-1].get_file()
        await _process_ai_edit(update.message.reply_to_message, photo_file, prompt, context)
        return ConversationHandler.END
    else:
        context.user_data['ai_prompt'] = prompt
        await update.message.reply_text(ask_message)
        return GET_AI_IMAGE

async def get_ai_image(update: Update, context: CallbackContext) -> int:
    """Menangani gambar yang dikirim setelah diminta oleh bot."""
    prompt = context.user_data.pop('ai_prompt', 'Tidak ada prompt yang diberikan.')
    photo_file = await update.message.photo[-1].get_file()
    await _process_ai_edit(update.message, photo_file, prompt, context)
    return ConversationHandler.END

async def cancel_ai(update: Update, context: CallbackContext) -> int:
    """Membatalkan alur percakapan AI."""
    await update.message.reply_text('Aksi edit gambar dibatalkan.')
    return ConversationHandler.END

# --- Perintah Preset untuk AI ---
async def toanime_command(update: Update, context: CallbackContext) -> int:
    return await _ai_command_entry_point(update, context, "Ubah gambar ini menjadi gaya anime.", "Baik, sekarang kirim gambar yang ingin diubah menjadi anime.")

async def tofigure_command(update: Update, context: CallbackContext) -> int:
    return await _ai_command_entry_point(update, context, "Ubah orang di gambar ini menjadi action figure yang realistis.", "Baik, sekarang kirim gambar yang ingin diubah menjadi action figure.")

async def cinematic_lift_command(update: Update, context: CallbackContext) -> int:
    return await _ai_command_entry_point(update, context, "Berikan efek sinematik dramatis pada gambar ini.", "Baik, sekarang kirim gambar untuk diberi efek sinematik.")

async def ootd_command(update: Update, context: CallbackContext) -> int:
    return await _ai_command_entry_point(update, context, "Berikan gaya OOTD (Outfit of The Day) yang modis pada orang di gambar ini.", "Baik, sekarang kirim gambar yang ingin diberi gaya OOTD.")

async def hitamkan_command(update: Update, context: CallbackContext) -> int:
    return await _ai_command_entry_point(update, context, "Ubah warna kulit orang di gambar ini menjadi lebih gelap.", "Baik, sekarang kirim gambar yang warna kulitnya ingin digelapkan.")

async def putihkan_command(update: Update, context: CallbackContext) -> int:
    return await _ai_command_entry_point(update, context, "Ubah warna kulit orang di gambar ini menjadi lebih cerah.", "Baik, sekarang kirim gambar yang warna kulitnya ingin dicerahkan.")

async def night_command(update: Update, context: CallbackContext) -> int:
    return await _ai_command_entry_point(update, context, "Ubah suasana gambar ini menjadi malam hari.", "Baik, sekarang kirim gambar yang ingin diubah suasananya menjadi malam.")

async def pretty_command(update: Update, context: CallbackContext) -> int:
    return await _ai_command_entry_point(update, context, "Edit wajah orang di gambar ini agar terlihat lebih cantik atau tampan.", "Baik, sekarang kirim gambar yang ingin dipercantik.")

async def ugly_command(update: Update, context: CallbackContext) -> int:
    return await _ai_command_entry_point(update, context, "Edit wajah orang di gambar ini menjadi sangat jelek dan lucu.", "Baik, sekarang kirim gambar yang ingin dibuat jelek.")

async def sedih_command(update: Update, context: CallbackContext) -> int:
    return await _ai_command_entry_point(update, context, "Ubah ekspresi wajah orang di gambar ini menjadi sedih.", "Baik, sekarang kirim gambar yang ekspresinya ingin diubah menjadi sedih.")

async def senyum_command(update: Update, context: CallbackContext) -> int:
    return await _ai_command_entry_point(update, context, "Ubah ekspresi wajah orang di gambar ini menjadi tersenyum.", "Baik, sekarang kirim gambar yang ekspresinya ingin diubah menjadi senyum.")

async def botakin_command(update: Update, context: CallbackContext) -> int:
    return await _ai_command_entry_point(update, context, "Hilangkan semua rambut dari kepala orang di gambar ini (botakin).", "Baik, sekarang kirim gambar yang ingin dibotakin.")

async def edit_ai_command(update: Update, context: CallbackContext) -> int:
    prompt = " ".join(context.args)
    if not prompt:
        await update.message.reply_text("Anda harus memberikan instruksi. Contoh: /edit_ai ubah latar belakang menjadi luar angkasa.")
        return ConversationHandler.END
    return await _ai_command_entry_point(update, context, prompt, f"Baik, prompt Anda adalah \"{prompt}\". Sekarang, kirimkan gambar yang ingin diedit.")


# --- Fitur Google Search ---

def perform_google_search_sync(query: str):
    """Fungsi sinkron untuk melakukan pencarian Google."""
    results = search(query, num_results=5)
    return results

async def google_search_command(update: Update, context: CallbackContext):
    """Mencari di Google berdasarkan query."""
    if context.args:
        query = " ".join(context.args)
        await perform_google_search(update.message, query)
    else:
        context.user_data['next_action'] = 'google_search'
        await update.message.reply_text("Silakan masukkan kata kunci pencarian Google:")

async def perform_google_search(message, query: str):
    status_msg = await message.reply_text(f"🔎 Mencari di Google untuk `{query}`...", parse_mode='Markdown')

    try:
        search_results = await asyncio.to_thread(perform_google_search_sync, query)

        if not search_results:
            await status_msg.edit_text("Tidak ada hasil yang ditemukan.")
            return

        response_text = f"Berikut adalah 5 hasil teratas untuk '{query}':\n\n"
        # Menggunakan enumerate(list(...)) karena objek search_results adalah generator
        for i, result in enumerate(list(search_results), 1):
            response_text += f"{i}. {result}\n" # URL adalah hasilnya

        await status_msg.edit_text(response_text, disable_web_page_preview=True)
    except Exception as e:
        logging.error(f"Error saat melakukan pencarian Google: {e}")
        await status_msg.edit_text("Terjadi kesalahan saat melakukan pencarian.")

async def start_google_search_from_menu(update: Update, context: CallbackContext):
    """Memulai alur pencarian Google dari menu."""
    query = update.callback_query
    context.user_data['next_action'] = 'google_search'
    await query.edit_message_text("Silakan masukkan kata kunci pencarian Google:")

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

async def process_download_request(message, query: str, context: CallbackContext):
    status_msg = await message.reply_text(f"🔎 Memproses `{query}`...", parse_mode='Markdown')
    try:
        # Tentukan apakah query adalah URL atau kata kunci pencarian
        is_url = query.strip().startswith('http')
        search_query = query if is_url else f"ytsearch5:{query}"

        ydl_opts = {
            'format': 'best',
            'noplaylist': True,
            'quiet': True,
        }

        with YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(search_query, download=False)
            await status_msg.delete()

            # Jika input adalah URL, result mungkin tidak memiliki 'entries'
            # jadi kita bungkus dalam list agar bisa di-loop
            entries = result.get('entries', [result] if 'id' in result else [])

            if entries:
                await message.reply_text("Berikut adalah hasilnya:")
                for entry in entries:
                    title = entry.get('title', 'N/A')
                    video_url = entry.get('webpage_url', entry.get('original_url', ''))
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
                await message.reply_text('Tidak ada hasil yang ditemukan atau URL tidak valid!')
    except Exception as e:
        logging.error(f"Error saat mencari: {e}")
        await status_msg.edit_text("Terjadi kesalahan saat melakukan pencarian.")

# --- Fungsi Unduh dengan Progress Hook ---

async def unduh_video(update: Update, context: CallbackContext):
    """Mengunduh video dengan progress bar."""
    query = update.callback_query
    video_url = query.data.split('|')[1]

    status_msg = await query.message.reply_text("⏳ Mengunduh video...")

    last_reported_percent = -1

    def progress_hook(d):
        nonlocal last_reported_percent
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
            if total_bytes:
                downloaded_bytes = d.get('downloaded_bytes')
                percent = int((downloaded_bytes / total_bytes) * 100)

                # Hanya edit pesan setiap kelipatan 10% untuk menghindari spam
                if percent // 10 > last_reported_percent // 10:
                    last_reported_percent = percent
                    loop = asyncio.get_running_loop()
                    loop.call_soon_threadsafe(asyncio.create_task, status_msg.edit_text(f"⏳ Mengunduh video... {percent}%"))
        elif d['status'] == 'finished':
             loop = asyncio.get_running_loop()
             loop.call_soon_threadsafe(asyncio.create_task, status_msg.edit_text("✅ Video selesai diunduh, sedang mengirim..."))

    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'noplaylist': True,
        'progress_hooks': [progress_hook],
        'nocheckcertificate': True,
    }
    if os.path.exists("cookies.txt"):
        ydl_opts['cookiefile'] = 'cookies.txt'

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info_dict)
            await context.bot.send_video(
                chat_id=query.message.chat_id,
                video=open(filename, 'rb'),
                caption=info_dict.get('title')
            )
            await status_msg.delete()
            os.remove(filename)
    except Exception as e:
        error_message = str(e)
        logging.error(f"Error saat mengunduh video: {error_message}")
        await status_msg.edit_text(f"Gagal mengunduh video.\n\nError: `{error_message}`", parse_mode='Markdown')

async def unduh_audio(update: Update, context: CallbackContext):
    """Mengunduh audio dengan progress bar."""
    query = update.callback_query
    video_url = query.data.split('|')[1]

    status_msg = await query.message.reply_text("⏳ Mengunduh audio...")

    last_reported_percent = -1

    def progress_hook(d):
        nonlocal last_reported_percent
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
            if total_bytes:
                downloaded_bytes = d.get('downloaded_bytes')
                percent = int((downloaded_bytes / total_bytes) * 100)
                if percent // 10 > last_reported_percent // 10:
                    last_reported_percent = percent
                    loop = asyncio.get_running_loop()
                    loop.call_soon_threadsafe(asyncio.create_task, status_msg.edit_text(f"⏳ Mengunduh audio... {percent}%"))
        elif d['status'] == 'finished':
            loop = asyncio.get_running_loop()
            loop.call_soon_threadsafe(asyncio.create_task, status_msg.edit_text("✅ Audio selesai diunduh, sedang memproses & mengirim..."))

    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'noplaylist': True,
        'format': 'bestaudio/best',
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}],
        'progress_hooks': [progress_hook],
        'nocheckcertificate': True,
    }

    if os.path.exists("cookies.txt"):
        ydl_opts['cookiefile'] = 'cookies.txt'

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info_dict)
            mp3_filename = os.path.splitext(filename)[0] + '.mp3'
            await context.bot.send_audio(
                chat_id=query.message.chat_id,
                audio=open(mp3_filename, 'rb'),
                caption=info_dict.get('title')
            )
            await status_msg.delete()
            os.remove(mp3_filename)
            if os.path.exists(filename):
                os.remove(filename)
    except Exception as e:
        error_message = str(e)
        logging.error(f"Error saat mengunduh audio: {error_message}")
        await status_msg.edit_text(f"Gagal mengunduh audio.\n\nError: `{error_message}`", parse_mode='Markdown')

def main():
    # Membuat direktori unduhan jika belum ada
    os.makedirs("downloads", exist_ok=True)

    application = Application.builder().token(TOKEN).post_init(post_init).build()

    # Conversation Handlers
    unduh_conv = ConversationHandler(
        entry_points=[CommandHandler("unduh", unduh), CallbackQueryHandler(start_unduh_from_menu, pattern='^start_video$')],
        states={GET_UNDUH_QUERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_unduh_query)]},
        fallbacks=[CommandHandler("start", start)],
    )
    gambar_conv = ConversationHandler(
        entry_points=[CommandHandler("cari_gambar", cari_gambar), CallbackQueryHandler(start_image_search_from_menu, pattern='^start_gambar$')],
        states={GET_GAMBAR_QUERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_gambar_query)]},
        fallbacks=[CommandHandler("start", start)],
    )
    google_conv = ConversationHandler(
        entry_points=[CommandHandler("google", google_search_command), CallbackQueryHandler(start_google_search_from_menu, pattern='^start_google$')],
        states={GET_GOOGLE_QUERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_google_query)]},
        fallbacks=[CommandHandler("start", start)],
    )
    azan_conv = ConversationHandler(
        entry_points=[CommandHandler("jadwal_azan", jadwal_azan), CallbackQueryHandler(start_azan_search_from_menu, pattern='^start_azan$')],
        states={GET_AZAN_QUERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_azan_query)]},
        fallbacks=[CommandHandler("start", start)],
    )

    # Tambahkan handler
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("menu", main_menu))

    application.add_handler(unduh_conv)
    application.add_handler(gambar_conv)
    application.add_handler(google_conv)
    application.add_handler(azan_conv)

    # AI Editor Conversation Handler
    ai_conv = ConversationHandler(
        entry_points=[
            CommandHandler("toanime", toanime_command),
            CommandHandler("tofigure", tofigure_command),
            CommandHandler("cinematic_lift", cinematic_lift_command),
            CommandHandler("ootd", ootd_command),
            CommandHandler("hitamkan", hitamkan_command),
            CommandHandler("putihkan", putihkan_command),
            CommandHandler("night", night_command),
            CommandHandler("pretty", pretty_command),
            CommandHandler("ugly", ugly_command),
            CommandHandler("sedih", sedih_command),
            CommandHandler("senyum", senyum_command),
            CommandHandler("botakin", botakin_command),
            CommandHandler("edit_ai", edit_ai_command),
        ],
        states={
            GET_AI_IMAGE: [MessageHandler(filters.PHOTO, get_ai_image)],
        },
        fallbacks=[CommandHandler("batal", cancel_ai)],
    )
    application.add_handler(ai_conv)

    # Handler unduhan harus didaftarkan SEBELUM handler tombol umum
    application.add_handler(CallbackQueryHandler(unduh_video, pattern='^unduh_video\\|'))
    application.add_handler(CallbackQueryHandler(unduh_audio, pattern='^unduh_audio\\|'))
    application.add_handler(CallbackQueryHandler(button_callback_handler))

    # Jalankan bot
    application.run_polling()

async def post_init(application: Application) -> None:
    """Mengatur daftar perintah bot setelah inisialisasi."""
    await application.bot.set_my_commands([
        ('menu', 'Buka menu utama'),
        ('unduh', 'Unduh video/audio dari URL/pencarian'),
        ('cari_gambar', 'Cari gambar di internet'),
        ('google', 'Cari informasi di Google'),
        ('jadwal_azan', 'Lihat jadwal salat'),
        ('edit_ai', 'Edit gambar dengan prompt kustom (balas ke gambar)'),
        ('toanime', 'Ubah gambar jadi anime (balas ke gambar)'),
        ('tofigure', 'Ubah gambar jadi action figure (balas ke gambar)'),
        ('cinematic_lift', 'Efek sinematik di lift (balas ke gambar)'),
        ('ootd', 'Gaya OOTD (balas ke gambar)'),
        ('pretty', 'Buat wajah lebih menarik (balas ke gambar)'),
        ('ugly', 'Buat wajah jadi jelek (balas ke gambar)'),
        ('senyum', 'Buat wajah tersenyum (balas ke gambar)'),
        ('sedih', 'Buat wajah jadi sedih (balas ke gambar)'),
        ('botakin', 'Hilangkan rambut (balas ke gambar)'),
        ('night', 'Ubah suasana jadi malam (balas ke gambar)'),
        ('hitamkan', 'Gelapkan warna kulit (balas ke gambar)'),
        ('putihkan', 'Cerahkan warna kulit (balas ke gambar)'),
        ('help', 'Tampilkan bantuan'),
        ('start', 'Mulai ulang bot'),
    ])

if __name__ == '__main__':
    main()