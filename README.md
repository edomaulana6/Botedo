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

## 🚀 Cara Menjalankan Bot 🚀

Anda bisa memilih dua cara untuk menjalankan bot, sesuai kebutuhan Anda.

### Mode 1: Normal (Untuk Debugging atau Penggunaan Singkat)

Mode ini akan menjalankan bot langsung di terminal Anda (di *foreground*). Ini berguna jika Anda ingin melihat output atau pesan error secara langsung. Bot akan berhenti jika Anda menutup sesi Termux atau menekan `Ctrl+C`.

**Untuk memulai:**
```bash
./run.sh
```
**Untuk berhenti:**
Tekan `Ctrl` + `C` di terminal.

### Mode 2: Stabil (Untuk Penggunaan Jangka Panjang)

Mode ini akan menjalankan bot di latar belakang. Bot akan tetap hidup meskipun Anda menutup aplikasi Termux dan akan secara otomatis me-restart jika terjadi error.

**Untuk memulai:**
```bash
./start.sh
```
Anda akan melihat pesan konfirmasi, dan terminal bisa langsung Anda gunakan untuk hal lain.

**Untuk memantau log (opsional):**
```bash
tail -f bot.log
```

**Untuk menghentikan:**
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