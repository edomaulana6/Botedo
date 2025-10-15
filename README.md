# 🤖 Bot Telegram Serbaguna untuk Termux 🤖

Halo! Ini adalah bot Telegram yang dibuat khusus untuk berjalan secara stabil di lingkungan Termux. Bot ini dirancang agar mudah digunakan melalui sistem menu interaktif.

## ✨ Fitur Utama ✨

Bot ini dilengkapi dengan beberapa fitur utama yang bisa diakses dengan mudah:

*   **Menu Interaktif**: Gunakan perintah `/menu` untuk mengakses semua fitur bot melalui tombol yang mudah dinavigasi.
*   **Downloader Video & Audio**: Cari video dari YouTube dan unduh dalam format video atau audio.
*   **Pencarian Gambar**: Cari gambar apa pun dari internet.
*   **Jadwal Salat**: Dapatkan jadwal salat untuk kota-kota di seluruh Indonesia.

---

## 🛠️ Cara Pemasangan di Termux 🛠️

Ikuti langkah-langkah ini satu per satu.

**Langkah 1: Persiapan Termux**
Buka Termux dan jalankan perintah ini untuk memperbarui sistem Anda.
```bash
pkg update && pkg upgrade -y
```

**Langkah 2: Instal Alat yang Dibutuhkan**
Bot ini memerlukan `python`, `git`, dan `ffmpeg`.
```bash
pkg install python git ffmpeg -y
```

**Langkah 3: Unduh Kode Bot**
Ganti `<URL_REPOSITORY>` dengan URL Git yang benar.
```bash
git clone <URL_REPOSITORY> termux_telegram_bot
cd termux_telegram_bot
```
> **Penting**: Semua perintah selanjutnya harus dijalankan dari dalam folder `termux_telegram_bot`.

**Langkah 4: Instal Dependensi Python**
```bash
pip install -r requirements.txt
```

**Langkah 5: Atur Token Bot Anda**
1.  Buat file `.env` dengan menyalin contoh yang ada.
    ```bash
    cp .env.example .env
    ```
2.  Buka file tersebut (`nano .env`) dan masukkan token bot Anda yang didapat dari [@BotFather](https://t.me/BotFather).
    ```
    TELEGRAM_TOKEN=ISI_TOKEN_ANDA_DISINI
    ```
3.  Simpan file tersebut.

---

## 🚀 Cara Menjalankan Bot 🚀

### Mode Stabil (Direkomendasikan)
Jalankan bot di latar belakang. Bot akan tetap hidup dan otomatis restart jika terjadi error.
```bash
# Untuk memulai
./start.sh

# Untuk menghentikan
./stop.sh
```

### Mode Normal (Untuk Debugging)
Jalankan bot langsung di terminal Anda. Bot akan berhenti jika Anda menutup Termux.
```bash
./run.sh
```

---

## 📖 Cara Menggunakan Bot 📖

Cukup kirim perintah `/menu` ke bot Anda. Semua fitur dapat diakses dari sana. Bot akan memandu Anda melalui tombol-tombol interaktif, sehingga Anda tidak perlu menghafal banyak perintah!

---

## 💡 Tips Tambahan 💡

Jika unduhan gagal, coba perbarui pustaka `yt-dlp` dengan:
```bash
pip install --upgrade yt-dlp
```
Lalu, restart botnya (`./stop.sh` lalu `./start.sh`).