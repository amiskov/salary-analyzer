import requests
from pprint import pprint
import logging
from logging import info, error
from statistics import mean
from salary import predict_rub_salary

logging.basicConfig(level=logging.INFO)


URL = 'https://api.hh.ru/vacancies'
LANGS = ['Python', 'Java', 'JavaScript', 'Go', 'PHP', 'C#', 'Swift', 'Kotlin']


def predict_rub_salary_hh(position: dict) -> int | None:
    """ Возвращает ожидаемую зарплату в рублях.

    Ожидаемая ЗП считается:
    - как среднее, если указаны оба поля `from` и `to`;
    - `from` * 1.2, если указано только поле `from`;
    - `to` * 0.8, если указано только поле `to`;
    - если `from` и `to` не указаны, вернётся `None`.
    """
    salary = position['salary']
    if not salary:
        return None
    if salary['currency'] != 'RUR':
        return None
    return predict_rub_salary(salary['from'], salary['to'])


def get_salaries_by_lang(lang: str) -> list[dict]:
    params = {
        'area': 1,  # Moscow
        'period': 30,  # month
        'professional_role': 96,  # Программист, разработчик
        # 'only_with_salary': True,
        # 'currency': 'RUR',
        'text': lang,
        # 'per_page': 5,
        'search_field': 'name',  # искать в названии
    }
    resp = requests.get(URL, params=params)
    resp.raise_for_status()
    salaries = []
    for position in resp.json()['items']:
        salaries.append(predict_rub_salary_hh(position))
    return salaries


def count_lang_positions(lang: str) -> int:
    params = {
        'area': '1',  # Moscow
        'period': 30,  # month
        'professional_role': 96,  # Программист, разработчик
        'text': lang,
        'per_page': 0,
        'search_field': 'name',  # искать в названии
    }
    resp = requests.get(URL, params=params)
    resp.raise_for_status()
    return resp.json()['found']


def fetch_from_hh(user_params: dict) -> dict:
    """
    Качает данные с HH API и возвращает ответ в виде словаря.
    На вход принимается словарь параметров для GET-запроса.
    Нумерация страниц в HH API начинаются с 0.
    """
    params = {
        'area': '1',  # Moscow
        'period': 30,  # days
        'professional_role': 96,  # Программист, разработчик
        'search_field': 'name',  # название вакансии
    }
    params.update(user_params)
    resp = requests.get(URL, params=params)
    resp.raise_for_status()
    return resp.json()


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
        resp = fetch_from_hh(params)
        vacancies_found = resp['found']

        for position in resp['items']:
            possible_salary = predict_rub_salary_hh(position)
            if not possible_salary:
                continue  # skip positions with no salary
            possible_salaries.append(possible_salary)
            vacancies_processed += 1

        pages = resp['pages']
        info(f'{lang.capitalize()} page {page+1} of {pages}.')
        page += 1

    return {
        'vacancies_found': vacancies_found,
        'vacancies_processed': vacancies_processed,
        'average_salary': int(mean(possible_salaries)),
    }


def main():
    # totals = defaultdict(int)
    # for lang in langs:
    #     totals[lang] = count_lang_positions(lang)
    #     print(f'Found {totals[lang]} for {lang}.')
    #     time.sleep(1)
    # pprint(dict(totals))
    # pprint(get_salaries_by_lang('python'))

    langs_stats = {}
    for lang in LANGS:
        print(f'Searching {lang} positions...')
        try:
            langs_stats[lang.capitalize()] = get_lang_stats(lang)
        except requests.ConnectionError as e:
            print("Unable to connect HH API.")
            error(e)
        except requests.HTTPError as e:
            print("Request to HH API failed.")
            error(e)
    pprint(langs_stats)


if __name__ == '__main__':
    main()
