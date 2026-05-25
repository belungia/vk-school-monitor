def users_get_script(user_ids: list[str]) -> str:
    """
    Генерирует VK Script для получения информации о пользователях.
    Принимает список строковых идентификаторов (например, ["id278844800", "keeeshik"]).
    Возвращает результат одного вызова API.users.get сразу для всех переданных ID.
    """
    ids_str = ",".join(user_ids)
    script = f"""
    return API.users.get({{
        "user_ids": "{ids_str}",
        "fields": "first_name,last_name"
    }});
    """
    return script