import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler, ConversationHandler
from yt_dlp import YoutubeDL
import requests
from dotenv import load_dotenv

# Muat variabel dari file .env
load_dotenv()

# Token Bot Telegram
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Konfigurasi logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# State untuk ConversationHandler
GET_QUERY = range(1)

# Fungsi untuk cari video
async def cari_video(update: Update, context: CallbackContext):
    query = " ".join(context.args)
    if query:
        await perform_search(update.message, query, context)
        return ConversationHandler.END
    await update.message.reply_text("Apa yang ingin Anda cari?")
    return GET_QUERY

async def get_search_query(update: Update, context: CallbackContext):
    await perform_search(update.message, update.message.text, context)
    return ConversationHandler.END

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

# Fungsi untuk cari jadwal azan
async def jadwal_azan(update: Update, context: CallbackContext):
    daerah = update.message.text
    api_url = f'https://api.example.com/jadwal-azan/{daerah}'
    response = requests.get(api_url)
    if response.status_code == 200:
        jadwal = response.json()
        await update.message.reply_text(f'Jadwal azan di {daerah}: {jadwal}')
    else:
        await update.message.reply_text('Gagal mencari jadwal azan!')

# Fungsi untuk cari foto di Pinterest
async def cari_foto(update: Update, context: CallbackContext):
    query = update.message.text
    api_url = f'https://api.example.com/pinterest/{query}'
    response = requests.get(api_url)
    if response.status_code == 200:
        foto = response.json()
        await update.message.reply_text(f'Foto di Pinterest: {foto}')
    else:
        await update.message.reply_text('Gagal mencari foto!')

# Fungsi untuk cari jadwal konser JKT48
async def jadwal_konser(update: Update, context: CallbackContext):
    api_url = 'https://api.example.com/jkt48'
    response = requests.get(api_url)
    if response.status_code == 200:
        jadwal = response.json()
        await update.message.reply_text(f'Jadwal konser JKT48: {jadwal}')
    else:
        await update.message.reply_text('Gagal mencari jadwal konser!')

# Fungsi untuk cari jadwal live streaming JKT48
async def jadwal_live_jkt48(update: Update, context: CallbackContext):
    api_url = 'https://api.example.com/jkt48/live'
    response = requests.get(api_url)
    if response.status_code == 200:
        jadwal = response.json()
        await update.message.reply_text(f'Jadwal live streaming JKT48: {jadwal}')
    else:
        await update.message.reply_text('Gagal mencari jadwal live streaming!')

def main():
    application = Application.builder().token(TOKEN).build()
    search_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("cari_video", cari_video)],
        states={GET_QUERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_search_query)]},
        fallbacks=[],
    )
    application.add_handler(search_conv_handler)
    application.add_handler(CallbackQueryHandler(unduh_video, pattern='^unduh_video\\|'))
    application.add_handler(CallbackQueryHandler(unduh_audio, pattern='^unduh_audio\\|'))
    application.add_handler(CommandHandler('jadwal_azan', jadwal_azan))
    application.add_handler(CommandHandler('cari_foto', cari_foto))
    application.add_handler(CommandHandler('jadwal_konser', jadwal_konser))
    application.add_handler(CommandHandler('jadwal_live_jkt48', jadwal_live_jkt48))
    application.run_polling()

if __name__ == '__main__':
    main()
