#!/bin/bash
echo "🚀 Memulai bot Telegram..."
# Menjalankan bot Python di latar belakang, log akan disimpan di bot.log
nohup python bot.py > bot.log 2>&1 &
# Menyimpan PID (Process ID) agar bisa dihentikan nanti
echo $! > bot.pid
echo "✅ Bot telah dimulai di latar belakang. Cek 'bot.log' untuk melihat log."
echo "   Untuk menghentikan bot, jalankan ./stop.sh"