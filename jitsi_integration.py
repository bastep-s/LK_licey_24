# jitsi_integration.py

from flask import Flask, render_template, request
import uuid

app = Flask(__name__)

@app.route('/conference/<int:user_id>')
def conference(user_id):
    # Генерация уникальной комнаты для каждой конференции
    room_name = str(uuid.uuid4())  # Генерируем уникальный ID для комнаты

    # Получаем имя пользователя (или данные из базы данных)
    # Для примера предполагаем, что у вас есть функция get_user_by_id
    user = get_user_by_id(user_id)  # Функция, которая извлекает данные пользователя из базы данных

    # Передаем уникальное имя комнаты и информацию о пользователе в шаблон
    return render_template('conference.html', room_name=room_name, user=user)

def get_user_by_id(user_id):
    # Пример получения данных пользователя из базы данных
    # Верните объект пользователя, который содержит его имя и другие данные
    return {'id': user_id, 'name': 'User_' + str(user_id)}

if __name__ == '__main__':
    app.run(debug=True)
