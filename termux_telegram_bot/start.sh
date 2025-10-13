#!/bin/bash
# Skrip ini akan memulai bot di latar belakang dengan stabil.
# Ia akan memeriksa apakah bot sudah berjalan sebelum memulai.

# Pindah ke direktori di mana skrip ini berada
cd "$(dirname "$0")"

# Cek apakah proses bot (baik penjaga maupun bot itu sendiri) sudah berjalan
# Menggunakan pgrep dengan -f untuk mencocokkan seluruh baris perintah
# `grep -v $$` mengecualikan proses skrip start.sh saat ini
if pgrep -f "python bot.py" > /dev/null || pgrep -f "bash -c" | grep -q "run_watcher"; then
    echo "🔵 Bot tampaknya sudah berjalan. Hentikan dulu dengan ./stop.sh jika ingin memulai ulang."
    exit 1
fi

# Fungsi ini berisi loop penjaga yang akan terus berjalan di latar belakang
run_watcher() {
    while true; do
        echo "[$(date)] 🚀 Memulai bot..." >> bot.log
        python bot.py >> bot.log 2>&1
        echo "[$(date)] ⚠️ Bot berhenti. Me-restart dalam 15 detik..." >> bot.log
        sleep 15
    done
}

# Jalankan fungsi penjaga di latar belakang menggunakan nohup
# nohup memastikan proses tetap berjalan bahkan jika terminal ditutup
# & mengirim proses ke latar belakang
nohup bash -c "$(declare -f run_watcher); run_watcher" > /dev/null 2>&1 &

echo "✅ Bot telah dimulai di latar belakang."
echo "   - Log dapat dipantau dengan perintah: tail -f bot.log"
echo "   - Untuk menghentikan bot, jalankan: ./stop.sh"