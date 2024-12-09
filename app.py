from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from datetime import timedelta
from datetime import datetime
from flask import flash, redirect, url_for
from flask import flash

app = Flask(__name__)
app.secret_key = 'MyVerySecretKey12345!'  # Для работы с сессиями

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,   # Запрещает доступ к кукам JavaScript
    SESSION_COOKIE_SECURE=True,     # Используется только с HTTPS
    PERMANENT_SESSION_LIFETIME=timedelta(days=7),  # Время жизни сессии (например, 7 дней)
    SESSION_COOKIE_SAMESITE='Strict',  # Защита от CSRF-атак
)

# Функция для подключения к базе данных
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row  # Для удобства работы с результатами
    return conn

# Главная страница с формой входа
@app.route('/')
def index():
    if 'user_id' in session:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],))
        student = cursor.fetchone()

        if student['role'] == 'admin':
            return redirect(url_for('admin_panel'))  # Для админа
        else:
            return redirect(url_for('student_profile', user_id=session['user_id']))  # Профиль ученика
    return render_template('login.html')  # Ваш HTML файл формы

# Обработка формы входа
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        # Сохраняем id и время начала сессии
        session['user_id'] = user['id']
        session['session_start'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Формат времени

        if user['role'] == 'admin':
            return redirect(url_for('admin_panel'))  # Для админа
        else:
            return redirect(url_for('student_profile', user_id=user['id']))  # Профиль ученика
    else:
        flash("Неверный логин или пароль", 'error')
        return redirect(url_for('index'))  # Перенаправляем обратно на страницу логина

@app.route('/profile')
def profile():
    # Проверяем, что пользователь авторизован (например, через сессии)
    if 'user_id' not in session:
        return redirect(url_for('index'))  # Перенаправляем на страницу логина, если не авторизован

    user_id = session['user_id']

    # Получаем данные пользователя из базы данных по его ID
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()  # Получаем первого пользователя (он должен быть единственным)
    conn.close()

    if user:
        # Передаем данные пользователя в шаблон
        return render_template('profile.html', users=user)
    else:
        return redirect(url_for('index'))  # Перенаправляем, если пользователь не найден

# Страница для админа
# Страница для админа
@app.route('/admin_panel')
def admin_panel():
    if 'user_id' not in session:
        return redirect(url_for('index'))  # Перенаправляем на страницу логина, если не авторизован

    conn = get_db_connection()
    cursor = conn.cursor()

    # Получаем текущего пользователя
    user_id = session['user_id']
    cursor.execute("SELECT full_name, avatar, role, id FROM users WHERE id = ?", (user_id,))
    current_user = cursor.fetchone()
    conn.close()
    
    if current_user['role'] != 'admin':
        return redirect(url_for('index'))

    # Статус сессии
    session_status = 'Открыта' if 'user_id' in session else 'Закрыта'

    # Расчет продолжительности сессии
    session_duration = calculate_session_duration(session['session_start']) if 'session_start' in session else 'Неизвестно'

    # Выводим статус сессии и продолжительность
    print(f"Статус сессии: {session_status} (Админ), Продолжительность: {session_duration}")

    # Передаем id_user в шаблон
    return render_template('admin_panel.html', current_user=current_user, session_status=session_status, session_duration=session_duration, id_user=current_user['id'])

# Маршрут для управления пользователями
@app.route('/admin/users')
def manage_users():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Получаем список пользователей из базы данных
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()

    return render_template('manage_users.html', users=users)

@app.route('/admin/users/add', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        # Получаем данные из формы
        username = request.form['username']
        password = request.form['password']
        full_name = request.form['full_name']
        role = request.form['role']
        group = request.form.get('group', '')  # Группа может быть пустой
        teacher_name = request.form.get('teacher_name', '')  # Учитель может быть пустым
        avatar = request.form.get('avatar', '')  # Аватар может быть пустым
        age = request.form.get('age')  # Возраст теперь может быть пустым

        # Проверка на пустое поле возраста (если возраст не указан, то None)
        if not age:
            age = None

        # Подключение к базе данных и добавление пользователя
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO users (username, password, full_name, role, class, class_teacher, avatar, age)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (username, password, full_name, role, group, teacher_name, avatar, age))
            conn.commit()
            flash('Пользователь успешно добавлен!', 'success')  # Сообщение об успешном добавлении
        except sqlite3.Error as e:
            flash(f'Ошибка при добавлении пользователя: {e}', 'error')  # Сообщение об ошибке

        conn.close()
        return redirect(url_for('add_user'))  # Перенаправление на страницу добавления

    return render_template('add_user.html')  # Отображаем страницу добавления пользователя

@app.route('/admin/users/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Получаем данные пользователя
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()

    # Получаем список администраторов
    cursor.execute("SELECT * FROM users WHERE role = 'admin'")
    admins = cursor.fetchall()

    if request.method == 'POST':
        try:
            # Получаем данные из формы
            username = request.form['username']
            password = request.form['password']
            full_name = request.form['full_name']
            role = request.form['role']
            group = request.form['group']
            teacher_name = request.form['teacher_name']
            avatar = request.form['avatar']

            # Обновляем данные пользователя
            cursor.execute("""
                UPDATE users SET username = ?, password = ?, full_name = ?, role = ?, class = ?, class_teacher = ?, avatar = ?
                WHERE id = ?
            """, (username, password, full_name, role, group, teacher_name, avatar, user_id))

            # Сохраняем изменения в базе данных
            conn.commit()

            # Отправляем уведомление об успешном обновлении
            flash('Данные пользователя успешно обновлены!', 'success')

        except Exception as e:
            # В случае ошибки отправляем уведомление об ошибке
            flash(f'Ошибка при обновлении данных пользователя: {e}', 'error')
            conn.rollback()  # Откатываем транзакцию в случае ошибки

        # Закрываем соединение с базой данных
        conn.close()

        # Рендерим шаблон с уведомлением
        return redirect(url_for('edit_user', user_id=user_id))

    # В случае GET-запроса рендерим форму для редактирования
    return render_template('edit_user.html', user=user, admins=admins)

@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Удаляем пользователя из базы
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

    flash('Пользователь удалён!', 'success')
    return redirect(url_for('manage_users'))  # Перенаправляем на страницу управления пользователями

# Страница профиля ученика
@app.route('/student/<int:user_id>')
def student_profile(user_id):
    if 'user_id' not in session:
        return redirect(url_for('index'))  # Перенаправляем на страницу логина, если не авторизован

    conn = get_db_connection()
    cursor = conn.cursor()

    # Получаем данные ученика
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    student = cursor.fetchone()

    # Статус сессии
    session_status = 'Открыта' if 'user_id' in session else 'Закрыта'

    # Расчет продолжительности сессии
    session_duration = calculate_session_duration(session['session_start']) if 'session_start' in session else 'Неизвестно'

    # Выводим статус сессии и продолжительность
    print(f"Статус сессии: {session_status} (Студент), Продолжительность: {session_duration}")

    return render_template('student_profile.html', student=student, session_status=session_status, session_duration=session_duration)

# Логика для выхода
@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Удаляем user_id из сессии
    flash('Вы успешно вышли из системы', 'info')  # Показываем сообщение об успешном выходе
    return redirect(url_for('index'))  # Перенаправляем на страницу логина

def calculate_session_duration(start_time):
    session_start = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
    now = datetime.now()
    duration = now - session_start
    return str(duration).split('.')[0]  # Убираем миллисекунды

@app.route('/session_duration')
def session_duration():
    if 'session_start' in session:
        session_start = session['session_start']
        session_duration = calculate_session_duration(session_start)
        return session_duration
    return "Неизвестно"

@app.route('/conference/<int:user_id>', methods=['GET'])
def conference(user_id):
    if 'user_id' not in session:
        return redirect(url_for('index'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        flash("Пользователь не найден", "error")
        return redirect(url_for('index'))

    # Передаем user_id как id_user
    return render_template(
        'conference.html',
        room_name=f"room-{user['username']}",
        user_name=user['full_name'],
        id_user=user['id']  # Здесь передаем id_user
    )

if __name__ == '__main__':
    app.run(debug=True)
