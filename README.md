# 🤖 Bot Telegram Serbaguna untuk Termux 🤖

Halo! Ini adalah bot Telegram yang dibuat khusus untuk jalan di Termux. Bot ini bisa membantumu download macem-macem hal, mulai dari lagu sampai gambar.

## ✨ Fitur Keren Bot Ini ✨

*   **Unduh Apa Aja dari URL**: Tinggal kasih link (misalnya dari YouTube, Instagram, dll), nanti bot tanya mau dijadiin video atau audio.
*   **Cari Lagu di YouTube**:
    *   **Pencarian Biasa**: Cari judul lagu, nanti bot kasih 5 hasil terbaik (yang durasinya pendek, cocok buat lagu). Lengkap dengan gambar thumbnail dan tombol buat milih video atau audio.
    *   **Cari Cepat**: Pakai perintah `/caricepat`, ketik judul lagu, dan bot bakal langsung kirim file audionya. Gak pake lama!
*   **Cari Gambar di Web**: Pakai perintah `/cari_gambar`, kamu bisa cari gambar apa aja dari internet. (Tips: Tambahkan `site:pinterest.com` di akhir pencarianmu untuk hasil khusus dari Pinterest).

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
pkg install python git ffmpeg aria2
```
*   `python` itu buat ngejalanin botnya.
*   `git` buat download file botnya.
*   `ffmpeg` buat proses video dan audio.
*   `aria2` buat mempercepat proses download.

**Langkah 3: Download File Botnya**

Sekarang, kita ambil file botnya dari internet.
*(Nanti ganti `<repository_url>` dengan link repository-nya ya)*
```bash
git clone <repository_url>
cd termux_telegram_bot
```
> Kalau kamu dapet filenya gak lewat `git`, cukup masuk aja ke folder tempat kamu nyimpen file botnya.

**Langkah 4: Install "Bumbu Dapur" buat Python**

Bot ini butuh beberapa library Python. Untungnya, daftarnya udah ada, jadi tinggal install aja.
```bash
pip install -r requirements.txt
```

**Langkah 5: Masukin Token Rahasia Bot Kamu**

Setiap bot punya token rahasia. Biar botnya bisa nyala, kamu harus masukin tokenmu.

1.  Buka file `.env` pakai editor `nano`.
    ```bash
    nano .env
    ```
2.  Di dalamnya, kamu akan melihat `YOUR_TOKEN_HERE="YOUR_TOKEN_HERE"`. Ganti tulisan `YOUR_TOKEN_HERE` di dalam tanda kutip dengan token bot kamu yang didapat dari [@BotFather](https://t.me/BotFather).
3.  Simpan filenya dengan menekan `Ctrl` + `X`, lalu `Y`, lalu `Enter`.

---

## 💡 Mengatasi Masalah Koneksi (Penting!) 💡

**Gejala:** Setelah menjalankan bot, bot tidak merespons atau langsung mati dengan pesan error seperti `Connection timed out`, `ConnectError`, atau `NetworkError`.

**Penyebab:** Kemungkinan besar, penyedia layanan internet (ISP) kamu memblokir akses langsung ke server Telegram. Ini sering terjadi di beberapa negara atau jaringan.

**Solusi:** Gunakan **Proxy**. Bot ini sudah dirancang untuk bisa berjalan lewat proxy dengan mudah.

### Cara Mengatur Proxy:

**1. Dapatkan Detail Proxy**

Cara termudah adalah dengan mendapatkannya dari channel Telegram seperti [@ProxyMTProto](https://t.me/ProxyMTProto).
   - Buka channel tersebut di aplikasi Telegram kamu.
   - Cari pesan yang berisi proxy **SOCKS5**.
   - Catat detailnya: **Server**, **Port**, **Username**, dan **Password**.

**2. Masukkan Detail Proxy ke File `.env`**

   - Buka kembali file `.env` dengan `nano .env`.
   - Kamu akan melihat baris `PROXY_URL=""`.
   - Isi baris tersebut dengan detail yang kamu dapatkan, dalam format berikut:
     ```
     PROXY_URL="socks5://<username>:<password>@<server>:<port>"
     ```
     **Contoh Nyata:**
     Misal kamu dapat detail:
     - Server: `proxy.mtproto.co`
     - Port: `1984`
     - Username: `user123`
     - Password: `pass456`

     Maka kamu harus mengisinya seperti ini:
     ```
     PROXY_URL="socks5://user123:pass456@proxy.mtproto.co:1984"
     ```
   - Simpan file (`Ctrl` + `X`, `Y`, `Enter`).

**3. Jalankan Ulang Bot**

Setelah proxy diatur, jalankan kembali bot (`./start.sh` atau `python bot.py`). Bot sekarang akan terhubung melalui proxy dan seharusnya bisa berjalan lancar!

---

## 🚀 Cara Menjalankan Bot 🚀

Kalau semua langkah di atas udah beres, sekarang tinggal nyalain botnya! Ada dua cara:

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

Terkadang, situs seperti TikTok atau YouTube mengubah cara kerja mereka, yang bisa membuat bot ini tiba-tiba gagal download dari link tertentu.

Kalau itu terjadi, solusinya adalah memperbarui "mesin" download bot ini (`yt-dlp`) ke versi paling baru, langsung dari sumbernya.

Caranya:
1.  Matikan bot (tekan `Ctrl` + `C`).
2.  Jalankan perintah di bawah ini di Termux:
    ```bash
    pip install --upgrade "https://github.com/yt-dlp/yt-dlp/archive/master.zip"
    ```
3.  Setelah selesai, nyalakan lagi botnya.

Ini akan memastikan bot kamu selalu punya versi `yt-dlp` yang paling canggih.