# 🤖 Bot Telegram Serbaguna untuk Termux 🤖

Halo! Ini adalah bot Telegram yang dibuat khusus untuk jalan di Termux. Bot ini bisa membantumu download macem-macem hal, mulai dari lagu sampai gambar.

## ✨ Fitur Keren Bot Ini ✨

*   **Unduh Apa Aja dari URL**: Tinggal kasih link (misalnya dari YouTube, Instagram, dll), nanti bot tanya mau dijadiin video atau audio.
*   **Cari Lagu di YouTube**:
    *   **Pencarian Biasa**: Cari judul lagu, nanti bot kasih 5 hasil terbaik (yang durasinya pendek, cocok buat lagu). Lengkap dengan gambar thumbnail dan tombol buat milih video atau audio.
    *   **Cari Cepat**: Pakai perintah `/caricepat`, ketik judul lagu, dan bot bakal langsung kirim file audionya. Gak pake lama!
*   **Cari Foto di Pinterest**: Mau cari gambar apa aja? Ketik kata kuncinya, nanti bot kirim 5 gambar paling top.

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
2.  Di dalemnya ada tulisan `YOUR_TOKEN_HERE`. Hapus tulisan itu dan ganti sama token bot kamu yang didapet dari [@BotFather](https://t.me/BotFather).
3.  Kalau udah, simpen filenya. Caranya: Tekan `Ctrl` + `X`, terus tekan `Y`, terus `Enter`.

---

## 🚀 Cara Menjalankan Bot 🚀

Kalau semua langkah di atas udah beres, sekarang tinggal nyalain botnya!

1.  Pastikan kamu ada di dalam folder botnya (`termux_telegram_bot`).
2.  Jalanin perintah ini:
    ```bash
    python bot.py
    ```

Selesai! Bot kamu sekarang udah online dan siap nerima perintah di Telegram. Kalau mau matiin botnya, tinggal tekan `Ctrl` + `C` di Termux. Selamat mencoba!