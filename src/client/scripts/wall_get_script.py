def wall_get_script(owner_ids: list[int]) -> str:
    script = f"""
    var owner_ids = {owner_ids};
    var results = [];
    var i = 0;
    while (i < owner_ids.length) {{
        var r = API.wall.get({{
            "owner_id": owner_ids[i],
            "count": 100,
            "filter": "all",
            "v": "5.199"
        }});
        if (r && r.items) {{
            results.push(r.items);
        }} else {{
            results.push([]);
        }}
        i = i + 1;
    }}
    return results;
    """
    return script