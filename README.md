# 🤖 Bot Telegram Serbaguna untuk Termux 🤖

Selamat datang! Ini adalah panduan untuk memasang bot Telegram multifungsi di aplikasi Termux Anda. Bot ini dirancang agar mudah dipasang dan digunakan, bahkan untuk pemula.

---

## 🛠️ Panduan Instalasi (Langkah demi Langkah) 🛠️

Ikuti setiap langkah dengan teliti. Cukup salin (`copy-paste`) setiap perintah ke dalam Termux Anda lalu tekan `Enter`.

### Langkah 1: Siapkan Termux Anda

Pertama, kita perlu memastikan Termux dan semua paketnya sudah diperbarui.

```bash
pkg update && pkg upgrade -y
```

### Langkah 2: Instal Alat-alat yang Diperlukan

Bot ini membutuhkan beberapa program dasar agar bisa berjalan. Perintah ini akan menginstalnya untuk Anda.

*   `git`: Untuk mengunduh kode bot dari GitHub.
*   `python`: Bahasa pemrograman yang digunakan bot ini.
*   `ffmpeg`: Untuk memproses file video dan audio.
*   `rust` & `clang`: Diperlukan untuk menginstal beberapa komponen penting dari pustaka Python.

```bash
pkg install git python ffmpeg rust clang -y
```

### Langkah 3: Unduh Kode Bot

Sekarang, kita akan mengunduh kode bot dari repositori ini ke dalam Termux.

```bash
git clone https://github.com/user/repo.git termux_telegram_bot
```
**Penting:** Ganti `https://github.com/user/repo.git` dengan URL repositori yang benar.

Setelah selesai, masuk ke direktori yang baru saja dibuat:
```bash
cd termux_telegram_bot
```
> **Catatan**: Semua perintah selanjutnya **harus** dijalankan dari dalam folder `termux_telegram_bot` ini.

### Langkah 4: Instal Komponen Bot

Perintah ini akan menginstal semua pustaka Python yang dibutuhkan oleh bot. Proses ini mungkin memakan waktu beberapa menit.

```bash
pip install -r requirements.txt
```

### Langkah 5: Atur Kunci Rahasia (Token) Bot Anda

Bot perlu "kunci" untuk bisa terhubung ke akun bot Telegram Anda.

1.  **Salin file contoh konfigurasi.** Perintah ini akan membuat file `.env` yang akan kita isi.
    ```bash
    cp .env.example .env
    ```

2.  **Isi Token Anda.** Sekarang, buka file `.env` tersebut dengan editor `nano`.
    ```bash
    nano .env
    ```

3.  Anda akan melihat teks berikut di layar:
    ```env
    TELEGRAM_TOKEN=ISI_TOKEN_TELEGRAM_ANDA_DISINI
    GEMINI_API_KEY=ISI_KUNCI_GEMINI_ANDA_DISINI
    ```

4.  Ganti `ISI_TOKEN_TELEGRAM_ANDA_DISINI` dengan token bot Anda yang didapat dari [@BotFather](https://t.me/BotFather).
5.  Jika Anda ingin menggunakan fitur AI, ganti juga `ISI_KUNCI_GEMINI_ANDA_DISINI` dengan kunci API Anda dari [Google AI Studio](https://aistudio.google.com/). Jika tidak, Anda bisa membiarkannya kosong.

6.  Untuk **menyimpan dan keluar** dari editor nano:
    *   Tekan `CTRL` + `X`
    *   Tekan `Y` (untuk Yes)
    *   Tekan `Enter`

---

## 🚀 Cara Menjalankan Bot 🚀

Anda punya dua cara untuk menjalankan bot:

### Mode Stabil (Direkomendasikan)

Gunakan skrip ini untuk menjalankan bot di latar belakang. Bot akan tetap hidup meskipun aplikasi Termux Anda ditutup.

*   **Untuk memulai bot:**
    ```bash
    ./start.sh
    ```
*   **Untuk menghentikan bot:**
    ```bash
    ./stop.sh
    ```

### Mode Debug (Untuk Cek Error)

Jika bot mengalami masalah, gunakan mode ini. Semua aktivitas dan error akan ditampilkan langsung di layar. Bot akan berhenti jika Anda menutup sesi Termux.

*   **Untuk memulai mode debug:**
    ```bash
    ./run.sh
    ```

---

## ✨ Fitur Bot ✨

Setelah bot berjalan, Anda bisa mulai dengan mengirim perintah `/menu` untuk melihat semua fitur yang tersedia dalam bentuk tombol interaktif.

*   **Downloader Cerdas**: Unduh video/audio dari YouTube, TikTok, Instagram, dll.
*   **Editor Gambar AI**: Edit gambar dengan perintah seperti `/toanime`, `/ootd`, atau gunakan prompt kustom Anda.
*   **Pencarian**: Cari gambar dengan `/cari_gambar` atau informasi di Google dengan `/google`.
*   **Fitur Islami**: Dapatkan jadwal salat dengan `/jadwal_azan`.

Jika Anda menemukan masalah, jangan ragu untuk melaporkannya!