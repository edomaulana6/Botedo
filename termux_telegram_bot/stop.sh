#!/bin/bash
echo "🔴 Menghentikan bot Telegram..."
# Membaca PID dari file bot.pid
if [ -f bot.pid ]; then
    PID=$(cat bot.pid)
    # Membunuh proses dengan PID yang tersimpan
    kill $PID
    rm bot.pid
    echo "✅ Bot dengan PID $PID telah dihentikan."
else
    echo "⚠️ Tidak dapat menemukan file 'bot.pid'. Mungkin bot tidak sedang berjalan?"
fi