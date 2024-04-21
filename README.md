# Телеграм бот, где можно прочитать книгу Толкина Дж. Р. Р. - Хоббит - Перевод А. Грузберга (но по тексту Гандалв заменено на Гэндальф)

Команды:

/start - запустить бота.

/help - справка по использованию.

/beginning - перейти в начало книги.

/continue - продолжить чтение.

/bookmarks - список закладок.

Читая книгу можно добавлять закладки, нажимая на кнопку текущей страницы.
Бот использует базу данных PostgreeSQL для хранения книг пользователей.
При каждом перезапуске бота стираются все данные из базы данных (если были) и заполняются необходимые для работы бота таблицы.


# Зависимости 

    Python 3.12

# Установка

1. Клонировать репозиторий.

2. Создание виртуального окружения и установка зависимостей:
```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

4. Установить PostgreSQL

5. Создать базу данных
```bash
psql -U postgres
```
```bash
CREATE DATABASE bot_db;
CREATE ROLE bot_user with password 'XXXXXXXX';
ALTER ROLE "bot_user" WITH LOGIN;
GRANT ALL PRIVILEGES ON DATABASE "bot_db" to bot_user;
ALTER USER bot_user CREATEDB;
```

6. Создать файл `.env` и заполнить его по образцу из `.env.example`

7. Запуcтить бот.

```bash
python3 main.py
```



