# 🤖 Bot Telegram Serbaguna untuk Termux 🤖

Selamat datang! Ini adalah panduan super-mudah untuk memasang bot Telegram di aplikasi Termux Anda. Struktur proyek ini sudah disederhanakan agar tidak ada lagi kebingungan.

---

## 🛠️ Panduan Instalasi (Final & Paling Mudah) 🛠️

Ikuti setiap langkah dengan teliti. Cukup salin (`copy-paste`) setiap perintah ke dalam Termux Anda lalu tekan `Enter`.

### Langkah 1: Persiapan Awal Termux
Pastikan Termux Anda dalam kondisi terbaru.
```bash
pkg update && pkg upgrade -y
```

### Langkah 2: Instal Program-program Penting
Bot ini butuh beberapa "alat" untuk bekerja. Perintah di bawah ini akan menginstal semuanya sekaligus.
*   `git`: Untuk mengunduh kode bot.
*   `python`: Bahasa yang digunakan bot.
*   `ffmpeg`: Untuk memproses video & audio.
*   `rust` & `clang`: Agar komponen Python bisa diinstal tanpa error.

```bash
pkg install git python ffmpeg rust clang -y
```

### Langkah 3: Unduh Kode Bot
Perintah ini akan mengunduh semua file bot ke dalam sebuah folder baru bernama `termux_bot`.
```bash
git clone https://github.com/user/repo.git termux_bot
```
**Penting:** Ganti `https://github.com/user/repo.git` dengan URL Git repositori ini.

### Langkah 4: Masuk ke Folder Bot
Setelah selesai mengunduh, Anda **wajib** masuk ke folder tersebut.
```bash
cd termux_bot
```
> **Catatan**: Semua perintah selanjutnya harus dijalankan dari dalam folder ini.

### Langkah 5: Instal Komponen Inti Bot
Sekarang kita sudah berada di folder yang benar, saatnya menginstal semua pustaka Python yang dibutuhkan bot.
```bash
pip install -r requirements.txt
```
Proses ini mungkin akan memakan waktu beberapa menit. Harap bersabar.

### Langkah 6: Buat dan Isi File Konfigurasi
Ini adalah langkah terakhir. Kita akan membuat file `.env` untuk menyimpan token rahasia bot Anda.

1.  **Salin file contoh.** Karena kita sudah berada di folder yang benar, perintah ini **pasti berhasil**.
    ```bash
    cp .env.example .env
    ```

2.  **Buka file tersebut dengan editor `nano`.**
    ```bash
    nano .env
    ```

3.  Anda akan melihat teks ini:
    ```env
    TELEGRAM_TOKEN=ISI_TOKEN_TELEGRAM_ANDA_DISINI
    GEMINI_API_KEY=ISI_KUNCI_GEMINI_ANDA_DISINI
    ```

4.  Ganti `ISI_TOKEN_TELEGRAM_ANDA_DISINI` dengan token bot Anda (dapatkan dari [@BotFather](https://t.me/BotFather)).
5.  Jika ingin pakai fitur AI, ganti juga `ISI_KUNCI_GEMINI_ANDA_DISINI` dengan kunci API Anda dari [Google AI Studio](https://aistudio.google.com/).

6.  **Cara Menyimpan & Keluar dari `nano`:**
    *   Tekan `CTRL` + `X`
    *   Tekan `Y` (artinya Yes)
    *   Tekan `Enter`

**Pemasangan Selesai!**

---

## 🚀 Cara Menjalankan Bot 🚀

*   **Mode Stabil (Direkomendasikan):**
    Jalankan bot di latar belakang. Bot akan tetap hidup meskipun Termux ditutup.
    ```bash
    ./start.sh
    ```

*   **Menghentikan Bot:**
    ```bash
    ./stop.sh
    ```

*   **Mode Debug (Jika Ada Masalah):**
    Gunakan ini untuk melihat log error secara langsung di layar.
    ```bash
    ./run.sh
    ```

---

## ✨ Fitur-fitur Bot ✨

Kirim perintah `/menu` untuk melihat semua fitur dalam bentuk tombol yang mudah digunakan.
*   **Downloader**: Unduh video/audio dari berbagai sumber.
*   **Editor AI**: Edit gambar dengan perintah `/toanime`, `/ootd`, dll.
*   **Pencarian**: Cari gambar atau informasi di Google.
*   **Islami**: Lihat jadwal salat.

Jika Anda masih menemukan kendala, jangan ragu untuk bertanya!