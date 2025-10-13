#!/bin/bash
echo "🔴 Menghentikan semua proses bot..."

# Pindah ke direktori skrip untuk memastikan pkill berjalan di konteks yang benar
cd "$(dirname "$0")"

# Menghentikan skrip penjaga (start.sh) yang berjalan di latar belakang
# `pkill -f` akan mencocokkan seluruh baris perintah, membuatnya lebih spesifik
pkill -f "bash ./start.sh"
if [ $? -eq 0 ]; then
    echo "✅ Skrip penjaga (start.sh) telah dihentikan."
else
    echo "⚠️ Skrip penjaga (start.sh) tidak ditemukan berjalan."
fi

# Menghentikan proses bot Python (bot.py) yang mungkin masih berjalan
pkill -f "python bot.py"
if [ $? -eq 0 ]; then
    echo "✅ Proses bot (python bot.py) telah dihentikan."
else
    echo "⚠️ Proses bot (python bot.py) tidak ditemukan berjalan."
fi

# Beri jeda singkat untuk memastikan semua proses benar-benar berhenti sebelum verifikasi
sleep 1

echo "✅ Semua proses bot telah berhasil dihentikan."