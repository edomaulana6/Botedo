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
from pterodactyl_manager import install_pterodactyl # Impor fungsi baru

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
        [InlineKeyboardButton("⚙️ Panel Pterodactyl", callback_data='menu_pterodactyl')],
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
    elif query.data == 'menu_pterodactyl':
        await pterodactyl_menu(update, context)
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
(
    GET_UNDUH_QUERY, GET_GAMBAR_QUERY, GET_GOOGLE_QUERY, GET_AZAN_QUERY, GET_AI_IMAGE,
    PTERO_GET_IP, PTERO_GET_USER, PTERO_GET_PASS,
    PTERO_GET_FQDN, PTERO_GET_EMAIL,
    PTERO_GET_ADMIN_USER, PTERO_GET_ADMIN_PASS,
    PTERO_GET_ADMIN_FNAME, PTERO_GET_ADMIN_LNAME,
    PTERO_GET_SSL,
    PTERO_ASK_WINGS, PTERO_GET_WINGS_CPU, PTERO_GET_WINGS_RAM,
    PTERO_CONFIRM
) = range(19)


async def pterodactyl_menu(update: Update, context: CallbackContext) -> None:
    """Menampilkan menu untuk fitur Pterodactyl."""
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🚀 Mulai Instalasi Panel", callback_data='ptero_start_install')],
        [InlineKeyboardButton("Kembali", callback_data='main_menu_back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = (
        "Anda berada di menu Panel Pterodactyl.\n\n"
        "Fitur ini akan memandu Anda untuk menginstal Panel Pterodactyl di VPS Anda secara otomatis."
    )
    await query.edit_message_text(text=text, reply_markup=reply_markup)

# --- Fungsi Pemula untuk ConversationHandler dari Menu ---
async def start_pterodactyl_install(update: Update, context: CallbackContext) -> int:
    """Memulai alur instalasi Pterodactyl dari menu dengan peringatan keamanan yang ditingkatkan."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "**⚠️ PERINGATAN KEAMANAN PENTING ⚠️**\n\n"
        "Anda akan memasukkan kredensial VPS (IP, user, pass). Informasi ini **tidak disimpan** oleh bot.\n\n"
        "Harap perhatikan risiko berikut:\n"
        "1. **Skrip Pihak Ketiga:** Bot ini menggunakan skrip dari `pterodactyl-installer.se` yang akan dijalankan dengan hak akses root di VPS Anda.\n"
        "2. **Koneksi SSH:** Verifikasi kunci host SSH dinonaktifkan (`AutoAddPolicy`), yang secara teoritis rentan terhadap serangan Man-in-the-Middle (MITM).\n\n"
        "Lanjutkan hanya jika Anda memahami dan menerima risiko ini. Kirim /batal kapan saja untuk berhenti.\n\n"
        "Silakan masukkan **Alamat IP** VPS Anda:",
        parse_mode='Markdown'
    )
    return PTERO_GET_IP

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
from google.api_core import exceptions
from PIL import Image

# --- Konfigurasi API Tambahan ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# --- Fitur AI Image Editor (dengan ConversationHandler) ---

async def _ai_command_entry_point(update: Update, context: CallbackContext, prompt: str, ask_message: str) -> int:
    """Titik masuk untuk semua perintah AI, menentukan alur percakapan."""
    if not GEMINI_API_KEY:
        await update.message.reply_text("Fitur AI tidak aktif. Kunci API Gemini belum diatur.")
        return ConversationHandler.END

    # Kasus 1: Perintah dikirim sebagai balasan ke sebuah gambar
    if update.message.reply_to_message and update.message.reply_to_message.photo:
        message_to_reply = update.message.reply_to_message
        status_msg = await message_to_reply.reply_text("🎨 Sedang memproses gambar dengan AI, ini mungkin memakan waktu...")
        try:
            photo_file = await message_to_reply.photo[-1].get_file()
            photo_bytes = await photo_file.download_as_bytearray()
            image_part = {"mime_type": "image/jpeg", "data": photo_bytes}
            model = genai.GenerativeModel('models/gemini-1.5-pro-latest')
            response = await model.generate_content_async([prompt, image_part], request_options={"timeout": 60})

            if not response.parts:
                raise ValueError("Respons AI tidak berisi data gambar.")

            await context.bot.send_photo(
                chat_id=message_to_reply.chat_id,
                photo=response.parts[0].inline_data.data,
                caption=f"Hasil edit untuk: \"{prompt}\"",
                reply_to_message_id=message_to_reply.message_id
            )
            await status_msg.delete()
        except ValueError as e:
            logging.error(f"ValueError di _ai_command_entry_point: {e}")
            await status_msg.edit_text("Gagal memproses: AI menolak gambar ini, kemungkinan karena alasan keamanan.")
        except exceptions.ResourceExhausted as e:
            logging.error(f"Quota error saat mengedit gambar dengan AI: {e}")
            await status_msg.edit_text("Maaf, kuota penggunaan AI gratis untuk hari ini telah habis. Silakan coba lagi besok.")
        except exceptions.DeadlineExceeded as e:
            logging.error(f"Timeout error saat mengedit gambar dengan AI: {e}")
            await status_msg.edit_text("Maaf, permintaan ke AI memakan waktu terlalu lama (timed out). Silakan coba lagi nanti.")
        except Exception as e:
            logging.error(f"Error di _ai_command_entry_point: {e}")
            await status_msg.edit_text("Terjadi kesalahan tak terduga saat memproses gambar Anda.")

        return ConversationHandler.END

    # Kasus 2: Perintah dikirim tanpa gambar, bot akan meminta gambar
    else:
        context.user_data['ai_prompt'] = prompt
        await update.message.reply_text(ask_message)
        return GET_AI_IMAGE

async def get_ai_image(update: Update, context: CallbackContext) -> int:
    """Menangani gambar yang dikirim setelah diminta oleh bot."""
    prompt = context.user_data.pop('ai_prompt', 'Gagal mendapatkan prompt.')
    status_msg = await update.message.reply_text("🎨 Sedang memproses gambar Anda dengan AI...")

    try:
        photo_file = await update.message.photo[-1].get_file()
        photo_bytes = await photo_file.download_as_bytearray()
        image_part = {"mime_type": "image/jpeg", "data": photo_bytes}
        model = genai.GenerativeModel('models/gemini-1.5-pro-latest')
        response = await model.generate_content_async([prompt, image_part], request_options={"timeout": 60})

        if not response.parts:
            raise ValueError("Respons AI tidak berisi data gambar.")

        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=response.parts[0].inline_data.data,
            caption=f"Hasil edit untuk: \"{prompt}\"",
            reply_to_message_id=update.message.message_id
        )
        await status_msg.delete()
    except ValueError as e:
        logging.error(f"ValueError di get_ai_image: {e}")
        await status_msg.edit_text("Gagal memproses: AI menolak gambar ini, kemungkinan karena alasan keamanan.")
    except exceptions.ResourceExhausted as e:
        logging.error(f"Quota error saat mengedit gambar dengan AI: {e}")
        await status_msg.edit_text("Maaf, kuota penggunaan AI gratis untuk hari ini telah habis. Silakan coba lagi besok.")
    except exceptions.DeadlineExceeded as e:
        logging.error(f"Timeout error saat mengedit gambar dengan AI: {e}")
        await status_msg.edit_text("Maaf, permintaan ke AI memakan waktu terlalu lama (timed out). Silakan coba lagi nanti.")
    except Exception as e:
        logging.error(f"Error di get_ai_image: {e}")
        await status_msg.edit_text("Terjadi kesalahan tak terduga saat memproses gambar Anda.")

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
        is_url = query.strip().startswith('http')
        search_query = query if is_url else f"ytsearch5:{query}"

        ydl_opts = {
            'format': 'best',
            'noplaylist': True,
            'quiet': True,
        }

        result = await asyncio.to_thread(YoutubeDL(ydl_opts).extract_info, search_query, download=False)
        await status_msg.delete()

        # Logika baru yang andal: Periksa apakah ini hasil pencarian atau URL tunggal
        if 'entries' in result:
            # Ini adalah hasil pencarian (misalnya dari ytsearch), gunakan daftarnya
            entries = result.get('entries', [])
        else:
            # Ini adalah URL tunggal (misalnya TikTok, Instagram), bungkus dalam daftar
            entries = [result]

        if not entries or entries[0] is None:
            await message.reply_text('Tidak ada hasil yang ditemukan atau URL tidak valid!')
            return

        await message.reply_text("Berikut adalah hasilnya:")
        for entry in entries:
            if not entry: continue # Lewati jika entri kosong

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
    except Exception as e:
        logging.error(f"Error saat memproses permintaan unduh: {e}")
        await status_msg.edit_text(f"Terjadi kesalahan saat memproses permintaan: {e}")

# --- Fungsi Unduh dengan Progress Hook ---

async def unduh_video(update: Update, context: CallbackContext):
    """Mengunduh video dengan progress bar."""
    query = update.callback_query
    video_url = query.data.split('|')[1]

    status_msg = await query.message.reply_text("⏳ Mengunduh video...")

    last_reported_percent = -1
    loop = asyncio.get_running_loop()

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
                    loop.call_soon_threadsafe(asyncio.create_task, status_msg.edit_text(f"⏳ Mengunduh video... {percent}%"))
        elif d['status'] == 'finished':
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
    loop = asyncio.get_running_loop()

    def progress_hook(d):
        nonlocal last_reported_percent
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
            if total_bytes:
                downloaded_bytes = d.get('downloaded_bytes')
                percent = int((downloaded_bytes / total_bytes) * 100)
                if percent // 10 > last_reported_percent // 10:
                    last_reported_percent = percent
                    loop.call_soon_threadsafe(asyncio.create_task, status_msg.edit_text(f"⏳ Mengunduh audio... {percent}%"))
        elif d['status'] == 'finished':
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

# --- Pterodactyl Installation Conversation ---

async def ptero_get_ip(update: Update, context: CallbackContext) -> int:
    """Menyimpan IP VPS dan meminta username."""
    context.user_data['ptero_ip'] = update.message.text
    await update.message.reply_text("IP berhasil disimpan. Sekarang, masukkan **username** VPS Anda (biasanya 'root'):", parse_mode='Markdown')
    return PTERO_GET_USER

async def ptero_get_user(update: Update, context: CallbackContext) -> int:
    """Menyimpan username dan meminta password."""
    context.user_data['ptero_user'] = update.message.text
    await update.message.reply_text("Username berhasil disimpan. Sekarang, masukkan **password** VPS Anda:", parse_mode='Markdown')
    return PTERO_GET_PASS

async def ptero_get_pass(update: Update, context: CallbackContext) -> int:
    """Menyimpan password, menghapus pesan, dan meminta FQDN."""
    context.user_data['ptero_pass'] = update.message.text

    # Hapus pesan yang berisi password
    await update.message.delete()

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Password VPS berhasil disimpan dan pesan asli telah dihapus demi keamanan.\n\n"
             "Sekarang, masukkan **Domain (FQDN)** yang akan Anda gunakan untuk panel (contoh: `panel.domain.com`):",
        parse_mode='Markdown'
    )
    return PTERO_GET_FQDN

async def ptero_get_fqdn(update: Update, context: CallbackContext) -> int:
    """Menyimpan FQDN dan meminta email."""
    context.user_data['ptero_fqdn'] = update.message.text
    await update.message.reply_text("Domain berhasil disimpan. Sekarang, masukkan **Email** Anda untuk admin dan sertifikat SSL:", parse_mode='Markdown')
    return PTERO_GET_EMAIL

async def ptero_get_email(update: Update, context: CallbackContext) -> int:
    """Menyimpan email dan meminta username admin."""
    context.user_data['ptero_email'] = update.message.text
    await update.message.reply_text("Email berhasil disimpan. Masukkan **Username** untuk akun admin panel:", parse_mode='Markdown')
    return PTERO_GET_ADMIN_USER

async def ptero_get_admin_user(update: Update, context: CallbackContext) -> int:
    """Menyimpan username admin dan meminta password admin."""
    context.user_data['ptero_admin_user'] = update.message.text
    await update.message.reply_text("Username admin berhasil disimpan. Masukkan **Password** untuk akun admin:", parse_mode='Markdown')
    return PTERO_GET_ADMIN_PASS

async def ptero_get_admin_pass(update: Update, context: CallbackContext) -> int:
    """Menyimpan password admin, menghapus pesan, dan meminta nama depan."""
    context.user_data['ptero_admin_pass'] = update.message.text

    # Hapus pesan yang berisi password
    await update.message.delete()

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Password admin berhasil disimpan dan pesan asli telah dihapus.\n\n"
             "Masukkan **Nama Depan** (First Name) Anda:",
        parse_mode='Markdown'
    )
    return PTERO_GET_ADMIN_FNAME

async def ptero_get_admin_fname(update: Update, context: CallbackContext) -> int:
    """Menyimpan nama depan dan meminta nama belakang."""
    context.user_data['ptero_admin_fname'] = update.message.text
    await update.message.reply_text("Nama depan berhasil disimpan. Masukkan **Nama Belakang** (Last Name) Anda:", parse_mode='Markdown')
    return PTERO_GET_ADMIN_LNAME

async def ptero_get_admin_lname(update: Update, context: CallbackContext) -> int:
    """Menyimpan nama belakang dan meminta konfigurasi SSL."""
    context.user_data['ptero_admin_lname'] = update.message.text

    keyboard = [
        [InlineKeyboardButton("Ya, gunakan Let's Encrypt (Disarankan)", callback_data='ptero_ssl_yes')],
        [InlineKeyboardButton("Tidak, saya akan atur manual nanti", callback_data='ptero_ssl_no')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Detail admin berhasil disimpan.\n\n"
        "Apakah Anda ingin mencoba mengkonfigurasi **SSL (HTTPS) secara otomatis** menggunakan Let's Encrypt?",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    return PTERO_GET_SSL

async def ptero_get_ssl(update: Update, context: CallbackContext) -> int:
    """Menyimpan pilihan SSL dan bertanya tentang instalasi Wings."""
    query = update.callback_query
    await query.answer()

    context.user_data['ptero_ssl'] = True if query.data == 'ptero_ssl_yes' else False

    keyboard = [
        [InlineKeyboardButton("Ya, instal Wings di server ini", callback_data='ptero_wings_yes')],
        [InlineKeyboardButton("Tidak, hanya instal Panel", callback_data='ptero_wings_no')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text="Konfigurasi SSL disimpan.\n\n"
             "Apakah Anda juga ingin menginstal **Wings** (daemon server game) di mesin yang sama? "
             "Ini diperlukan untuk menjalankan server game di VPS ini.",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    return PTERO_ASK_WINGS


async def ptero_ask_wings(update: Update, context: CallbackContext) -> int:
    """Menangani pilihan instalasi Wings. Jika ya, minta batas CPU."""
    query = update.callback_query
    await query.answer()

    if query.data == 'ptero_wings_yes':
        context.user_data['install_wings'] = True
        await query.edit_message_text(
            text="Baik, kita akan instal Wings.\n\n"
                 "Masukkan **batas CPU** untuk server game (dalam %, contoh: `200` untuk 2 core):",
            parse_mode='Markdown'
        )
        return PTERO_GET_WINGS_CPU
    else:
        context.user_data['install_wings'] = False
        # Jika tidak install wings, langsung ke ringkasan
        return await ptero_show_summary_and_confirm(update, context, is_callback=True)

async def ptero_get_wings_cpu(update: Update, context: CallbackContext) -> int:
    """Menyimpan batas CPU dan meminta batas RAM."""
    context.user_data['wings_cpu'] = update.message.text
    await update.message.reply_text(
        "Batas CPU disimpan.\n\n"
        "Masukkan **batas RAM** untuk server game (dalam MB, contoh: `4096` untuk 4GB):",
        parse_mode='Markdown'
    )
    return PTERO_GET_WINGS_RAM

async def ptero_get_wings_ram(update: Update, context: CallbackContext) -> int:
    """Menyimpan batas RAM dan menampilkan ringkasan."""
    context.user_data['wings_ram'] = update.message.text
    return await ptero_show_summary_and_confirm(update, context, is_callback=False)

async def ptero_show_summary_and_confirm(update: Update, context: CallbackContext, is_callback: bool) -> int:
    """Menampilkan ringkasan akhir dari semua data yang dikumpulkan dan meminta konfirmasi."""
    details = {
        "IP VPS": context.user_data.get('ptero_ip'),
        "Username VPS": context.user_data.get('ptero_user'),
        "Domain Panel": context.user_data.get('ptero_fqdn'),
        "Email Admin": context.user_data.get('ptero_email'),
        "Username Admin": context.user_data.get('ptero_admin_user'),
        "SSL Otomatis": "Ya" if context.user_data.get('ptero_ssl') else "Tidak",
        "Instal Wings": "Ya" if context.user_data.get('install_wings') else "Tidak",
    }
    if context.user_data.get('install_wings'):
        details["Batas CPU Wings"] = f"{context.user_data.get('wings_cpu')}%"
        details["Batas RAM Wings"] = f"{context.user_data.get('wings_ram')} MB"

    summary_text = "**Harap Konfirmasi Detail Instalasi:**\n\n"
    for key, value in details.items():
        summary_text += f"**{key}:** `{value}`\n"
    summary_text += "\nApakah Anda yakin ingin melanjutkan?"

    keyboard = [
        [InlineKeyboardButton("✅ Ya, Lanjutkan", callback_data='ptero_confirm_yes')],
        [InlineKeyboardButton("❌ Tidak, Batalkan", callback_data='ptero_confirm_no')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Pesan diedit jika dari callback, atau dikirim baru jika dari pesan biasa
    if is_callback:
        query = update.callback_query
        await query.edit_message_text(text=summary_text, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.message.reply_text(text=summary_text, reply_markup=reply_markup, parse_mode='Markdown')

    return PTERO_CONFIRM

async def ptero_confirm(update: Update, context: CallbackContext) -> int:
    """Menangani konfirmasi akhir dari pengguna dan memulai instalasi."""
    query = update.callback_query
    await query.answer()

    if query.data == 'ptero_confirm_yes':
        status_message = await query.edit_message_text(
            "⏳ **Menginisialisasi...**\n"
            "Mencoba terhubung ke VPS Anda. Mohon tunggu.",
            parse_mode='Markdown'
        )

        ptero_user_data = context.user_data.copy()

        asyncio.create_task(
            install_pterodactyl(ptero_user_data, context.bot, update.effective_chat.id, status_message)
        )

        context.user_data.clear()
        return ConversationHandler.END
    else:
        await query.edit_message_text("Instalasi dibatalkan.")
        context.user_data.clear()
        return ConversationHandler.END

async def ptero_cancel(update: Update, context: CallbackContext) -> int:
    """Membatalkan alur percakapan Pterodactyl."""
    await update.message.reply_text('Instalasi Pterodactyl dibatalkan.')
    context.user_data.clear()
    return ConversationHandler.END


def main():
    # Membuat direktori unduhan jika belum ada
    os.makedirs("downloads", exist_ok=True)

    # Atur timeout aplikasi lebih tinggi dari timeout API untuk mencegah pembatalan dini
    application = Application.builder().token(TOKEN).post_init(post_init).read_timeout(90).write_timeout(90).build()

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

    # Handler Pterodactyl
    ptero_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_pterodactyl_install, pattern='^ptero_start_install$')],
        states={
            PTERO_GET_IP: [MessageHandler(filters.TEXT & ~filters.COMMAND, ptero_get_ip)],
            PTERO_GET_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, ptero_get_user)],
            PTERO_GET_PASS: [MessageHandler(filters.TEXT & ~filters.COMMAND, ptero_get_pass)],
            PTERO_GET_FQDN: [MessageHandler(filters.TEXT & ~filters.COMMAND, ptero_get_fqdn)],
            PTERO_GET_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, ptero_get_email)],
            PTERO_GET_ADMIN_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, ptero_get_admin_user)],
            PTERO_GET_ADMIN_PASS: [MessageHandler(filters.TEXT & ~filters.COMMAND, ptero_get_admin_pass)],
            PTERO_GET_ADMIN_FNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ptero_get_admin_fname)],
            PTERO_GET_ADMIN_LNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ptero_get_admin_lname)],
            PTERO_GET_SSL: [CallbackQueryHandler(ptero_get_ssl, pattern='^ptero_ssl_')],
            PTERO_ASK_WINGS: [CallbackQueryHandler(ptero_ask_wings, pattern='^ptero_wings_')],
            PTERO_GET_WINGS_CPU: [MessageHandler(filters.TEXT & ~filters.COMMAND, ptero_get_wings_cpu)],
            PTERO_GET_WINGS_RAM: [MessageHandler(filters.TEXT & ~filters.COMMAND, ptero_get_wings_ram)],
            PTERO_CONFIRM: [CallbackQueryHandler(ptero_confirm, pattern='^ptero_confirm_')],
        },
        fallbacks=[CommandHandler("batal", ptero_cancel)],
    )
    application.add_handler(ptero_conv)

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