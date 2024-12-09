import sqlite3

# Подключаемся к базе данных (или создаем ее, если она не существует)
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Обновленная таблица пользователей с дополнительными данными
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    full_name TEXT NOT NULL,
    age INTEGER NOT NULL,
    role TEXT CHECK(role IN ('admin', 'student')) NOT NULL,
    class TEXT NOT NULL,
    class_teacher TEXT NOT NULL
)
''')

# Пример добавления пользователей (админ и ученик)
cursor.execute("INSERT INTO users (username, password, full_name, age, role, class, class_teacher) VALUES (?, ?, ?, ?, ?, ?, ?)", 
               ('admin', 'admin_password', 'Иван Иванов', 40, 'admin', '10А', 'Петрова И.С.'))

cursor.execute("INSERT INTO users (username, password, full_name, age, role, class, class_teacher) VALUES (?, ?, ?, ?, ?, ?, ?)", 
               ('student1', 'student_password', 'Алексей Смирнов', 16, 'student', '10А', 'Петрова И.С.'))

# Сохраняем изменения и закрываем подключение
conn.commit()
conn.close()
