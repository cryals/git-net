import datetime
import subprocess

def get_speed():
    try:
        result = subprocess.run(["speedtest-cli", "--simple"], capture_output=True, text=True, timeout=30)
        lines = [x for x in result.stdout.splitlines() if x]
        if len(lines) != 3 or not all(k in lines[i] for i, k in enumerate(['Ping', 'Download', 'Upload'])):
            # неверный результат, вернуть как ошибку
            return None, None, None, result.stdout.strip() or "NO OUTPUT"
        ping = float(lines[0].split()[1])
        download = float(lines[1].split()[1])
        upload = float(lines[2].split()[1])
        return ping, download, upload, None
    except Exception as e:
        return None, None, None, str(e)

def speed_icon(speed):
    if speed is None:
        return "⚪️"
    elif speed > 1000:
        return "🔵"
    elif speed > 500:
        return "🟢"
    elif speed > 100:
        return "🟡"
    else:
        return "🟠"

def append_readme(ping, download, upload, error_message=None):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    icon = speed_icon(download)
    download_field = f"{download:.2f} Мбит/с" if download else "-"
    upload_field = f"{upload:.2f} Мбит/с" if upload else "-"
    ping_field = f"{ping:.2f} ms" if ping else "-"
    error_note = f"{error_message}" if error_message else ""
    line = f"| {now} | {icon} | {download_field} | {upload_field} | {ping_field} | {error_note} |\n"

    with open("README.md", "r+", encoding='utf-8') as f:
        content = f.read()
        if "| Время | Статус | Download | Upload | Ping |" not in content:
            header = (
                "# Интернет-замер\n\n"
                "Утилита — speedtest-cli\n\n"
                "| Время | Статус | Download | Upload | Ping | Примечание |\n"
                "|---|---|---|---|---|---|\n"
            )
            content = header + content
        table_start = content.find("| Время |")
        table_end = content.find("\n", table_start) + 1
        before_table = content[:table_end]
        after_table = content[table_end:]
        new_content = before_table + line + after_table
        f.seek(0)
        f.write(new_content)
        f.truncate()

ping, download, upload, error = get_speed()
append_readme(ping, download, upload, error)
