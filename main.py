from flask import Flask, request, jsonify
import datetime

app = Flask(__name__)

# План чтения Библии: день -> текст (Синодальный перевод, сокращённо для примера)
BIBLE = {
    "1": "В начале сотворил Бог небо и землю. Земля же была безвидна и пуста, и тьма над бездною, и Дух Божий носился над водою.",
    "2": "И сказал Бог: да будет твердь посреди воды, и да отделяет она воду от воды.",
    "3": "И сказал Бог: да произрастит земля зелень, траву, сеющую семя, дерево плодовитое.",
    "4": "И сказал Бог: да будут светила на тверди небесной, чтобы отделять день от ночи.",
    "5": "И сказал Бог: да произведет вода пресмыкающихся, душу живую; и птицы да полетят над землею.",
    # ... сюда можно добавить все 365 дней
}

START_DATE = datetime.date(2025, 1, 1)  # дата начала отсчёта

@app.route('/alice', methods=['POST'])
def alice():
    today = datetime.date.today()
    day_num = (today - START_DATE).days + 1
    total_days = len(BIBLE)
    day_key = str(((day_num - 1) % total_days) + 1)
    text = BIBLE.get(day_key, "Глава не найдена.")

    return jsonify({
        "version": request.json['version'],
        "session": request.json['session'],
        "response": {
            "text": f"День {day_num}. {text}",
            "tts": f"День {day_num}. {text}",
            "end_session": True
        }
    })

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
