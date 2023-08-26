import requests
from logging import info
from statistics import mean
from salary import predict_rub_salary


URL = 'https://api.hh.ru/vacancies'


def get_lang_stats(lang: str) -> dict:
    vacancies_found, vacancies_processed = 0, 0
    possible_salaries = []

    params = {
        'text': lang,
        'per_page': 50,  # 50 is the maximum
    }

    page, pages = 0, 1
    while page < pages:
        params.update({'page': page})
        resp = _fetch(params)
        vacancies_found = resp['found']

        for position in resp['items']:
            salary_from, salary_to = _get_salary_range(position)
            possible_salary = predict_rub_salary(salary_from, salary_to)
            if not possible_salary:
                continue  # skip positions with no salary
            possible_salaries.append(possible_salary)
            vacancies_processed += 1

        pages = resp['pages']
        info(f'{lang.capitalize()} page {page+1} of {pages}.')
        page += 1

    avg_salary = 0
    if possible_salaries:
        avg_salary = int(mean(possible_salaries))

    return {
        'vacancies_found': vacancies_found,
        'vacancies_processed': vacancies_processed,
        'average_salary': avg_salary,
    }


def _fetch(user_params: dict) -> dict:
    """
    Качает данные с HH API и возвращает ответ в виде словаря.
    На вход принимается словарь параметров для GET-запроса.
    Нумерация страниц в HH API начинаются с 0.
    """
    params = {
        'area': '1',  # Moscow
        'period': 30,  # days
        'professional_role': 96,  # "Программист, разработчик"
        'search_field': 'name',  # искать в названии вакансии
    }
    params.update(user_params)
    resp = requests.get(URL, params=params)
    resp.raise_for_status()
    return resp.json()


def _get_salary_range(position: dict) -> tuple[int | None, int | None]:
    """Возвращает значения "от" и "до" из зарплаты вакансии."""
    salary = position['salary']
    if not salary:
        return None, None
    if salary['currency'] != 'RUR':
        return None, None
    return salary['from'], salary['to']
