# 🤖 Bot Telegram Serbaguna untuk Termux 🤖

Halo! Ini adalah bot Telegram yang dibuat khusus untuk jalan di Termux. Bot ini bisa membantumu download macem-macem hal, mulai dari lagu sampai gambar.

## ✨ Fitur Keren Bot Ini ✨

*   **Unduh Apa Aja dari URL**: Tinggal kasih link (misalnya dari YouTube, Instagram, dll), nanti bot tanya mau dijadiin video atau audio.
*   **Cari Lagu di YouTube**:
    *   **Pencarian Biasa**: Cari judul lagu, nanti bot kasih 5 hasil terbaik. Lengkap dengan gambar thumbnail dan tombol buat milih video atau audio.
    *   **Cari Cepat**: Pakai perintah `/caricepat`, ketik judul lagu, dan bot bakal langsung kirim file audionya.
*   **Cari Gambar di Web**: Pakai perintah `/cari_gambar`, kamu bisa cari gambar apa aja dari internet.

---

## 🛠️ Cara Pasang di Termux (Gampang Kok!) 🛠️

Ikuti langkah-langkah ini satu per satu ya.

**Langkah 1: Siapin Termux kamu**

Buka Termux, terus ketik perintah ini buat update sistemnya.
```bash
pkg update && pkg upgrade
```

**Langkah 2: Install Alat-alat yang Dibutuhin**

Bot ini butuh beberapa alat biar bisa jalan. Ketik perintah ini:
```bash
pkg install python git ffmpeg
```
*   `python` itu buat ngejalanin botnya.
*   `git` untuk mengunduh file bot dari repositori.
*   `ffmpeg` penting untuk memproses video dan audio.

**Langkah 3: Unduh Bot dan Masuk ke Direktori**

1.  Unduh file bot menggunakan `git`. Ganti `<URL_REPOSITORY>` dengan URL yang benar.
    ```bash
    git clone <URL_REPOSITORY>
    ```
2.  Sekarang, masuk ke dalam folder utama bot. **Ini langkah penting!**
    ```bash
    cd termux_telegram_bot
    ```
> Semua perintah selanjutnya harus dijalankan dari dalam folder `termux_telegram_bot` ini.

**Langkah 4: Install Dependensi Python**

Jalankan perintah ini untuk menginstal semua "bumbu dapur" yang dibutuhkan oleh bot.
```bash
pip install -r requirements.txt
```

**Langkah 5: Masukkan Token Rahasia Bot Kamu**

1.  Buka file `.env` menggunakan editor teks `nano`.
    ```bash
    nano .env
    ```
2.  Di dalamnya, Anda akan melihat baris `TELEGRAM_TOKEN="ISI_TOKEN_ANDA_DISINI"`. Ganti `ISI_TOKEN_ANDA_DISINI` dengan token bot Anda yang didapat dari [@BotFather](https://t.me/BotFather).
3.  Simpan file dengan menekan `Ctrl` + `X`, lalu `Y`, lalu `Enter`.

---

## 🚀 Cara Menjalankan Bot 🚀

Kalau semua langkah di atas udah beres, sekarang tinggal nyalain botnya!

### Cara 1: Dijalankan di Latar Belakang (Direkomendasikan)

Ini cara terbaik biar bot tetap hidup meskipun aplikasi Termux kamu tertutup.

1.  Pastikan kamu ada di dalam folder `termux_telegram_bot`.
2.  Jalankan skrip `start.sh`:
    ```bash
    ./start.sh
    ```
    Bot akan mulai berjalan di latar belakang.

**Untuk menghentikan bot:**
Jalankan skrip `stop.sh`:
```bash
./stop.sh
```

### Cara 2: Dijalankan Langsung (Untuk Cek Error/Debugging)

Cara ini cocok kalau kamu mau lihat log atau pesan error secara langsung di layar.

1.  Pastikan kamu ada di dalam folder `termux_telegram_bot`.
2.  Jalankan perintah ini:
    ```bash
    python bot.py
    ```
Bot akan berjalan di sesi terminalmu. Untuk mematikannya, cukup tekan `Ctrl` + `C`.

Selamat mencoba!

---

## 🔧 Mengatasi Masalah Umum 🔧

### Error `dpkg` saat `pkg upgrade`

Jika Anda menemukan error seperti di bawah ini saat menjalankan `pkg upgrade`:
```
E: Sub-process /data/data/com.termux/files/usr/bin/dpkg returned an error code (1)
```
Ini biasanya terjadi karena ada paket yang tidak terkonfigurasi dengan benar setelah proses update. Untuk memperbaikinya, jalankan perintah berikut:
```bash
dpkg --configure -a
```
Setelah perintah di atas selesai, coba jalankan kembali `pkg upgrade`.

### Error Koneksi (`TimedOut`)

Jika bot berjalan tetapi tidak merespons dan Anda melihat error `telegram.error.TimedOut` di log, ini berarti koneksi dari Termux ke server Telegram gagal.

**Langkah-langkah diagnosis:**
1.  **Cek Koneksi Internet**: Pastikan Anda memiliki koneksi internet yang aktif. Coba buka browser atau aplikasi lain.
2.  **Gunakan `ping`**: Coba ping ke server Google untuk memeriksa koneksi dasar.
    ```bash
    ping 8.8.8.8
    ```
    Jika Anda mendapatkan balasan, berarti koneksi internet Anda berfungsi.
3.  **Cek Akses ke Telegram**: Terkadang, hanya akses ke Telegram yang diblokir. Coba perintah ini:
    ```bash
    curl https://api.telegram.org
    ```
    Jika Anda melihat tulisan `{"ok":false,"error_code":404,"description":"Not Found"}` atau sejenisnya, berarti Anda **bisa** menjangkau server Telegram. Jika perintah ini *hang* atau *timeout*, berarti ada masalah pada jaringan Anda untuk mengakses Telegram.

**Solusi yang bisa dicoba:**
*   Restart koneksi data atau Wi-Fi Anda.
*   Gunakan jaringan yang berbeda (misalnya, beralih dari Wi-Fi ke data seluler, atau sebaliknya).
*   Gunakan VPN jika Anda menduga ada pemblokiran jaringan.

---

## 💡 Tips Tambahan: Kalau Gagal Download 💡

Terkadang, situs seperti YouTube mengubah cara kerja mereka. Jika bot gagal download, coba update `yt-dlp` dengan perintah ini:
```bash
pip install --upgrade yt-dlp
```
Lalu, restart botnya.