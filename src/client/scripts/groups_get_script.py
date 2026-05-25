def groups_get_script(user_ids: list[int]) -> str:
    script = f"""
    var user_ids = {user_ids};
    var results = [];
    var i = 0;
    while (i < user_ids.length) {{
        results.push(API.groups.get({{
            "user_id": user_ids[i],
            "extended": 1,
            "v": "5.199"
        }}));
        i = i + 1;
    }}
    return results;
    """
    return script