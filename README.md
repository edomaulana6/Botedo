# 🤖 Bot Telegram Serbaguna untuk Termux 🤖

Halo! Ini adalah bot Telegram yang dibuat khusus untuk berjalan secara stabil di lingkungan Termux.

## ✨ Fitur Utama ✨

*   **/menu**: Menampilkan menu interaktif untuk semua fitur.
*   **/unduh <judul atau URL>**: Perintah serbaguna untuk mengunduh media dari YouTube, TikTok, Instagram, Facebook, Mediafire, dan ratusan situs lainnya.
*   **/cari_foto <kata kunci>**: Mencari 5 gambar teratas berdasarkan kata kunci.
*   **/jadwal_azan <nama kota>**: Menampilkan jadwal salat lengkap untuk kota di Indonesia.
*   **Notifikasi Penjaga Admin**: Memberikan peringatan di grup setiap kali ada admin yang diturunkan pangkatnya.

---

## 🛠️ Cara Pemasangan di Termux 🛠️

Ikuti langkah-langkah ini satu per satu.

**1. Persiapan Termux**
```bash
pkg update && pkg upgrade -y
```

**2. Instal Alat yang Dibutuhkan**
```bash
pkg install python git ffmpeg -y
```

**3. Unduh Kode Bot**
```bash
# Ganti <URL_REPOSITORY> dengan URL yang benar
git clone <URL_REPOSITORY>
cd termux_telegram_bot
```
> **Penting**: Semua perintah selanjutnya harus dijalankan dari dalam folder `termux_telegram_bot`.

**4. Instal Dependensi Python**
```bash
pip install -r requirements.txt
```

**5. Atur Token Bot Anda**
Buka file `.env` menggunakan editor teks (misalnya `nano .env`) dan masukkan token bot Anda yang didapat dari [@BotFather](https://t.me/BotFather) seperti ini:
```
TELEGRAM_TOKEN=ISI_TOKEN_ANDA_DISINI
```

---

## 🚀 Cara Menjalankan Bot 🚀

Anda bisa memilih dua cara untuk menjalankan bot:

### Mode Normal (Untuk Debugging)
Jalankan bot langsung di terminal Anda. Bot akan berhenti jika Anda menutup Termux atau menekan `Ctrl+C`.
```bash
./run.sh
```

### Mode Stabil (Direkomendasikan)
Jalankan bot di latar belakang. Bot akan tetap hidup dan otomatis restart jika terjadi error.
```bash
# Untuk memulai
./start.sh

# Untuk menghentikan
./stop.sh

# Untuk melihat log (opsional)
tail -f bot.log
```

---

## 🔧 Mengatasi Masalah Umum 🔧

### Error `dpkg` saat `pkg upgrade`
Jika Anda menemukan error saat `pkg upgrade`, jalankan perintah ini, lalu ulangi upgrade:
```bash
dpkg --configure -a
```

### Error Koneksi (`TimedOut`)
Jika bot tidak merespons, itu mungkin masalah jaringan. Coba restart koneksi data/Wi-Fi Anda atau gunakan VPN.

---

## 💡 Tips Tambahan 💡

Jika unduhan gagal, coba perbarui pustaka downloader dengan:
```bash
pip install --upgrade yt-dlp
```
Lalu, restart botnya (`./stop.sh` lalu `./start.sh`).