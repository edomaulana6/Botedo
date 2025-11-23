import asyncio
import os
import shlex

async def run_subprocess(command, bot, chat_id, status_message, success_msg=""):
    """
    Menjalankan perintah shell, menangani error, dan memberikan umpan balik minimal.
    """
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        error_output = stderr.decode('utf-8', 'ignore').strip()
        raise Exception(f"Perintah gagal dengan kode {process.returncode}:\n{error_output}")

    if success_msg:
        await bot.edit_message_text(chat_id=chat_id, message_id=status_message.message_id, text=success_msg)

    return stdout.decode('utf-8', 'ignore').strip()

async def install_pterodactyl(user_data, bot, chat_id, status_message):
    """
    Menggunakan perintah sistem (sshpass, sftp, ssh) untuk mengunggah dan menjalankan skrip instalasi.
    """
    ip = user_data.get('ptero_ip')
    user = user_data.get('ptero_user')
    password = shlex.quote(user_data.get('ptero_pass'))

    local_scripts_dir = 'termux_telegram_bot/scripts'
    remote_base_dir = '/tmp/pterodactyl_installer'

    ssh_opts = "-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"
    sshpass_prefix = f"sshpass -p {password}"

    try:
        await run_subprocess(
            f"{sshpass_prefix} ssh {ssh_opts} {user}@{ip} 'mkdir -p {remote_base_dir}'",
            bot, chat_id, status_message, "✅ Terhubung ke VPS. Membuat direktori remote..."
        )

        sftp_batch_file = f'put -r {local_scripts_dir}/* {remote_base_dir}/'
        await run_subprocess(
            f"{sshpass_prefix} sftp {ssh_opts} {user}@{ip} -b <(echo \"{sftp_batch_file}\")",
            bot, chat_id, status_message, "✅ Direktori dibuat. Mengunggah skrip instalasi..."
        )

        await bot.edit_message_text(chat_id=chat_id, message_id=status_message.message_id, text="✅ Skrip diunggah. Memulai instalasi Panel...")

        # --- Instalasi Panel ---
        export_vars = (
            f"export FQDN='{user_data.get('ptero_fqdn')}';"
            f"export email='{user_data.get('ptero_email')}';"
            f"export user_email='{user_data.get('ptero_email')}';"
            f"export user_username='{user_data.get('ptero_admin_user')}';"
            f"export user_password='{user_data.get('ptero_admin_pass')}';"
            f"export user_firstname='{user_data.get('ptero_admin_fname')}';"
            f"export user_lastname='{user_data.get('ptero_admin_lname')}';"
            f"export CONFIGURE_LETSENCRYPT='{'true' if user_data.get('ptero_ssl') else 'false'}';"
            f"export CONFIGURE_FIREWALL='true';"
            f"export ASSUME_SSL='false';"
        )

        panel_cmd = f"bash {remote_base_dir}/ui/panel.sh"
        full_panel_cmd = f"{sshpass_prefix} ssh {ssh_opts} {user}@{ip} \"{export_vars} {panel_cmd}\""

        asyncio.create_task(asyncio.create_subprocess_shell(full_panel_cmd))

        await bot.edit_message_text(chat_id=chat_id, message_id=status_message.message_id,
                                    text="⏳ **Instalasi Panel telah dimulai di latar belakang.**\n\n"
                                         "Ini akan memakan waktu 15-30 menit. Silakan pantau log di VPS Anda.")

        # --- Instalasi Wings (jika dipilih) ---
        if user_data.get('install_wings'):
            await asyncio.sleep(5)
            await bot.send_message(chat_id=chat_id, text="⏳ **Memulai instalasi Wings di latar belakang...**")

            wings_export_vars = (
                f"export FQDN='{user_data.get('ptero_fqdn')}';"
                f"export CONFIGURE_FIREWALL='true';"
                f"export CONFIGURE_LETSENCRYPT='{'true' if user_data.get('ptero_ssl') else 'false'}';"
                f"export WINGS_CPU={user_data.get('wings_cpu')};"
                f"export WINGS_RAM={user_data.get('wings_ram')};"
                f"export WINGS_SWAP=0;"
            )
            wings_cmd = f"bash {remote_base_dir}/ui/wings.sh"
            full_wings_cmd = f"{sshpass_prefix} ssh {ssh_opts} {user}@{ip} \"{wings_export_vars} {wings_cmd}\""

            asyncio.create_task(asyncio.create_subprocess_shell(full_wings_cmd))

        final_message = "✅ **Perintah instalasi telah berhasil dikirim!**\n\n" \
                        "Proses berjalan di latar belakang VPS Anda. Periksa kembali dalam 30 menit."

        await asyncio.sleep(10)
        await bot.send_message(chat_id=chat_id, text=final_message)

    except Exception as e:
        await bot.edit_message_text(chat_id=chat_id, message_id=status_message.message_id, text=f"❌ **Terjadi Kesalahan:**\n`{str(e)}`", parse_mode='Markdown')
    finally:
        try:
            await run_subprocess(f"{sshpass_prefix} ssh {ssh_opts} {user}@{ip} 'rm -rf {remote_base_dir}'", bot, chat_id, status_message)
        except:
            pass
