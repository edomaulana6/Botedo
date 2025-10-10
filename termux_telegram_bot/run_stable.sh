#!/bin/bash
# Skrip ini akan menjalankan bot secara terus-menerus.
# Jika bot crash, skrip akan secara otomatis me-restartnya.

# Pindah ke direktori skrip agar path file (seperti .env) berfungsi
cd "$(dirname "$0")"

while true; do
    echo "[$(date)] 🚀 Memulai bot..."
    python bot.py
    echo "[$(date)] ⚠️ Bot berhenti. Me-restart dalam 5 detik..."
    sleep 5
done