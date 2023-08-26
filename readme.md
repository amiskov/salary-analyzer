# Статистика по вакансиям
Выводит среднюю зарплату для заданных языков программирования. Работает с HeadHunter и SuperJob.

## Установка
Установите зависимости через Poetry [Poetry](https://python-poetry.org):

```sh
poetry install
```
Получите [API-ключ для SuperJob](https://api.superjob.ru) (нужна регистрация) и сохраните его в файл `.env` взяв за основу `.env.example`.

## Запуск
Языки программирования указаны в `main.py` в константе `LANGS`. Получить по ним статистику:

```sh
poetry run python main.py
```
