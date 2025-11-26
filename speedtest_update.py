import datetime
import subprocess
import re
from zoneinfo import ZoneInfo  # Для работы с часовыми поясами

def get_speed():
    try:
        result = subprocess.run(
            ["speedtest-cli", "--simple"],
            capture_output=True, text=True, timeout=30
        )
        lines = [x for x in result.stdout.splitlines() if x]
        if len(lines) != 3 or not all(k in lines[i] for i, k in enumerate(['Ping', 'Download', 'Upload'])):
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

def format_log_line(ping, download, upload, error_message=None):
    # Указываем московский часовой пояс
    msk_timezone = ZoneInfo("Europe/Moscow")
    now = datetime.datetime.now(msk_timezone).strftime("%Y-%m-%d %H:%M:%S")
    icon = speed_icon(download)
    download_field = f"{download:.2f} Мбит/с" if download is not None else "-"
    upload_field = f"{upload:.2f} Мбит/с" if upload is not None else "-"
    ping_field = f"{ping:.2f} ms" if ping is not None else "-"
    return f"| {now} | {icon} | {download_field} | {upload_field} | {ping_field} |"

def update_history_in_readme(log_line):
    start_marker = '<!-- SPEEDTEST_HISTORY_START -->'
    end_marker = '<!-- SPEEDTEST_HISTORY_END -->'
    with open("README.md", "r+", encoding='utf-8') as f:
        content = f.read()
        # Находим существующую историю между маркерами
        pattern = re.compile(
            rf"({start_marker}\n)(.*?)(\n{end_marker})",
            re.DOTALL
        )
        match = pattern.search(content)
        if not match:
            raise Exception("Markers not found properly in README.md")
        history = match.group(2).strip()
        # Если история отсутствует, делаем заголовки таблицы
        if history.startswith("*(история") or not history:
            history = (
                "| Время | Статус | Download | Upload | Ping |\n"
                "|---|---|---|---|---|\n"
            )
        # Гарантируем перенос строки перед добавлением
        if not history.endswith('\n'):
            history += '\n'
        history += log_line + "\n"
        # Собираем новый README c правильными маркерами
        new_readme = (
            content[:match.start(1) + len(start_marker) + 1] +
            history +
            content[match.end(2):]
        )
        f.seek(0)
        f.write(new_readme)
        f.truncate()

ping, download, upload, error = get_speed()
log_line = format_log_line(ping, download, upload, error)
update_history_in_readme(log_line)
