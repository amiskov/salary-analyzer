import requests
from pprint import pprint
from environs import Env
from salary import predict_rub_salary
from statistics import mean
import logging
import math
from logging import info, error

logging.basicConfig(level=logging.INFO)

env = Env()
env.read_env()

SUPERJOB_ID = env('SUPERJOB_ID')
SUPERJOB_SECRET_KEY = env('SUPERJOB_SECRET_KEY')
LANGS = ['Python', 'Java', 'JavaScript', 'Go', 'PHP', 'C#', 'Swift', 'Kotlin']

URL = 'https://api.superjob.ru/2.0/vacancies/'


def fetch_from_sj(user_params: dict) -> dict:
    """
    Качает данные с HH API и возвращает ответ в виде словаря.
    На вход принимается словарь параметров для GET-запроса.
    Нумерация страниц в HH API начинаются с 0.
    """
    headers = {
        'X-Api-App-Id': SUPERJOB_SECRET_KEY,
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


def get_lang_stats(lang: str) -> dict:
    vacancies_found, vacancies_processed = 0, 0
    possible_salaries = []

    params = {
        'keyword': lang,
        'count': 100,  # max 100 positions per page
    }

    page, pages = 0, 1
    while page < pages:
        params.update({'page': page})
        resp = fetch_from_sj(params)
        vacancies_found = resp['total']

        for position in resp['objects']:
            possible_salary = predict_rub_salary_sj(position)
            if not possible_salary:
                continue  # skip positions with no salary
            possible_salaries.append(possible_salary)
            vacancies_processed += 1

        pages = math.ceil(vacancies_found / params['count'])
        info(f'{lang.capitalize()} page {page+1} of {pages}.')
        page += 1

    return {
        'vacancies_found': vacancies_found,
        'vacancies_processed': vacancies_processed,
        'average_salary': int(mean(possible_salaries))
        if len(possible_salaries) > 0 else 0,
    }


def predict_rub_salary_sj(position: dict) -> int | None:
    salary_from, salary_to = None, None
    if position['payment_from'] != 0:
        salary_from = position['payment_from']
    if position['payment_to'] != 0:
        salary_to = position['payment_to']
    return predict_rub_salary(salary_from, salary_to)


def main():
    langs_stats = {}
    for lang in LANGS:
        print(f'Searching {lang} positions...')
        try:
            langs_stats[lang.capitalize()] = get_lang_stats(lang)
        except requests.ConnectionError as e:
            print("Unable to connect SJ API.")
            error(e)
        except requests.HTTPError as e:
            print("Request to SJ API failed.")
            error(e)
    pprint(langs_stats)


if __name__ == '__main__':
    main()
