def extract_links_from_file_text(text: str) -> list[str]:
    lines = text.strip().splitlines()
    seen = set()
    unique_links = []
    for line in lines:
        link = line.strip()
        if link and link.startswith("https://vk.com/"):
            if link not in seen:
                seen.add(link)
                unique_links.append(link)
    return unique_links