import datetime
import json
import re
import sys
from typing import NamedTuple
from urllib.parse import quote_plus
from urllib.parse import urlencode
from urllib.request import build_opener
from urllib.request import HTTPError

import xbmc
import xbmcgui
import xbmcplugin

import requests


def show_top():
    add_action(name="総合ランキング", action="show_ranking_all")
    add_action(name="ドラマランキング", action="show_ranking_drama")
    add_action(name="バラエティランキング", action="show_ranking_variety")
    add_action(name="すべて 新着", action="show_newer_all")
    add_action(name="ドラマ 新着", action="show_newer_drama")
    add_action(name="バラエティ 新着", action="show_newer_variety")
    add_action(name="検索", action="show_keyword_search")
    xbmcplugin.endOfDirectory(int(sys.argv[1]))


def show_ranking_all():
    url = "https://service-api.tver.jp/api/v1/callEpisodeRankingDetail/all"
    data = get(url, {"x-tver-platform-type": "web"})
    contents = data["result"]["contents"]["contents"]
    add_contents(contents)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))


def show_ranking_drama():
    url = "https://service-api.tver.jp/api/v1/callEpisodeRankingDetail/drama"
    data = get(url, {"x-tver-platform-type": "web"})
    contents = data["result"]["contents"]["contents"]
    add_contents(contents)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))


def show_ranking_variety():
    url = "https://service-api.tver.jp/api/v1/callEpisodeRankingDetail/variety"
    data = get(url, {"x-tver-platform-type": "web"})
    contents = data["result"]["contents"]["contents"]
    add_contents(contents)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))


def show_newer_all():
    url = "https://service-api.tver.jp/api/v1/callNewerDetail/all"
    data = get(url, {"x-tver-platform-type": "web"})
    contents = data["result"]["contents"]["contents"]
    add_contents(contents)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))


def show_newer_drama():
    url = "https://service-api.tver.jp/api/v1/callNewerDetail/drama"
    data = get(url, {"x-tver-platform-type": "web"})
    contents = data["result"]["contents"]["contents"]
    add_contents(contents)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))


def show_newer_variety():
    url = "https://service-api.tver.jp/api/v1/callNewerDetail/variety"
    data = get(url, {"x-tver-platform-type": "web"})
    contents = data["result"]["contents"]["contents"]
    add_contents(contents)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))


def __url(url: str) -> tuple[str, str]:
    buf = urlread(url)
    episode = json.loads(buf)
    video = episode.get("video")
    videoRefID = video.get("videoRefID")
    videoID = video.get("videoID")
    accountID = video.get("accountID")
    playerID = video.get("playerID")
    url = f"https://players.brightcove.net/{accountID}/{playerID}_default/index.min.js"
    buf = urlread(url)
    policykey = re.search(
        r'options:\{accountId:"(.*?)",policyKey:"(.*?)"\}', buf.decode()
    ).group(2)
    if videoRefID:
        url = f"https://edge.api.brightcove.com/playback/v1/accounts/{accountID}/videos/ref%3A{videoRefID}"
    elif videoID:
        url = f"https://edge.api.brightcove.com/playback/v1/accounts/{accountID}/videos/{videoID}"
    buf = urlread(url, ("accept", f"application/json;pk={policykey}"))
    playback = json.loads(buf)
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


class ContentInfo(NamedTuple):
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


class Content(NamedTuple):
    type: str
    content: ContentInfo


def add_contents(contents):
    items = []
    for data in contents:
        item = data.get("content")
        id = item.get("id")
        date = item.get("broadcastDateLabel")
        title = []
        if date:
            title.append(date)
        if item.get("seriesTitle"):
            title.append(item.get("seriesTitle"))
        if item.get("title"):
            title.append("    " + item.get("title"))
        title = " ".join(title)
        description = "\n".join(
            [
                item["seriesTitle"],
                item["title"],
                item["broadcastDateLabel"],
                "配信終了: "
                + datetime.datetime.fromtimestamp(item["endAt"]).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "字幕: " + str(item["isSubtitle"]),
                item["broadcasterName"],
            ]
        )
        broadcasterName = item.get("broadcasterName")
        thumbnail = (
            f"https://statics.tver.jp/images/content/thumbnail/episode/small/{id}.jpg"
        )
        episode_url = f"https://statics.tver.jp/content/episode/{id}.json"
        labels = {
            "title": title,
            "plot": description,
            "plotoutline": description,
            "studio": broadcasterName,
            "date": __labeldate(__date(date)),
        }
        listitem = xbmcgui.ListItem(title)
        listitem.setArt(
            {
                "icon": thumbnail,
                "thumb": thumbnail,
                "poster": thumbnail,
            }
        )
        listitem.setInfo(type="video", infoLabels=labels)
        listitem.setProperty("IsPlayable", "true")
        url = "%s?action=%s&url=%s" % (sys.argv[0], "play", quote_plus(episode_url))
        items += [(url, listitem, False)]
    xbmcplugin.addDirectoryItems(int(sys.argv[1]), items)


def add_action(name, action):
    listitem = xbmcgui.ListItem(name)
    url = "%s?action=%s" % (sys.argv[0], action)
    xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, listitem, True)


def __date(itemdate):
    now = datetime.datetime.now()
    year0 = now.strftime("%Y")
    date0 = now.strftime("%m-%d")
    date = "0000-00-00"
    m = re.match(r"(20[0-9]{2})年", itemdate)
    if m:
        date = "%s-00-00" % (m.group(1))
    m = re.match(r"([0-9]{1,2})月([0-9]{1,2})日", itemdate)
    if m:
        date1 = "%02d-%02d" % (int(m.group(1)), int(m.group(2)))
        date = "%04d-%s" % (int(year0) - 1 if date1 > date0 else int(year0), date1)
    m = re.match(r"([0-9]{1,2})/([0-9]{1,2})", itemdate)
    if m:
        date1 = "%02d-%02d" % (int(m.group(1)), int(m.group(2)))
        date = "%04d-%s" % (int(year0) if date1 < date0 else int(year0) - 1, date1)
    return date


def __labeldate(date):
    m = re.search("^([0-9]{4})-([0-9]{2})-([0-9]{2})", date)
    if m:
        date = "%s.%s.%s" % (m.group(3), m.group(2), m.group(1))
    return date


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


def get_search_result(url: str) -> dict:
    headers = {"User-Agent": "", "x-tver-platform-type": "web"}
    r = requests.get(url, headers=headers)
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
    params = urlencode(
        {
            "platform_uid": platform_uid,
            "platform_token": platform_token,
            "keyword": keyword,
        }
    )
    endpont = "https://platform-api.tver.jp/service/api/v1/callKeywordSearch"
    url = f"{endpont}?{params}"
    return get_search_result(url)


def show_keyword_search(keyword: str = ""):
    keyword = keyword or prompt("検索")
    if keyword:
        platform_uid, platform_token = get_token()
        buf = keyword_search(platform_uid, platform_token, keyword)
        contents = buf["result"]["contents"]
        add_contents(contents)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))


def prompt(heading: str = "") -> str:
    kb = xbmc.Keyboard("", heading)
    kb.doModal()
    if kb.isConfirmed():
        name = kb.getText()
        return name
    return ""
