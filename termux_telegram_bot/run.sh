#!/bin/bash
# Skrip ini menjalankan bot secara langsung di foreground.
# Ini berguna untuk debugging atau jika Anda tidak ingin bot berjalan terus-menerus.

# Pindah ke direktori skrip agar path file (seperti .env) berfungsi
cd "$(dirname "$0")"

echo "🚀 Menjalankan bot di foreground. Tekan Ctrl+C untuk berhenti."
python bot.py