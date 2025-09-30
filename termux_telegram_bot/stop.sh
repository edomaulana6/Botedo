#!/bin/bash

# Pindah ke direktori tempat skrip ini berada
cd "$(dirname "$0")"

# Cek apakah file PID ada
if [ ! -f bot.pid ]; then
    echo "Bot is not running (or bot.pid file is missing)."
    exit 1
fi

# Baca PID dari file
BOT_PID=$(cat bot.pid)

echo "Stopping bot with PID: $BOT_PID..."

# Gunakan kill untuk menghentikan proses
kill $BOT_PID

# Hapus file PID setelah proses dihentikan
rm bot.pid

echo "Bot stopped successfully."