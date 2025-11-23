import paramiko
import asyncio
import os

def upload_dir_recursive(sftp, local_path, remote_path):
    """
    Mengunggah direktori secara rekursif dari local_path ke remote_path menggunakan SFTP.
    """
    try:
        sftp.mkdir(remote_path)
    except IOError:
        pass

    for item in os.listdir(local_path):
        local_item_path = os.path.join(local_path, item)
        remote_item_path = os.path.join(remote_path, item)

        if os.path.isfile(local_item_path):
            sftp.put(local_item_path, remote_item_path)
        else:
            sftp.mkdir(remote_item_path)
            upload_dir_recursive(sftp, local_item_path, remote_item_path)

async def execute_remote_command(client, command, bot, chat_id, status_message):
    """Mengeksekusi perintah di server remote dan mengirimkan output secara real-time."""
    stdin, stdout, stderr = client.exec_command(command, get_pty=True)

    last_update_text = ""
    while not stdout.channel.exit_status_ready():
        if stdout.channel.recv_ready():
            line = stdout.channel.recv(1024).decode('utf-8', 'ignore')
            if "TASK" in line or "..." in line or "INFO" in line:
                current_status_text = f"⚙️ **Proses:**\n`{line.strip()}`"
                if current_status_text != last_update_text:
                    try:
                        await bot.edit_message_text(
                            chat_id=chat_id, message_id=status_message.message_id,
                            text=current_status_text, parse_mode='Markdown'
                        )
                        last_update_text = current_status_text
                    except Exception:
                        pass
        await asyncio.sleep(2)

    return stdout.channel.recv_exit_status()

async def install_pterodactyl(user_data, bot, chat_id, status_message):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ip = user_data.get('ptero_ip')
    user = user_data.get('ptero_user')
    password = user_data.get('ptero_pass')

    local_scripts_dir = 'termux_telegram_bot/scripts'
    remote_base_dir = '/tmp/pterodactyl_installer'

    try:
        await asyncio.to_thread(client.connect, hostname=ip, username=user, password=password, timeout=20)

        await bot.edit_message_text(chat_id=chat_id, message_id=status_message.message_id, text="✅ Terhubung. Mengunggah skrip instalasi...")

        sftp = await asyncio.to_thread(client.open_sftp)
        await asyncio.to_thread(upload_dir_recursive, sftp, local_scripts_dir, remote_base_dir)
        sftp.close()

        await bot.edit_message_text(chat_id=chat_id, message_id=status_message.message_id, text="✅ Skrip diunggah. Memulai instalasi Panel...")

        # --- Instalasi Panel ---
        export_vars = (
            f"export FQDN='{user_data.get('ptero_fqdn')}'\n"
            f"export email='{user_data.get('ptero_email')}'\n"
            f"export user_email='{user_data.get('ptero_email')}'\n"
            f"export user_username='{user_data.get('ptero_admin_user')}'\n"
            f"export user_password='{user_data.get('ptero_admin_pass')}'\n"
            f"export user_firstname='{user_data.get('ptero_admin_fname')}'\n"
            f"export user_lastname='{user_data.get('ptero_admin_lname')}'\n"
            f"export CONFIGURE_LETSENCRYPT='{'true' if user_data.get('ptero_ssl') else 'false'}'\n"
            f"export CONFIGURE_FIREWALL='true'\n"
            f"export ASSUME_SSL='false'\n"
        )

        panel_cmd = f"{export_vars}\nbash {remote_base_dir}/ui/panel.sh"
        panel_exit_code = await execute_remote_command(client, panel_cmd, bot, chat_id, status_message)

        if panel_exit_code != 0:
            raise Exception(f"Instalasi Panel gagal dengan kode error: {panel_exit_code}")

        # --- Instalasi Wings (jika dipilih) ---
        if user_data.get('install_wings'):
            await bot.edit_message_text(chat_id=chat_id, message_id=status_message.message_id, text="✅ Panel selesai. Memulai instalasi Wings...")

            wings_export_vars = (
                f"export CONFIGURE_FIREWALL='true'\n"
                f"export CONFIGURE_LETSENCRYPT='{'true' if user_data.get('ptero_ssl') else 'false'}'\n"
                f"export FQDN='{user_data.get('ptero_fqdn')}'\n"
                f"export WINGS_CPU={user_data.get('wings_cpu')}\n"
                f"export WINGS_RAM={user_data.get('wings_ram')}\n"
                f"export WINGS_SWAP=0\n"
            )

            wings_cmd = f"{wings_export_vars}\nbash {remote_base_dir}/ui/wings.sh"
            wings_exit_code = await execute_remote_command(client, wings_cmd, bot, chat_id, status_message)

            if wings_exit_code != 0:
                raise Exception(f"Instalasi Wings gagal dengan kode error: {wings_exit_code}")

        final_message = "✅ **Instalasi Selesai!** Panel dan/atau Wings telah berhasil diinstal."
        await bot.edit_message_text(chat_id=chat_id, message_id=status_message.message_id, text=final_message, parse_mode='Markdown')

    except Exception as e:
        await bot.edit_message_text(chat_id=chat_id, message_id=status_message.message_id, text=f"❌ **Terjadi Kesalahan:**\n`{str(e)}`", parse_mode='Markdown')
    finally:
        # Bersihkan direktori remote
        try:
            client.exec_command(f"rm -rf {remote_base_dir}")
        except:
            pass
        if client.get_transport() and client.get_transport().is_active():
            client.close()
