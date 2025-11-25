import os
import datetime
import subprocess

def get_speed():
    result = subprocess.run(
        ["speedtest-cli", "--simple"],
        capture_output=True, text=True)
    lines = result.stdout.splitlines()
    ping = float(lines[0].split()[1])
    download = float(lines[1].split()[1])
    upload = float(lines[2].split()[1])
    return ping, download, upload

def speed_icon(speed):
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
    line = f"| {now} | {icon} | {download:.1f} Мбит/с | {upload:.1f} Мбит/с | {ping:.1f} ms |\n"

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
        # вставляем после последней строки таблицы
        idx = content.rfind("|")
        table_start = content.find("| Время |")
        table_end = content.find("\n", table_start) + 1
        before_table = content[:table_end]
        after_table = content[table_end:]
        new_content = before_table + line + after_table
        f.seek(0)
        f.write(new_content)
        f.truncate()

ping, download, upload = get_speed()
append_readme(ping, download, upload)

