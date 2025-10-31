from flask import Flask, request, jsonify
import datetime
import json
import re
import os

app = Flask(__name__)

# Загружаем данные из файла
with open('bible_365.json', 'r', encoding='utf-8') as f:
    BIBLE = json.load(f)

# Дата начала отсчёта
START_DATE = datetime.date(2025, 1, 1)

# Сопоставление разговорных форм с полными названиями
BOOK_ALIASES = {
    'матфея': 'Евангелие от Матфея',
    'марка': 'Евангелие от Марка',
    'луки': 'Евангелие от Луки',
    'иоанна': 'Евангелие от Иоанна',
}

def find_chapter_by_request(query):
    """Ищет главу по фразе вроде 'глава 5 от марка' или 'Евангелие от Луки, глава 3'."""
    query = query.lower()

    # Ищем номер главы
    chapter_match = re.search(r'глава\s+(\d+)|главу\s+(\d+)', query)
    if not chapter_match:
        return None
    chapter_num = chapter_match.group(1) or chapter_match.group(2)

    # Ищем евангелиста
    book_key = None
    for alias, full_name in BOOK_ALIASES.items():
        if alias in query:
            book_key = full_name
            break

    if not book_key:
        return None

    # Формируем ожидаемое начало главы
    target_prefix = f"{book_key}, глава {chapter_num}."
    for key, text in BIBLE.items():
        if text.startswith(target_prefix):
            return key
    return None

def format_tts(text, use_voice=True):
    if use_voice:
        return f'<speaker voice="omazh">{text}</speaker>'
    return text

@app.route('/alice', methods=['POST'])
def alice():
    req = request.json
    command = req['request']['original_utterance'].lower().strip()
    session = req['session']

    # Команды для сегодняшнего чтения
    if any(phrase in command for phrase in [
        "почитай библию",
        "прочитай библию",
        "продолжи чтение библии",
        "сегодня читаем библию"
    ]):
        # === СПОСОБ ОПРЕДЕЛЕНИЯ ДНЯ ===
        day_num = (datetime.date.today() - START_DATE).days + 1
        day_key = str(((day_num - 1) % 100) + 1)
        text = BIBLE.get(day_key, "Сегодняшняя глава не найдена.")
        response_text = f"Сегодня {day_num}-й день чтения. {text}"
        tts = format_tts(response_text)

    elif "прочитай" in command or "глава" in command:
        found_key = find_chapter_by_request(command)
        if found_key:
            text = BIBLE[found_key]
            response_text = f"Читаю: {text}"
            tts = format_tts(response_text)
        else:
            response_text = (
                "Извините, я не нашла такую главу. Скажите, например: "
                "«Прочитай главу 5 от Марка» или «Евангелие от Луки, глава 3»."
            )
            tts = format_tts(response_text)

    else:
        response_text = (
            "Скажите: «Почитай Библию» — чтобы услышать сегодняшнюю главу, "
            "или «Прочитай главу 5 от Марка» — чтобы выбрать конкретную главу."
        )
        tts = format_tts(response_text)

    return jsonify({
        "version": req['version'],
        "session": session,
        "response": {
            "text": response_text,
            "tts": tts,
            "end_session": True
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
