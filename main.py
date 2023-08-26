from functools import partial
from typing import Callable
from logging import error
import logging

from terminaltables import AsciiTable
from environs import Env
import requests

import superjob
import hh

LANGS = ['Python', 'C', 'C++', 'Ruby', 'Java', '1С',
         'JavaScript', 'Go', 'PHP', 'C#', 'Swift', 'Kotlin']


def main():
    env = Env()
    env.read_env()
    logging.basicConfig(level=logging.INFO)

    SJ_SECRET_KEY = env('SUPERJOB_SECRET_KEY')

    # HeadHunter Stats
    langs_stats = get_service_stats(hh.get_lang_stats, LANGS)
    table = create_table_from_stats('HeadHunter Moscow', langs_stats)
    print(table.table)

    # SuperJob Stats
    sj_stats_getter = partial(superjob.get_lang_stats, api_key=SJ_SECRET_KEY)
    langs_stats = get_service_stats(sj_stats_getter, LANGS)
    table = create_table_from_stats('SuperJob Moscow', langs_stats)
    print(table.table)


def get_service_stats(get_lang_stats: Callable[[str], dict],
                      langs: list[str]) -> dict:
    """Возвращает статистику по вакансиям для языков программирования.

    - `get_lang_stats` - получает статистику для одного языка
                            программирования из произвольного сервиса.
    - `langs` - языки программирования, по которым нужно составить статистику.
    """
    langs_stats = {}
    for lang in langs:
        print(f'Searching {lang} positions...')
        try:
            langs_stats[lang.capitalize()] = get_lang_stats(lang)
        except requests.ConnectionError as e:
            print("Unable to connect API.")
            error(e)
        except requests.HTTPError as e:
            print("Request to API failed.")
            error(e)
    return langs_stats


def create_table_from_stats(title: str, langs_stats: dict) -> AsciiTable:
    """Возвращает таблицу для последующей печати из данных по вакансиям."""
    table_data = [
        ('Язык программирования', 'Вакансий найдено',
         'Вакансий обработано', 'Средняя зарплата')
    ]
    for lang, stats in langs_stats.items():
        row = (lang, stats['vacancies_found'], stats['vacancies_processed'],
               stats['average_salary'])
        table_data.append(row)
    table = AsciiTable(table_data)
    table.title = title
    return table


if __name__ == '__main__':
    main()
