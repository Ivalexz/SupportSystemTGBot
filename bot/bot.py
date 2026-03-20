import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_API = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}'
API_URL = os.getenv('APP_API_URL', 'http://127.0.0.1:8000')

user_states: dict[int, dict] = {}
last_notification_ids: dict[int, set[int]] = {}


def send_message(chat_id: int, text: str) -> None:
    requests.post(f'{TELEGRAM_API}/sendMessage', json={'chat_id': chat_id, 'text': text})


def get_updates(offset: int | None = None) -> list:
    params = {'timeout': 20}
    if offset:
        params['offset'] = offset
    response = requests.get(f'{TELEGRAM_API}/getUpdates', params=params, timeout=25)
    return response.json().get('result', [])


def register_user(chat_id: int, username: str | None, full_name: str) -> None:
    requests.post(
        f'{API_URL}/users/register',
        json={
            'telegram_id': chat_id,
            'username': username,
            'full_name': full_name,
            'role': 'Client',
        },
        timeout=10,
    )


def get_user(chat_id: int) -> dict | None:
    response = requests.get(f'{API_URL}/users/by-telegram/{chat_id}', timeout=10)
    if response.status_code == 200:
        return response.json()
    return None


def handle_start(message: dict) -> None:
    chat_id = message['chat']['id']
    user = message.get('from', {})
    full_name = ' '.join(filter(None, [user.get('first_name'), user.get('last_name')])).strip() or 'Unknown User'
    register_user(chat_id, user.get('username'), full_name)
    send_message(
        chat_id,
        'Вітаю! Ти зареєстрований у системі заявок.\n\n'
        'Команди:\n'
        '/help - допомога\n'
        '/newrequest - створити заявку\n'
        '/myrequests - переглянути мої заявки\n'
        '/notifications - мої повідомлення',
    )


def handle_help(chat_id: int) -> None:
    send_message(
        chat_id,
        'Доступні команди:\n'
        '/start - запуск і реєстрація\n'
        '/help - список команд\n'
        '/newrequest - створення нової заявки\n'
        '/myrequests - перегляд своїх заявок\n'
        '/notifications - повідомлення про зміни статусу',
    )


def handle_new_request(chat_id: int) -> None:
    user_states[chat_id] = {'step': 'waiting_title'}
    send_message(chat_id, 'Введи назву заявки:')


def save_request(chat_id: int, title: str, description: str) -> None:
    response = requests.post(
        f'{API_URL}/requests',
        json={'telegram_id': chat_id, 'title': title, 'description': description},
        timeout=10,
    )
    if response.status_code == 200:
        req = response.json()['request']
        send_message(chat_id, f'Заявку створено ✅\nID: {req["id"]}\nСтатус: {req["status"]}')
    else:
        send_message(chat_id, 'Не вдалося створити заявку. Спочатку виконай /start')


def handle_my_requests(chat_id: int) -> None:
    response = requests.get(f'{API_URL}/requests/user/{chat_id}', timeout=10)
    if response.status_code != 200:
        send_message(chat_id, 'Користувача не знайдено. Виконай /start')
        return

    requests_data = response.json().get('requests', [])
    if not requests_data:
        send_message(chat_id, 'У тебе поки немає заявок.')
        return

    lines = ['Твої заявки:']
    for item in requests_data:
        lines.append(
            f"ID: {item['id']} | {item['title']}\nСтатус: {item['status']}\nОпис: {item['description']}"
        )
    send_message(chat_id, '\n\n'.join(lines))


def handle_notifications(chat_id: int) -> None:
    response = requests.get(f'{API_URL}/notifications/{chat_id}', timeout=10)
    if response.status_code != 200:
        send_message(chat_id, 'Повідомлень немає.')
        return

    notifications = response.json().get('notifications', [])
    if not notifications:
        send_message(chat_id, 'Нових повідомлень немає.')
        return

    lines = ['Останні повідомлення:']
    for item in notifications[:10]:
        lines.append(
            f"Заявка #{item['request_id']} | статус: {item.get('status', '-') }\n{item['text']}"
        )
    send_message(chat_id, '\n\n'.join(lines))


def push_new_notifications(chat_id: int) -> None:
    response = requests.get(f'{API_URL}/notifications/{chat_id}', timeout=10)
    if response.status_code != 200:
        return
    notifications = response.json().get('notifications', [])
    known = last_notification_ids.setdefault(chat_id, set())
    fresh = [n for n in notifications if n['id'] not in known]
    for item in reversed(fresh):
        send_message(
            chat_id,
            f"🔔 Оновлення по заявці #{item['request_id']}\nСтатус: {item.get('status', '-') }\n{item['text']}",
        )
        known.add(item['id'])


def handle_text_message(message: dict) -> None:
    chat_id = message['chat']['id']
    text = message.get('text', '').strip()

    if text == '/start':
        handle_start(message)
        return
    if text == '/help':
        handle_help(chat_id)
        return
    if text == '/newrequest':
        handle_new_request(chat_id)
        return
    if text == '/myrequests':
        handle_my_requests(chat_id)
        return
    if text == '/notifications':
        handle_notifications(chat_id)
        return

    state = user_states.get(chat_id)
    if not state:
        send_message(chat_id, 'Невідома команда. Використай /help')
        return

    if state['step'] == 'waiting_title':
        state['title'] = text
        state['step'] = 'waiting_description'
        send_message(chat_id, 'Тепер введи опис заявки:')
        return

    if state['step'] == 'waiting_description':
        title = state['title']
        description = text
        save_request(chat_id, title, description)
        user_states.pop(chat_id, None)
        return


def poll_notifications_for_known_users() -> None:
    for chat_id in list(last_notification_ids.keys()):
        try:
            push_new_notifications(chat_id)
        except Exception:
            pass


def main() -> None:
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError('TELEGRAM_BOT_TOKEN is not set in .env')

    offset = None
    while True:
        try:
            updates = get_updates(offset)
            for update in updates:
                offset = update['update_id'] + 1
                message = update.get('message')
                if not message or 'text' not in message:
                    continue
                chat_id = message['chat']['id']
                last_notification_ids.setdefault(chat_id, set())
                handle_text_message(message)
            poll_notifications_for_known_users()
        except Exception as e:
            print('Bot error:', e)
            time.sleep(3)


if __name__ == '__main__':
    main()
