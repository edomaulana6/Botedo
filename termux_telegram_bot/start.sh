#!/bin/bash

# Pindah ke direktori tempat skrip ini berada, agar semua path file benar
cd "$(dirname "$0")"

# Cek apakah bot sudah berjalan
if [ -f bot.pid ]; then
    echo "Bot is already running. Please run stop.sh first if you want to restart."
    exit 1
fi

echo "Starting bot in the background..."

# Jalankan bot menggunakan nohup agar tetap berjalan setelah terminal ditutup
# Alihkan output standar dan error ke file log
# Jalankan di latar belakang dengan tanda &
nohup python bot.py > bot.log 2>&1 &

# Dapatkan Process ID (PID) dari proses yang baru saja dijalankan di latar belakang
BOT_PID=$!

# Simpan PID ke dalam file agar skrip stop.sh bisa menggunakannya
echo $BOT_PID > bot.pid

echo "Bot started with PID: $BOT_PID. Logs are being saved to bot.log."
echo "To stop the bot, run: ./stop.sh"