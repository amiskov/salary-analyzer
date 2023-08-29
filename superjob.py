from statistics import mean
from logging import info
import math

import requests

from salary import predict_rub_salary

URL = 'https://api.superjob.ru/2.0/vacancies/'


def get_lang_stats(lang: str,  api_key: str | None = None) -> dict:
    """Возвращает статистику по языку программирования от SuperJob."""
    vacancies_found = 0
    possible_salaries = []

    if not api_key:
        raise ValueError('Please, provide an API KEY.')

    headers = {
        'X-Api-App-Id': api_key,
    }
    params = {
        'town': 4,  # "Москва"
        'period': 30,  # дней
        'catalogues': 48,  # "Разработка, программирование"
        'count': 100,  # max 100 positions per page
        'keyword': lang,
    }

    page, pages = 0, 1
    while page < pages:
        params.update({'page': page})

        raw_resp = requests.get(URL, params=params, headers=headers)
        raw_resp.raise_for_status()
        resp = raw_resp.json()

        for position in resp['objects']:
            salary_from, salary_to = _get_salary_range(position)
            possible_salary = predict_rub_salary(salary_from, salary_to)
            if not possible_salary:
                continue  # skip positions with no salary
            possible_salaries.append(possible_salary)

        vacancies_found = resp['total']
        pages = math.ceil(vacancies_found / params['count'])
        info(f'{lang.capitalize()} page {page+1} of {pages}.')
        page += 1

    avg_salary = 0
    if possible_salaries:
        avg_salary = int(mean(possible_salaries))

    return {
        'vacancies_found': vacancies_found,
        'vacancies_processed': len(possible_salaries),
        'average_salary': avg_salary,
    }


def _get_salary_range(position: dict) -> tuple[int | None, int | None]:
    """Возвращает значения "от" и "до" из зарплаты вакансии."""
    salary_from, salary_to = None, None
    if position['payment_from'] != 0:
        salary_from = position['payment_from']
    if position['payment_to'] != 0:
        salary_to = position['payment_to']
    return salary_from, salary_to
