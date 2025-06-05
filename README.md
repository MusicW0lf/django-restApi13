# 📘 Система керування проектами з виконанням коду

> *Веб-застосунок для керування проектами з можливістю виконання обмеженого Python-коду та аутентифікацією користувача.*

---

## 👤 Автор

- **ПІБ**: Юрасов Володимир
- **Група**: ФЕІ-42
- **Керівник**: Гусак Олег Васильович, аспірант, асистент
- **Дата виконання**: 01.06.2025

---

## 📌 Загальна інформація

- **Тип проєкту**: Вебзастосунок
- **Мова програмування**: Python
- **Фреймворки / Бібліотеки**: Django, Django REST framework, Graphene, RestrictedPython, Waitress, Locust

---

## 🧠 Опис функціоналу

- 🔐 Реєстрація та авторизація з JWT (через cookies)
- 📁 Створення, перейменування, видалення проектів
- 🧠 Збереження і виконання Python-коду з sandbox-оточенням
- 🌐 REST API для керування проектами
- 🧬 GraphQL API як альтернативний інтерфейс
- 🧪 Навантажувальне тестування через Locust
- 🧪 Файли для тестування у Postman

---

## 🧱 Опис основних класів / файлів

| Клас / Файл                         | Призначення |
|------------------------------------|-------------|
| `views.py`                         | REST-ендпоінти для автентифікації та проектів |
| `serializers.py`                   | Схеми перетворення моделей у JSON |
| `models.py`                        | Модель Project з автором, кодом, мовою |
| `graphql_views.py`                 | GraphQL обробка запитів через Graphene |
| `urls.py`                          | Основні маршрути API |
| `locust_rest.py`, `locust_graphql.py` | Скрипти навантажувального тестування |

---

## ▶️ Як запустити проєкт "з нуля"

### 1. Встановлення інструментів

- Python 3.11+
- pip
- PostgreSQL (або SQLite для локального запуску)

### 2. Клонування репозиторію

```bash
git clone git@github.com:MusicW0lf/django-restApi13.git
cd django-restApi13
```

### 3. Створення віртуального середовища

```bash
python -m venv venv
venv/Scripts/Activate
```

### 4. Створення .env файлу з даними для бази даних

```bash
DB_PASSWORD = 'postgres'
DB_HOST = 'localhost'
DB_PORT ='5432'
DB_USERNAME = 'postgres'
DB_NAME = 'AlgoLib'
```

### 5. Встановлення залежностей

```bash
pip install -r requirements.txt
```

### 6. Налаштування БД

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Запуск сервера

```bash
python manage.py runserver
```

або за допомогою **waitress**:

```bash
waitress-serve --listen=0.0.0.0:8080 --threads=32 server.wsgi:application
```

---

## 🔌 API приклади

> **Примітка**: після входу JWT-токен зберігається в HttpOnly cookie.

### 🔐 Аутентифікація

#### **POST `/signup`**

```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "securepass"
}
```

#### **POST `/login`**

```json
{
  "email": "test@example.com",
  "password": "securepass"
}
```

#### **POST `/logout`**

Очищає cookie з JWT.

---

### 📁 Проекти

#### **GET `/user-projects/`**

Отримати список проектів користувача.

#### **POST `/create-project`**

```json
{
  "name": "Мій перший проект",
  "language": "Python"
}
```

#### **GET `/project/<project-id>/`**

Отримати деталі проекту, якщо користувач є автором.

#### **PATCH `/project/<project_id>/rename/`**

```json
{
  "name": "Оновлена назва"
}
```

#### **DELETE `/project/<project_id>/delete/`**

Видалити проект.

#### **POST `/project/execute/`**

```json
{
  "project_id": 3,
  "code": "print(1 + 2)"
}
```

**Response:**

```json
{
  "stdout": ["3"],
  "error": null
}
```

---

### 👤 Користувач

#### **GET `/user-details`**

Повертає:

```json
{ "username": "testuser" }
```

---

## 🧪 Тестування навантаження

### Запуск Locust (REST):

```bash
locust -f locust_rest.py --host=http://127.0.0.1:8080/
```

### Запуск Locust (GraphQL):

```bash
locust -f locust_graphql.py --host=http://127.0.0.1:8080/graphql/
```

---

## 🖱️ Інструкція для користувача

1. **Зареєструйтесь** або **увійдіть** на http://localhost:8000/signup або /login
2. Зайдіть на http://localhost:8000/graqhql/ і використовуючи візуальну панель:
   - `➕ Створити проект`
   - `📄 Перегляд імені та коду проектів`
   - `✏️ Перейменувати`, `🗑️ Видалити`
   - `▶️ Виконати код`

---

## 📷 Приклади / скриншоти

Скриншоти інтерфейсу або API-відповідей у папці `/screenshots/`

Крім того надані файли тестувальних кейсів для Postman, як для GraphQL так і для REST.
---

## 🧪 Проблеми і рішення

| Проблема                   | Рішення                                  |
|---------------------------|-------------------------------------------|
| Сайту за посиланням не існує      | При використанні runserver використовується порт 8000, waitress використовує порт 8080 |
| Точка доступу не працює           | Перевірити правильність посилання, наприклад /login правильне, а /login/ ні |
| JWT не зберігається               | Перевірити cookie-налаштування (HttpOnly, SameSite) |
| Код не виконується                | Перевірити правильність синтаксису та sandbox-обмеження |
| CORS помилка                      | Додати CORS middleware (`django-cors-headers`) |

---

## 🧾 Використані джерела / література

- Django Official Docs
- Django REST Framework
- Graphene-Django
- RestrictedPython
- StackOverflow

---
