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
*   `git` buat download file botnya (jika diperlukan).
*   `ffmpeg` penting untuk memproses video dan audio.

**Langkah 3: Buat Folder untuk Bot**

Biar rapi, kita buat folder khusus untuk bot.
```bash
mkdir termux_telegram_bot
cd termux_telegram_bot
```
> Setelah ini, pastikan semua file bot (`bot.py`, `requirements.txt`, dll.) ada di dalam folder ini.

**Langkah 4: Install "Bumbu Dapur" buat Python**

Bot ini butuh beberapa library Python. Buat file `requirements.txt` lalu install.
```bash
pip install -r requirements.txt
```

**Langkah 5: Masukin Token Rahasia Bot Kamu**

Setiap bot punya token rahasia. Biar botnya bisa nyala, kamu harus masukin tokenmu ke dalam file `.env`.

1.  Buka file `.env` pakai editor `nano`.
    ```bash
    nano .env
    ```
2.  Di dalamnya, ganti tulisan `YOUR_TOKEN_HERE` dengan token bot kamu yang didapat dari [@BotFather](https://t.me/BotFather).
3.  Simpan filenya dengan menekan `Ctrl` + `X`, lalu `Y`, lalu `Enter`.

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

## 💡 Tips Tambahan: Kalau Gagal Download 💡

Terkadang, situs seperti YouTube mengubah cara kerja mereka. Jika bot gagal download, coba update `yt-dlp` dengan perintah ini:
```bash
pip install --upgrade yt-dlp
```
Lalu, restart botnya.