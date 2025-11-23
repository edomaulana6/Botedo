# 🤖 Bot Telegram Serbaguna untuk Termux 🤖

Selamat datang! Ini adalah bot Telegram multifungsi yang dirancang khusus untuk berjalan dengan stabil dan andal di lingkungan Termux. Bot ini mudah dioperasikan berkat sistem menu interaktif berbasis tombol.

## ✨ Fitur Unggulan ✨

*   **Sistem Menu Interaktif**: Cukup gunakan perintah `/menu` untuk mengakses semua fitur bot tanpa perlu menghafal banyak perintah.
*   **Downloader Cerdas**:
    *   Mendukung pencarian video/audio dari YouTube.
    *   Mengunduh dari berbagai URL (TikTok, Instagram, Facebook, dll.).
    *   Menampilkan **progress bar** saat mengunduh.
    *   Dapat menggunakan `cookies.txt` untuk mengunduh konten yang memerlukan login.
*   **Editor Gambar AI**: Edit gambar Anda menggunakan model AI generatif dari Google.
    *   Gunakan perintah preset seperti `/toanime`, `/ootd`, `/pretty`.
    *   Gunakan prompt kustom Anda sendiri dengan `/edit_ai`.
*   **Pencarian Multifungsi**:
    *   `/cari_gambar`: Menemukan dan menampilkan 5 gambar teratas.
    *   `/google`: Melakukan pencarian Google dan memberikan hasil teratas.
*   **Fitur Islami**:
    *   `/jadwal_azan`: Mendapatkan jadwal salat untuk kota-kota di seluruh Indonesia.

---

## 🛠️ Panduan Instalasi Lengkap di Termux 🛠️

Ikuti langkah-langkah ini dengan teliti untuk memastikan instalasi berjalan lancar.

**Langkah 1: Perbarui Termux**
Pastikan semua paket di Termux adalah versi terbaru.
```bash
pkg update && pkg upgrade -y
```

**Langkah 2: Instal Dependensi Sistem**
Perintah ini menginstal semua paket dasar yang dibutuhkan bot untuk berfungsi.
```bash
pkg install python git ffmpeg openssh sshpass -y
```

**Langkah 3: Unduh Kode Bot & Masuk ke Direktori**

1.  **Unduh Kode (Clone)**
    Perintah ini akan mengunduh kode bot ke dalam sebuah folder baru bernama `termux_telegram_bot`. Ganti `<URL_REPOSITORY_ANDA>` dengan URL Git proyek ini.
    ```bash
    git clone <URL_REPOSITORY_ANDA> termux_telegram_bot
    ```

2.  **Masuk ke Folder Bot (Sangat Penting!)**
    Setelah selesai, Anda **wajib** pindah ke dalam folder tersebut.
    ```bash
    cd termux_telegram_bot
    ```
    > **PEMBERITAHUAN PENTING:**
    > Semua perintah selanjutnya (`pip install`, `cp .env.example`, `./run.sh`, dll.) **harus** dijalankan dari dalam folder `termux_telegram_bot`. Jika tidak, Anda akan mendapatkan error `No such file or directory`.

**Langkah 4: Instal Pustaka Python**
Perintah ini akan menginstal semua pustaka Python yang dibutuhkan oleh bot.
```bash
pip install -r requirements.txt
```

**Langkah 5: Atur Kunci API Anda**

1.  **Salin File Konfigurasi**
    Perintah ini akan membuat file `.env` dari contoh yang ada. File ini bersifat rahasia dan tidak boleh dibagikan.
    ```bash
    cp .env.example .env
    ```

2.  **Buka File `.env`**
    Gunakan editor teks `nano` untuk mengedit file tersebut.
    ```bash
    nano .env
    ```
    > *Catatan: Jika perintah `nano` gagal, berarti editor belum terinstal. Instal dengan `pkg install nano -y`, lalu ulangi perintah di atas.*

3.  **Isi Kunci API Anda**
    Anda akan melihat konten berikut di dalam file:
    ```ini
    # .env (SEBELUM DIEDIT)
    TELEGRAM_TOKEN="ISI_TOKEN_ANDA_DISINI"
    GEMINI_API_KEY="ISI_KUNCI_API_GEMINI_ANDA_DISINI"
    ```

    Ganti `ISI_..._DISINI` dengan kunci asli yang Anda dapatkan. Pastikan token Anda berada **di dalam tanda kutip (`"`)**.

    **Contoh hasil akhir yang benar:**
    ```ini
    # .env (SESUDAH DIEDIT)
    TELEGRAM_TOKEN="123456:ABC-DEF1234567"
    GEMINI_API_KEY="AIzaSyA...Zb-12345_ABCDE"
    ```
    *   `TELEGRAM_TOKEN`: Dapatkan dari [@BotFather](https://t.me/BotFather) di Telegram.
    *   `GEMINI_API_KEY`: Dapatkan dari [Google AI Studio](https://aistudio.google.com/) (gratis). Wajib diisi jika ingin menggunakan fitur AI.

4.  **Simpan dan Keluar**
    Tekan `CTRL + X`, ketik `Y` untuk konfirmasi, lalu tekan `Enter`.

---

## 🚀 Cara Menjalankan Bot 🚀

### Mode Stabil (Direkomendasikan)
Gunakan skrip ini untuk menjalankan bot di latar belakang. Bot akan tetap hidup meskipun Anda menutup aplikasi Termux dan akan otomatis dimulai ulang jika terjadi error.
```bash
# Untuk memulai bot
./start.sh

# Untuk menghentikan bot
./stop.sh
```

### Mode Debugging
Gunakan skrip ini untuk menjalankan bot di sesi terminal saat ini. Ini berguna untuk melihat log secara langsung, tetapi bot akan mati jika Anda menutup sesi.
```bash
./run.sh
```

---

## 💡 Tips & Trik Pengguna 💡

### Mengatasi Gagal Unduh (Facebook, Instagram, dll.)

Beberapa situs web mengharuskan Anda login untuk melihat atau mengunduh konten. Agar bot dapat melakukannya, Anda perlu memberinya file "cookies".

**Cara Mendapatkan `cookies.txt` (Hanya perlu dilakukan sekali):**

1.  **Gunakan Browser di PC/Laptop (Chrome/Firefox).**
2.  Instal ekstensi browser bernama **"Get cookies.txt"** (aman dan populer).
3.  Buka situs web yang diinginkan (misal, `facebook.com`) dan **login** ke akun Anda.
4.  Klik ikon ekstensi "Get cookies.txt" dan pilih **"Export"**. Sebuah file bernama `cookies.txt` akan terunduh.

**Cara Menggunakan `cookies.txt` di Termux:**

1.  Pindahkan file `cookies.txt` yang baru Anda unduh ke folder "Download" di penyimpanan internal ponsel Anda.
2.  Buka Termux dan salin file tersebut ke direktori bot:
    ```bash
    cp /sdcard/Download/cookies.txt ~/termux_telegram_bot/cookies.txt
    ```
    *(Catatan: Sesuaikan path `/sdcard/Download/` jika Anda menyimpannya di tempat lain).*
3.  Restart bot Anda (`./stop.sh` lalu `./start.sh`) agar bot memuat cookies baru.

Sekarang bot akan secara otomatis menggunakan cookies ini untuk mengunduh, memungkinkannya mengakses konten yang dilindungi login. Jika unduhan kembali gagal di masa mendatang, cukup ulangi langkah-langkah ini untuk mendapatkan cookies yang baru.