from datetime import datetime
import json
import re
import sys
from typing import TypedDict
from urllib.parse import quote_plus
from urllib.parse import urlencode
from urllib.request import build_opener
from urllib.request import HTTPError

import xbmc
import xbmcgui
import xbmcplugin

import requests


def show_top():
    add_dashboard()
    listitem = xbmcgui.ListItem("検索")
    url = "%s?action=%s" % (sys.argv[0], "show_keyword_search")
    xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, listitem, True)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))


def add_dashboard():
    dashboard_endpoints = [
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
    for dashboard_endpoint in dashboard_endpoints:
        listitem = xbmcgui.ListItem(dashboard_endpoint["name"])
        url = "%s?action=%s&dashboard_url=%s" % (
            sys.argv[0],
            "dashboard",
            quote_plus(dashboard_endpoint["url"]),
        )
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, listitem, True)


def dashboard(url: str):
    data = get(url, {"x-tver-platform-type": "web"})
    contents = data["result"]["contents"]["contents"]
    add_contents(contents)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))


def __url(url: str) -> tuple[str, str]:
    buf = urlread(url)
    episode = json.loads(buf)
    video = episode["video"]
    videoRefID = video.get("videoRefID")
    videoID = video.get("videoID")
    accountID = video["accountID"]
    playerID = video["playerID"]
    url = f"https://players.brightcove.net/{accountID}/{playerID}_default/index.min.js"
    buf = urlread(url)
    policykey = re.search(
        r'options:\{accountId:"(.*?)",policyKey:"(.*?)"\}', buf.decode()
    ).group(2)
    if videoRefID:
        url = f"https://edge.api.brightcove.com/playback/v1/accounts/{accountID}/videos/ref%3A{videoRefID}"
    elif videoID:
        url = f"https://edge.api.brightcove.com/playback/v1/accounts/{accountID}/videos/{videoID}"
    playback = get(url, {"accept": f"application/json;pk={policykey}"})
    sources = playback.get("sources")
    text_tracks = playback["text_tracks"][0]["sources"]
    if text_tracks:
        vtt_url: str = text_tracks[0]["src"]
    else:
        vtt_url = ""
    filtered = filter(
        lambda source: source.get("ext_x_version")
        and source.get("src").startswith("https://"),
        sources,
    )
    video_url: str = list(filtered)[-1].get("src")
    return video_url, vtt_url


def play(url: str):
    video_url, vtt_url = __url(url)
    listitem = xbmcgui.ListItem(path=video_url)
    if vtt_url:
        listitem.setSubtitles([vtt_url])
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


def add_contents(contents: list[Content]):
    items = []
    for data in contents:
        item = data["content"]
        id = item["id"]
        title = f'{item["broadcastDateLabel"]} {item["seriesTitle"]}  {item["title"]}'
        description = "\n".join(
            [
                item["seriesTitle"],
                item["title"],
                "",
                item["broadcastDateLabel"],
                "配信終了: "
                + datetime.fromtimestamp(item["endAt"]).strftime("%Y-%m-%d %H:%M:%S"),
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


def urlread(url: str, *headers):
    opener = build_opener()
    h = [("User-Agent", "")]
    for header in headers:
        h.append(header)
    opener.addheaders = h
    try:
        response = opener.open(url)
        buf = response.read()
        response.close()
    except HTTPError:
        buf = ""
    return buf


def get(url: str, *headers_arg: dict[str, str]):
    headers: dict[str, str] = {"User-Agent": ""}
    for header in headers_arg:
        headers |= header
    r = requests.get(url, headers=header)
    return r.json()


def get_token() -> tuple[str, str]:
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
    return (platform_uid, platform_token)


def keyword_search(platform_uid: str, platform_token: str, keyword: str) -> dict:
    endpoint = "https://platform-api.tver.jp/service/api/v2/callKeywordSearch"
    params = urlencode(
        {
            "platform_uid": platform_uid,
            "platform_token": platform_token,
            "keyword": keyword,
        }
    )
    url = f"{endpoint}?{params}"
    return get(url, {"x-tver-platform-type": "web"})


def show_keyword_search(keyword: str = ""):
    keyword = keyword or prompt("検索")
    if keyword:
        platform_uid, platform_token = get_token()
        data = keyword_search(platform_uid, platform_token, keyword)
        contents = data["result"]["contents"]
        if contents:
            add_contents(contents)
            xbmcplugin.endOfDirectory(int(sys.argv[1]))


def prompt(heading: str = "") -> str:
    kb = xbmc.Keyboard("", heading)
    kb.doModal()
    if kb.isConfirmed():
        name = kb.getText()
        return name
    return ""
