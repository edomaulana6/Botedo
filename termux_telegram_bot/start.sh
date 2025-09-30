#!/bin/bash
echo "🚀 Memulai bot Telegram..."
# Menjalankan bot Python di latar belakang
nohup python bot.py > bot.log 2>&1 &
# Menyimpan PID (Process ID) dari proses yang baru saja dijalankan
echo $! > bot.pid
echo "✅ Bot telah dimulai di latar belakang. Cek 'bot.log' untuk melihat log."
echo "   Untuk menghentikan bot, jalankan ./stop.sh"