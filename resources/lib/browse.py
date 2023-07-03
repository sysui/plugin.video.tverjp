from datetime import datetime
import json
from pathlib import Path
import re
import sys
from typing import TypedDict
from urllib.parse import quote_plus, urlencode

import xbmc
import xbmcaddon
from xbmcvfs import translatePath
import xbmcgui
import xbmcplugin

import requests


def show_top():
    _add_dashboard()
    listitem = xbmcgui.ListItem("検索 / 検索履歴")
    url = "%s?action=%s" % (sys.argv[0], "show_keyword_history")
    xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, listitem, True)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))


def _add_dashboard():
    dashboard_entrypoints = [
        {
            "name": "総合ランキング",
            "url": "https://service-api.tver.jp/api/v1/callEpisodeRankingDetail/all",
        },
        {
            "name": "ドラマランキング",
            "url": "https://service-api.tver.jp/api/v1/callEpisodeRankingDetail/drama",
        },
        {
            "name": "バラエティランキング",
            "url": "https://service-api.tver.jp/api/v1/callEpisodeRankingDetail/variety",
        },
        {
            "name": "すべて 新着",
            "url": "https://service-api.tver.jp/api/v1/callNewerDetail/all",
        },
        {
            "name": "ドラマ 新着",
            "url": "https://service-api.tver.jp/api/v1/callNewerDetail/drama",
        },
        {
            "name": "バラエティ 新着",
            "url": "https://service-api.tver.jp/api/v1/callNewerDetail/variety",
        },
    ]
    for dashboard_endpoint in dashboard_entrypoints:
        listitem = xbmcgui.ListItem(dashboard_endpoint["name"])
        url = "%s?action=%s&dashboard_url=%s" % (
            sys.argv[0],
            "dashboard",
            quote_plus(dashboard_endpoint["url"]),
        )
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, listitem, True)


def dashboard(url: str):
    data = _get_json(url, {"x-tver-platform-type": "web"})
    contents = data["result"]["contents"]["contents"]
    _add_contents(contents)


def _get_video(url: str) -> tuple[str, list[str]]:
    buf = requests.get(url, headers={"User-Agent": ""}).content
    episode = json.loads(buf)
    video = episode["video"]
    videoRefID = video.get("videoRefID")
    videoID = video.get("videoID")
    accountID = video["accountID"]
    playerID = video["playerID"]
    url = f"https://players.brightcove.net/{accountID}/{playerID}_default/index.min.js"
    buf = requests.get(url, headers={"User-Agent": ""}).content
    policykey = re.search(
        r'options:\{accountId:"(.*?)",policyKey:"(.*?)"\}', buf.decode()
    ).group(2)
    if videoRefID:
        url = f"https://edge.api.brightcove.com/playback/v1/accounts/{accountID}/videos/ref%3A{videoRefID}"
    elif videoID:
        url = f"https://edge.api.brightcove.com/playback/v1/accounts/{accountID}/videos/{videoID}"
    playback = _get_json(url, {"accept": f"application/json;pk={policykey}"})
    subtitle_uri_list = []
    if text_tracks := playback["text_tracks"][0]["sources"]:
        subtitle_uri_list = list(
            map(
                lambda text_track: text_track["src"],
                text_tracks,
            )
        )
    filtered = filter(
        lambda source: source.get("ext_x_version")
        and source.get("src").startswith("https://"),
        playback.get("sources"),
    )
    video_url: str = list(filtered)[-1].get("src")
    return video_url, subtitle_uri_list


def play(url: str):
    video_url, subtitle_uri_list = _get_video(url)
    listitem = xbmcgui.ListItem(path=video_url)
    if subtitle_uri_list:
        listitem.setSubtitles(subtitle_uri_list)
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), succeeded=True, listitem=listitem)


class ContentInfo(TypedDict):
    id: str
    version: int
    title: str
    seriesID: str
    endAt: int
    broadcastDateLabel: str
    isNHKContent: bool
    isSubtitle: bool
    ribbonID: int
    seriesTitle: str
    isAvailable: bool
    broadcasterName: str
    productionProviderName: str


class Content(TypedDict):
    type: str
    content: ContentInfo


def _add_contents(contents: list[Content]):
    items = []
    for data in contents:
        item = data["content"]
        id = item["id"]
        title = f'{item["broadcastDateLabel"]} {item["seriesTitle"]}  {item["title"]}'
        # Year 2038 problem
        if item["endAt"] < 2147483647:
            endAtStr = datetime.fromtimestamp(item["endAt"]).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        else:
            endAtStr = "なし"
        description = "\n".join(
            [
                item["seriesTitle"],
                item["title"],
                "",
                item["broadcastDateLabel"],
                "配信終了: " + endAtStr,
                "字幕: " + str(item["isSubtitle"]),
                item["broadcasterName"],
            ]
        )
        thumbnail = (
            f"https://statics.tver.jp/images/content/thumbnail/episode/small/{id}.jpg"
        )
        listitem = xbmcgui.ListItem(title)
        listitem.setArt(
            {
                "icon": thumbnail,
                "thumb": thumbnail,
                "poster": thumbnail,
            }
        )
        labels = {
            "title": title,
            "plot": description,
            "plotoutline": description,
            "studio": item["broadcastDateLabel"],
        }
        listitem.setInfo(type="video", infoLabels=labels)
        listitem.setProperty("IsPlayable", "true")
        episode_url = f"https://statics.tver.jp/content/episode/{id}.json"
        url = "%s?action=%s&url=%s" % (sys.argv[0], "play", quote_plus(episode_url))
        items += [(url, listitem, False)]
    xbmcplugin.addDirectoryItems(int(sys.argv[1]), items)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))


def _get_json(url: str, *headers_arg: dict[str, str]) -> dict:
    headers: dict[str, str] = {"User-Agent": ""}
    for header in headers_arg:
        headers |= header
    r = requests.get(url, headers=headers)
    return r.json()


def _get_token() -> tuple[str, str]:
    URL_TOKEN_SERVICE = (
        "https://platform-api.tver.jp/v2/api/platform_users/browser/create"
    )
    headers = {
        "user-agent": "",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    r = requests.post(URL_TOKEN_SERVICE, data=b"device_type=pc", headers=headers)
    data = r.json()
    platform_uid = data["result"]["platform_uid"]
    platform_token = data["result"]["platform_token"]
    return platform_uid, platform_token


def _keyword_search(platform_uid: str, platform_token: str, keyword: str) -> dict:
    endpoint = "https://platform-api.tver.jp/service/api/v2/callKeywordSearch"
    params = urlencode(
        {
            "platform_uid": platform_uid,
            "platform_token": platform_token,
            "keyword": keyword,
        }
    )
    url = f"{endpoint}?{params}"
    return _get_json(url, {"x-tver-platform-type": "web"})


def show_keyword_search(keyword: str = ""):
    keyword = keyword or _prompt("検索")
    if keyword:
        _append_keyword_history(keyword)
        platform_uid, platform_token = _get_token()
        data = _keyword_search(platform_uid, platform_token, keyword)
        contents = data["result"]["contents"]
        if contents:
            _add_contents(contents)


def show_keyword_history():
    listitem = xbmcgui.ListItem("新しい検索")
    url = "%s?action=%s" % (sys.argv[0], "show_keyword_search")
    xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, listitem, True)
    for keyword in _get_keyword_history():
        listitem = xbmcgui.ListItem(keyword)
        url = "%s?action=%s&keyword=%s" % (
            sys.argv[0],
            "search_with_keyword_params",
            keyword,
        )
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, listitem, True)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))


def _prompt(heading: str = "") -> str:
    kb = xbmc.Keyboard("", heading)
    kb.doModal()
    if kb.isConfirmed():
        name = kb.getText()
        return name
    return ""


class KeywordJson(TypedDict):
    keyword_list: list[str]


def _get_keyword_history_path() -> Path:
    profile_dir = Path(translatePath(xbmcaddon.Addon().getAddonInfo("profile")))
    profile_dir.mkdir(parents=True, exist_ok=True)
    keyword_history_file = profile_dir.joinpath("keyword_history.json")
    keyword_history_file.touch()
    return keyword_history_file


def _append_keyword_history(keyword: str):
    keyword_history_file = _get_keyword_history_path()
    with open(keyword_history_file) as f:
        try:
            keyword_history: KeywordJson = json.load(f)
        except:
            keyword_history = {"keyword_list": []}
    if keyword in keyword_history["keyword_list"]:
        keyword_history["keyword_list"].remove(keyword)
    keyword_history["keyword_list"].insert(0, keyword)
    keyword_history["keyword_list"] = keyword_history["keyword_list"][:20]
    with open(keyword_history_file, "w") as f:
        json.dump(keyword_history, f)


def _get_keyword_history() -> list[str]:
    keyword_history_file = _get_keyword_history_path()
    with open(keyword_history_file) as f:
        try:
            keyword_history: KeywordJson = json.load(f)
            return keyword_history["keyword_list"]
        except:
            return []
