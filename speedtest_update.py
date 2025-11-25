import os
import datetime
import subprocess

def get_speed():
    try:
        result = subprocess.run(["speedtest-cli", "--simple"], capture_output=True, text=True, timeout=30)
        lines = [line for line in result.stdout.splitlines() if line]
        # Ожидается минимум 3 строки: Ping, Download, Upload
        if len(lines) < 3 or not lines[0].startswith('Ping'):
            raise ValueError("speedtest-cli output is invalid or speedtest failed:\n" + result.stdout)
        ping = float(lines[0].split()[1])
        download = float(lines[1].split()[1])
        upload = float(lines[2].split()[1])
        return ping, download, upload
    except Exception as e:
        # При ошибке возвращаем None — в таблицу не записываем
        print(f"Speedtest error: {e}")
        return None, None, None

def speed_icon(speed):
    if speed is None:
        return "⚪️"
    if speed > 1000:
        return "🔵"
    elif speed > 500:
        return "🟢"
    elif speed > 100:
        return "🟡"
    else:
        return "🟠"

def append_readme(ping, download, upload):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    icon = speed_icon(download)
    if download is None:
        download_field = upload_field = ping_field = "-"
    else:
        download_field = f"{download:.1f} Мбит/с"
        upload_field = f"{upload:.1f} Мбит/с"
        ping_field = f"{ping:.1f} ms"
    line = f"| {now} | {icon} | {download_field} | {upload_field} | {ping_field} |\n"

    with open("README.md", "r+", encoding='utf-8') as f:
        content = f.read()
        if "| Время | Статус | Download | Upload | Ping |" not in content:
            header = (
                "# Интернет-замер\n\n"
                "Утилита — speedtest-cli\n\n"
                "| Время | Статус | Download | Upload | Ping |\n"
                "|---|---|---|---|---|\n"
            )
            content = header + content
        # Находим место вставки после header таблицы
        table_start = content.find("| Время |")
        table_end = content.find("\n", table_start) + 1
        before_table = content[:table_end]
        after_table = content[table_end:]
        new_content = before_table + line + after_table
        f.seek(0)
        f.write(new_content)
        f.truncate()

ping, download, upload = get_speed()
if download is not None:
    append_readme(ping, download, upload)
else:
    print("Speedtest failed; result not appended.")
