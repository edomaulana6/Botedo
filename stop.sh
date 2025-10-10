#!/bin/bash
echo "🔴 Menghentikan semua proses bot..."

# Menghentikan skrip penjaga (run_stable.sh)
pkill -f "run_stable.sh"
if [ $? -eq 0 ]; then
    echo "✅ Skrip penjaga (run_stable.sh) telah dihentikan."
else
    echo "⚠️ Skrip penjaga (run_stable.sh) tidak ditemukan berjalan."
fi

# Menghentikan proses bot Python (bot.py)
pkill -f "python bot.py"
if [ $? -eq 0 ]; then
    echo "✅ Proses bot (python bot.py) telah dihentikan."
else
    echo "⚠️ Proses bot (python bot.py) tidak ditemukan berjalan."
fi

# Membersihkan file PID lama jika ada
if [ -f bot.pid ]; then
    rm bot.pid
    echo "🗑️ File 'bot.pid' lama telah dihapus."
fi

echo "✅ Semua proses bot telah dihentikan."