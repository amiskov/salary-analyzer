def predict_rub_salary(salary_from, salary_to) -> int | None:
    """ Возвращает ожидаемую зарплату в рублях.

    Ожидаемая зарплата считается:
    - как среднее, если указаны оба поля `salary_from` и `salary_to`;
    - `salary_from` * 1.2, если указано только поле `salary_from`;
    - `salary_to` * 0.8, если указано только поле `salary_to`;
    - `None`, если `salary_from` и `salary_to` не указаны.
    """
    if salary_from and salary_to:
        return int((salary_from + salary_to) / 2)
    elif salary_from and not salary_to:
        return int(salary_from * 1.2)
    elif not salary_from and salary_to:
        return int(salary_to * .8)
    else:
        return None
