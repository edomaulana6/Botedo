# Termux Telegram Downloader Bot

This is a Telegram bot designed to run on Termux. It can download videos/audio from URLs, search for music on YouTube, and find images on Pinterest.

## Features

-   **Download from URL**: Paste any supported URL (like YouTube, Instagram, etc.) and choose to download as video or audio.
-   **Search YouTube (Top 5)**: Search for songs on YouTube to get the top 5 results with thumbnails, allowing you to choose video or audio for download.
-   **Quick Search YouTube (Top 1)**: Use the `/caricepat` command to instantly search for a song and receive the top result as an audio file.
-   **Search Pinterest**: Find the top 5 images for any keyword and receive them in a media group.

## Installation on Termux

1.  **Update Packages:**
    ```bash
    pkg update && pkg upgrade
    ```

2.  **Install Dependencies:**
    ```bash
    # Install Python, Git, and FFmpeg
    pkg install python git ffmpeg
    ```

3.  **Clone the Repository:**
    *(Replace `<repository_url>` with the actual URL if you clone it from a git repo)*
    ```bash
    git clone <repository_url>
    cd termux_telegram_bot
    ```
    *If you downloaded the files directly, just navigate to the directory.*

4.  **Install Python Libraries:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Set Up Your Bot Token:**
    -   Open the `.env` file using a text editor like `nano`:
        ```bash
        nano .env
        ```
    -   Replace `YOUR_TOKEN_HERE` with your actual Telegram bot token obtained from [@BotFather](https://t.me/BotFather).
    -   Save the file by pressing `Ctrl+X`, then `Y`, and then `Enter`.

## How to Run

1.  Navigate to the bot's directory:
    ```bash
    cd /path/to/termux_telegram_bot
    ```
2.  Start the bot with this command:
    ```bash
    python bot.py
    ```
3.  The bot is now running! You can interact with it on Telegram. To stop it, press `Ctrl+C` in the Termux session.