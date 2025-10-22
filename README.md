# 🤖 Bot Telegram Serbaguna untuk Termux 🤖

Selamat datang! Ini adalah panduan super-mudah untuk memasang bot Telegram di aplikasi Termux Anda. Setiap langkah dijelaskan dengan detail agar tidak ada lagi error.

---

## 🛠️ Panduan Instalasi (Dijamin Mudah) 🛠️

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

### Langkah 3: Unduh Kode Bot & Masuk ke Folder-nya

Perintah ini akan mengunduh kode bot dari GitHub, lalu **langsung memindahkan Anda ke dalam folder yang benar**.

```bash
git clone https://github.com/user/repo.git termux_telegram_bot && cd termux_telegram_bot
```
**Penting:**
*   Ganti `https://github.com/user/repo.git` dengan URL Git repositori ini.
*   Pastikan perintah di atas berhasil. Setelah selesai, Anda seharusnya sudah berada di dalam folder `termux_telegram_bot`.

### Langkah 4: Instal Komponen Inti Bot

Sekarang kita sudah berada di folder yang benar, saatnya menginstal semua pustaka Python yang dibutuhkan bot.

```bash
pip install -r requirements.txt
```
Proses ini mungkin akan memakan waktu beberapa menit. Harap bersabar.

### Langkah 5: Buat dan Isi File Konfigurasi

Ini adalah langkah paling penting. Kita akan membuat file `.env` untuk menyimpan token rahasia bot Anda.

1.  **Pastikan Anda Berada di Folder yang Benar.** Jalankan perintah ini:
    ```bash
    pwd
    ```
    Pastikan outputnya diakhiri dengan `/termux_telegram_bot`. Jika tidak, ulangi langkah 3.

2.  **Sekarang, salin file contoh.** Karena kita sudah berada di folder yang benar, perintah ini **pasti berhasil**.
    ```bash
    cp .env.example .env
    ```

3.  **Buka file tersebut dengan editor `nano`.**
    ```bash
    nano .env
    ```

4.  Anda akan melihat teks ini:
    ```env
    TELEGRAM_TOKEN=ISI_TOKEN_TELEGRAM_ANDA_DISINI
    GEMINI_API_KEY=ISI_KUNCI_GEMINI_ANDA_DISINI
    ```

5.  Ganti `ISI_TOKEN_TELEGRAM_ANDA_DISINI` dengan token bot Anda (dapatkan dari [@BotFather](https://t.me/BotFather)).
6.  Jika ingin pakai fitur AI, ganti juga `ISI_KUNCI_GEMINI_ANDA_DISINI` dengan kunci API Anda dari [Google AI Studio](https://aistudio.google.com/).

7.  **Cara Menyimpan & Keluar dari `nano`:**
    *   Tekan `CTRL` + `X`
    *   Tekan `Y` (artinya Yes)
    *   Tekan `Enter`

Instalasi Selesai!

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