#!/bin/bash
# Skrip ini akan menjalankan bot secara terus-menerus dan stabil.
# Jika bot crash, skrip akan secara otomatis me-restartnya.

# Pindah ke direktori skrip agar path file (seperti .env dan bot.py) berfungsi dengan benar
cd "$(dirname "$0")"

# Jalankan bot dalam loop tak terbatas
while true; do
    echo "[$(date)] 🚀 Memulai bot..."
    # Menjalankan bot dan mengarahkan semua output (stdout & stderr) ke bot.log
    python bot.py >> bot.log 2>&1
    echo "[$(date)] ⚠️ Bot berhenti. Me-restart dalam 15 detik..."
    sleep 15
done