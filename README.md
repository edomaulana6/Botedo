# 🤖 Bot Telegram Serbaguna untuk Termux 🤖

Halo! Ini adalah bot Telegram yang dibuat khusus untuk berjalan secara stabil di lingkungan Termux.

## ✨ Fitur Utama ✨

*   **/unduh <judul atau URL>**: Mengunduh video atau audio dari berbagai sumber (YouTube, TikTok, dll.). Cukup berikan judul untuk dicari atau URL langsung. Bot akan memberikan pilihan format.
*   **/cari_foto <kata kunci>**: Mencari 5 gambar teratas berdasarkan kata kunci yang Anda berikan.
*   **/jadwal_azan <nama kota>**: Menampilkan jadwal salat lengkap untuk kota di Indonesia.
*   **/help**: Menampilkan daftar semua perintah yang tersedia.

---

## 🛠️ Cara Pemasangan di Termux 🛠️

Ikuti langkah-langkah ini satu per satu.

**Langkah 1: Persiapan Termux**

Buka Termux, lalu jalankan perintah ini untuk memastikan semuanya ter-update.
```bash
pkg update && pkg upgrade -y
```

**Langkah 2: Instal Alat yang Dibutuhkan**

Bot ini memerlukan beberapa program dasar agar bisa berjalan.
```bash
pkg install python git ffmpeg -y
```
*   `python`: Untuk menjalankan kode bot.
*   `git`: Untuk mengunduh file bot dari repositori.
*   `ffmpeg`: Penting untuk memproses video dan audio.

**Langkah 3: Unduh Kode Bot**

1.  Unduh (clone) file bot dari repositori ini. Ganti `<URL_REPOSITORY>` dengan URL yang benar.
    ```bash
    git clone <URL_REPOSITORY>
    ```
2.  Masuk ke dalam folder bot yang baru saja diunduh.
    ```bash
    cd termux_telegram_bot
    ```
> **Penting**: Semua perintah selanjutnya harus dijalankan dari dalam folder `termux_telegram_bot`.

**Langkah 4: Instal Dependensi Python**

Jalankan perintah ini untuk menginstal semua pustaka Python yang dibutuhkan oleh bot.
```bash
pip install -r requirements.txt
```

**Langkah 5: Atur Token Bot Anda**

1.  Salin file konfigurasi contoh.
    ```bash
    cp .env.example .env
    ```
2.  Buka file `.env` yang baru dibuat menggunakan editor teks seperti `nano`.
    ```bash
    nano .env
    ```
3.  Di dalamnya, ganti `ISI_TOKEN_ANDA_DISINI` dengan token bot Anda yang didapat dari [@BotFather](https://t.me/BotFather).
4.  Simpan file dengan menekan `Ctrl` + `X`, lalu `Y`, lalu `Enter`.

---

## 🚀 Menjalankan Bot (Stabil & Otomatis) 🚀

Cukup jalankan satu skrip untuk memulai, dan satu skrip untuk berhenti.

### Untuk Memulai Bot:

Jalankan skrip `start.sh`. Bot akan secara otomatis berjalan di latar belakang dan akan me-restart sendiri jika terjadi error.
```bash
./start.sh
```
Anda akan melihat pesan konfirmasi, dan terminal bisa langsung Anda gunakan untuk hal lain.

### Untuk Memantau Log (Opsional):

Jika Anda ingin melihat aktivitas bot, gunakan perintah ini:
```bash
tail -f bot.log
```

### Untuk Menghentikan Bot:

Jalankan skrip `stop.sh`. Ini akan menghentikan semua proses bot dengan aman.
```bash
./stop.sh
```

Selamat mencoba!

---

## 💡 Tips Tambahan: Jika Gagal Download 💡

Terkadang, situs seperti YouTube mengubah cara kerja mereka. Jika bot gagal mengunduh, coba perbarui pustaka `yt-dlp` dengan perintah ini:
```bash
pip install --upgrade yt-dlp
```
Lalu, restart botnya dengan menjalankan `./stop.sh` diikuti `./start.sh`.