#!/bin/bash
# Skrip ini akan menghentikan semua proses bot yang berjalan di latar belakang.

# Pindah ke direktori di mana skrip ini berada
cd "$(dirname "$0")"

echo "🔴 Menghentikan semua proses bot..."

# Menghentikan proses penjaga (watcher) yang dijalankan oleh start.sh
# Pola "run_watcher" sangat spesifik untuk proses latar belakang kita
pkill -f "run_watcher"
if [ $? -eq 0 ]; then
    echo "✅ Proses penjaga (watcher) telah dihentikan."
else
    echo "⚠️ Proses penjaga (watcher) tidak ditemukan berjalan."
fi

# Menghentikan proses bot Python itu sendiri
pkill -f "python bot.py"
if [ $? -eq 0 ]; then
    echo "✅ Proses bot (python bot.py) telah dihentikan."
else
    echo "⚠️ Proses bot (python bot.py) tidak ditemukan berjalan."
fi

echo "✅ Semua proses bot telah berhasil dihentikan."