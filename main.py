import os

from flask import Flask, request
import logging

import json


app = Flask(__name__)

# Устанавливаем уровень логирования
logging.basicConfig(level=logging.INFO)

sessionStorage = {}


@app.route('/post', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')

    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    handle_dialog(request.json, response)

    logging.info(f'Response:  {response!r}')

    # Преобразовываем в JSON и возвращаем
    return json.dumps(response)


def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:

        sessionStorage[user_id] = {
            'suggests': [
                "Не хочу.",
                "Не буду.",
                "Отстань!",
            ],
            'is_bought_elephant': False
        }

        res['response']['text'] = 'Привет! Купи слона!'

        res['response']['buttons'] = get_suggests(user_id)
        return

    for word in req['request']['original_utterance'].lower().split():
        if word in [
            'ладно',
            'куплю',
            'покупаю',
            'хорошо'
        ]:
            if sessionStorage[user_id]['is_bought_elephant']:
                res['response']['text'] = 'Кролика можно найти на Яндекс.Маркете!'
                res['response']['end_session'] = True
                return
            else:
                res['response']['text'] = 'Слона можно найти на Яндекс.Маркете! А что насчёт кролика?'
                sessionStorage[user_id]['is_bought_elephant'] = True
                res['response']['buttons'] = get_suggests(user_id)
                return

    if not sessionStorage[user_id]['is_bought_elephant']:
        res['response']['text'] = \
            f"Все говорят '{req['request']['original_utterance']}', а ты купи слона!"
        res['response']['buttons'] = get_suggests(user_id)
    else:
        res['response']['text'] = \
            f"Все говорят '{req['request']['original_utterance']}', а ты купи кролика!"
        res['response']['buttons'] = get_suggests(user_id)


def get_suggests(user_id):
    session = sessionStorage[user_id]

    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]

    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session

    if not sessionStorage[user_id]['is_bought_elephant']:
        if len(suggests) < 2:
            suggests.append({
                "title": "Ладно",
                "url": "https://market.yandex.ru/search?text=слон",
                "hide": True
            })
    else:
        if len(suggests) < 2:
            suggests.append({
                "title": "Ладно",
                "url": "https://market.yandex.ru/search?text=кролик",
                "hide": True
            })

    return suggests


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
