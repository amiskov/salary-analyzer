def predict_rub_salary(salary_from, salary_to) -> int | None:
    """ Возвращает ожидаемую зарплату в рублях.

    Ожидаемая ЗП считается:
    - как среднее, если указаны оба поля `from` и `to`;
    - `from` * 1.2, если указано только поле `from`;
    - `to` * 0.8, если указано только поле `to`;
    - если `from` и `to` не указаны, вернётся `None`.
    """
    if salary_from and salary_to:
        return int((salary_from + salary_to) / 2)
    elif salary_from and not salary_to:
        return int(salary_from * 1.2)
    elif not salary_from and salary_to:
        return int(salary_to * .8)
    else:
        return None
