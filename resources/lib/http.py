import requests


def get_json(url: str, *headers_arg: dict[str, str]):
    headers: dict[str, str] = {"User-Agent": ""}
    for header in headers_arg:
        headers |= header
    r = requests.get(url, headers=headers)
    return r.json()
