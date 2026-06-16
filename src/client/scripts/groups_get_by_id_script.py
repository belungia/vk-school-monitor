def groups_get_by_id_script(group_ids: list[str]) -> str:
    """
    Генерирует VK Script для получения базовой инфы о сообществах по их id/короткому имени.
    Принимает список идентификаторов (например, ["club123", "team"]).
    Возвращает результат одного вызова API.groups.getById сразу по всем переданным id.
    """
    ids_str = ",".join(group_ids)
    script = f"""
    return API.groups.getById({{
        "group_ids": "{ids_str}",
        "fields": "name,screen_name"
    }});
    """
    return script
