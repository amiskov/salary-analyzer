import requests
from statistics import mean
import math
from logging import info

from salary import predict_rub_salary

URL = 'https://api.superjob.ru/2.0/vacancies/'


def get_lang_stats(lang: str,  api_key: str | None = None) -> dict:
    vacancies_found, vacancies_processed = 0, 0
    possible_salaries = []

    params = {
        'keyword': lang,
        'count': 100,  # max 100 positions per page
    }

    if not api_key:
        raise ValueError('Please, provide an API KEY.')

    page, pages = 0, 1
    while page < pages:
        params.update({'page': page})
        resp = _fetch(params, api_key)
        vacancies_found = resp['total']

        for position in resp['objects']:
            salary_from, salary_to = _get_salary_range(position)
            possible_salary = predict_rub_salary(salary_from, salary_to)
            if not possible_salary:
                continue  # skip positions with no salary
            possible_salaries.append(possible_salary)
            vacancies_processed += 1

        pages = math.ceil(vacancies_found / params['count'])
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


def _fetch(user_params: dict, api_key: str) -> dict:
    """
    Качает данные с HH API и возвращает ответ в виде словаря.
    На вход принимается словарь параметров для GET-запроса.
    Нумерация страниц в HH API начинаются с 0.
    """
    headers = {
        'X-Api-App-Id': api_key,
    }
    params = {
        'town': 4,  # "Москва"
        'period': 30,  # дней
        'catalogues': 48,  # "Разработка, программирование"
    }
    params.update(user_params)
    resp = requests.get(URL, params=params, headers=headers)
    resp.raise_for_status()
    return resp.json()


def _get_salary_range(position: dict) -> tuple[int | None, int | None]:
    """Возвращает значения "от" и "до" из зарплаты вакансии."""
    salary_from, salary_to = None, None
    if position['payment_from'] != 0:
        salary_from = position['payment_from']
    if position['payment_to'] != 0:
        salary_to = position['payment_to']
    return salary_from, salary_to
