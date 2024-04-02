import json
from pathlib import Path
from typing import TypedDict

import xbmcaddon
from xbmcvfs import translatePath


class KeywordJson(TypedDict):
    keyword_list: list[str]


def _get_filepath(filename: str) -> Path:
    profile_dir = Path(translatePath(xbmcaddon.Addon().getAddonInfo("profile")))
    profile_dir.mkdir(parents=True, exist_ok=True)
    path = profile_dir.joinpath(filename)
    path.touch()
    return path


def _get_keyword_history_path() -> Path:
    HISTORY_FILENAME = "keyword_history.json"
    return _get_filepath(HISTORY_FILENAME)


def append_keyword_history(keyword: str):
    keyword_list = get_keyword_history()
    if keyword in keyword_list:
        keyword_list.remove(keyword)
    keyword_list.insert(0, keyword)
    keyword_list = keyword_list[:20]
    _set_keyword_history(keyword_list)


def get_keyword_history() -> list[str]:
    keyword_history_file = _get_keyword_history_path()
    with open(keyword_history_file) as f:
        try:
            keyword_history: KeywordJson = json.load(f)
            return keyword_history["keyword_list"]
        except:
            return []


def _set_keyword_history(keywords: list[str]):
    with open(_get_keyword_history_path(), "w") as f:
        json.dump({"keyword_list": keywords}, f)


def remove_keyword(keywords: list[str]):
    keyword_list = get_keyword_history()
    for keyword in keywords:
        if keyword in keyword_list:
            keyword_list.remove(keyword)
    _set_keyword_history(keyword_list)


def remove_all_keyword():
    _set_keyword_history([])
