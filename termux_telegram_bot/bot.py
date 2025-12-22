import os
import logging
import io
import asyncio
import requests
from dotenv import load_dotenv

# Telegram Library
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    filters, CallbackContext, CallbackQueryHandler, ConversationHandler
)

# Tools
from yt_dlp import YoutubeDL
from duckduckgo_images_api import search as ddg_search
import google.generativeai as genai

# Muat variabel environment
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Konfigurasi logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

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

# --- FUNGSI NAVIGASI & MENU ---

async def start(update: Update, context: CallbackContext):
    user = update.effective_user
    await update.message.reply_html(
        f"👋 Halo {user.mention_html()}!\n\n"
        "Saya adalah bot asisten serbaguna. Gunakan /menu untuk melihat fitur."
    )

async def main_menu(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("📥 Downloader", callback_data='menu_downloader')],
        [InlineKeyboardButton("🖼️ Cari Gambar", callback_data='start_gambar')],
        [InlineKeyboardButton("🎨 AI Editor", callback_data='menu_ai_editor')],
        [InlineKeyboardButton("🕌 Islami", callback_data='menu_islamic')],
        [InlineKeyboardButton("⚙️ Pterodactyl", callback_data='menu_pterodactyl')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "💡 **Main Menu**\nSilakan pilih kategori fitur di bawah ini:"
    
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')

# --- FITUR CARI GAMBAR (FIXED) ---

async def start_image_search_from_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🖼️ Masukkan kata kunci gambar yang ingin Anda cari:")
    return GET_GAMBAR_QUERY

async def perform_gambar_search(update: Update, context: CallbackContext):
    query = update.message.text
    status_msg = await update.message.reply_text(f"🔍 Mencari gambar untuk: `{query}`...", parse_mode='Markdown')
    
    try:
        # Mengambil 5 gambar dari DuckDuckGo
        results = await asyncio.to_thread(ddg_search, query, max_results=5)
        if results:
            media = [InputMediaPhoto(r['image']) for r in results]
            await update.message.reply_media_group(media)
            await status_msg.delete()
        else:
            await status_msg.edit_text("❌ Gambar tidak ditemukan.")
    except Exception as e:
        await status_msg.edit_text(f"❌ Terjadi kesalahan: {e}")
    return ConversationHandler.END

# --- FITUR DOWNLOADER (WITH PROGRESS BAR & BUTTONS) ---

async def start_unduh_from_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("📥 Kirimkan URL atau Judul Video untuk dicari:")
    return GET_UNDUH_QUERY

# ... (kode pencarian video di atasnya) ...

async def handle_downloads(update: Update, context: CallbackContext):
    # --- SEMUA ISI FUNGSI INI DIGANTI ---
    # Mulai dari sini sampai...
    # ... proses download & progress bar ...
    # ... sampai os.remove(path) ...

# --- DI SINI ADALAH BATASNYA ---
# --- FUNGSI PEMBANTU LAINNYA (ISLAMI & MENU) ---

async def islamic_menu(update: Update, context: CallbackContext):
    # ... (dan seterusnya) ...

# --- FUNGSI PEMBANTU LAINNYA (ISLAMI & MENU) ---

async def islamic_menu(update: Update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton("▶️ Jadwal Azan", callback_data='start_azan')],
                [InlineKeyboardButton("Kembali", callback_data='main_menu_back')]]
    await update.callback_query.edit_message_text("🕌 **Menu Islami**\nCek jadwal salat kota Anda.", 
                                                 reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def start_azan_search(update: Update, context: CallbackContext):
    await update.callback_query.edit_message_text("📍 Masukkan nama kota (contoh: Jakarta):")
    return GET_AZAN_QUERY

async def get_azan(update: Update, context: CallbackContext):
    city = update.message.text
    url = f"http://api.aladhan.com/v1/timingsByCity?city={city}&country=Indonesia&method=20"
    try:
        res = requests.get(url).json()
        t = res['data']['timings']
        msg = f"🕌 **Jadwal Salat: {city}**\n\nSubuh: {t['Fajr']}\nZuhur: {t['Dhuhr']}\nAsar: {t['Asr']}\nMaghrib: {t['Maghrib']}\nIsya: {t['Isha']}"
        await update.message.reply_text(msg, parse_mode='Markdown')
    except:
        await update.message.reply_text("❌ Kota tidak ditemukan.")
    return ConversationHandler.END

# --- MAIN RUNNER ---

def main():
    if not os.path.exists("downloads"): os.makedirs("downloads")
    app = Application.builder().token(TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", main_menu))

    # Downloader Conv
    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(start_unduh_from_menu, pattern='^menu_downloader$')],
        states={GET_UNDUH_QUERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_download_request)]},
        fallbacks=[]
    ))

    # Image Conv
    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(start_image_search_from_menu, pattern='^start_gambar$')],
        states={GET_GAMBAR_QUERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, perform_gambar_search)]},
        fallbacks=[]
    ))

    # Islamic Conv
    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(start_azan_search, pattern='^start_azan$')],
        states={GET_AZAN_QUERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_azan)]},
        fallbacks=[]
    ))

    # Tombol Download & Back
    app.add_handler(CallbackQueryHandler(handle_downloads, pattern='^dl_'))
    app.add_handler(CallbackQueryHandler(islamic_menu, pattern='^menu_islamic$'))
    app.add_handler(CallbackQueryHandler(main_menu, pattern='^main_menu_back$'))

def main():
    if not os.path.exists("downloads"): os.makedirs("downloads")
    app = Application.builder().token(TOKEN).build()

    # --- REGISTRASI COMMAND HANDLERS ---
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", main_menu))
    
    # Menambahkan shortcut agar perintah langsung bisa jalan
    
    # app.add_handler(CommandHandler("ai", start_ai_chat)) # Aktifkan jika fungsi AI sudah siap

    # --- REGISTRASI CONVERSATION HANDLERS ---
    # Downloader
    app.add_handler(ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_unduh_from_menu, pattern='^menu_downloader$'),
            CommandHandler("unduh", start_unduh_from_menu) # Shortcut command
        ],
        states={GET_UNDUH_QUERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_download_request)]},
        fallbacks=[],
        per_message=True
    ))

    # Image Search
    app.add_handler(ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_image_search_from_menu, pattern='^start_gambar$'),
            CommandHandler("gambar", start_image_search_from_menu) # Shortcut command
        ],
        states={GET_GAMBAR_QUERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, perform_gambar_search)]},
        fallbacks=[],
        per_message=True
    ))

    # Islamic Search
    app.add_handler(ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_azan_search, pattern='^start_azan$'),
            CommandHandler("azan", start_azan_search) # Shortcut command
        ],
        states={GET_AZAN_QUERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_azan)]},
        fallbacks=[],
        per_message=True
    ))

    # Callback untuk tombol umum
    app.add_handler(CallbackQueryHandler(handle_downloads, pattern='^dl_'))
    app.add_handler(CallbackQueryHandler(islamic_menu, pattern='^menu_islamic$'))
    app.add_handler(CallbackQueryHandler(main_menu, pattern='^main_menu_back$'))

    print("🚀 Bot is running with Shortcut Commands...")
    app.run_polling()

if __name__ == '__main__':
    main()
    
