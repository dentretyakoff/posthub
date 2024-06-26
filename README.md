# PostHub

- [Описание](#desc)
- [Основные возможности](#main-features)
- [Технологический стек](#stack)
- [Установка и запуск](#install)
- [Команда](#team)

## Описание <a id="desc"></a>
Этот сервис представляет собой платформу для общения и обмена информацией между пользователями. Пользователи могут регистрироваться, оставлять посты, объединять посты в различные группы, подписываться друг на друга и комментировать посты. Сервис разработан с использованием стека Django 2.2, PostgreSQL и Python 3.9. Для обеспечения качества кода и функциональности написаны тесты.

## Основные возможности <a id="main-features"></a>

1. **Регистрация пользователей**:
   - Пользователи могут создавать учетные записи и входить в систему для доступа ко всем функциям сервиса.

2. **Создание и управление постами**:
   - Пользователи могут создавать текстовые посты.
   - Посты могут быть объединены в группы по интересам или тематикам.

3. **Взаимодействие пользователей**:
   - Пользователи могут подписываться друг на друга, создавая личные сети и сообщества.
   - Возможность оставлять комментарии к постам, что способствует активному обсуждению и обмену мнениями.

4. **Группы и объединение постов**:
   - Посты могут быть объединены в различные группы, что позволяет организовать контент по тематикам или интересам.

5. **Тестирование**:
   - Для сервиса написаны тесты, обеспечивающие качество кода и проверку функциональности всех основных возможностей.

## Технологический стек <a id="stack"></a>

- **Django 2.2**: Основной фреймворк для разработки веб-приложения.
- **PostgreSQL**: СУБД для хранения данных.
- **Python 3.9**: Язык программирования, используемый для разработки приложения.

## Установка и запуск <a id="install"></a>
Клонируйте репозиторий и перейдите в него в командной строке:

```
git clone git@github.com:dentretyakoff/posthub.git
```

```
cd yatube
```

В корне проекта создайте файл `.env` и заполните в нем переменную:
```
SECRET_KEY=Your_secret_key
```

Установите виртуальное окружение:

- На Windows:
```
python -m venv env
```
- На macOS и Linux: 
```
python3 -m venv env
```

Активируйте виртуальное окружение:

- На Windows: 
```
.\env\Scripts\activate
```
- На macOS и Linux: 
```
source env/bin/activate
```

Установите зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполните миграции:

```
python manage.py migrate
```

Создайте суперпользователя: 

```
python manage.py createsuperuser
```

Запустите сервер:

```
python manage.py runserver
```

Для запуска тестов используйте команду:
```
python manage.py test
```



## Команда <a id="team"></a>
[Денис Третьяков](https://github.com/dentretyakoff)


[MIT License](https://opensource.org/licenses/MIT)