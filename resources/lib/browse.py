import sys
import re
import datetime
import json

import xbmcgui
import xbmcplugin


from urllib.parse import quote_plus
from urllib.parse import parse_qs

from resources.lib.common import urlread


def update_query(query, values=None):
    args = parse_qs(query, keep_blank_values=True)
    for key in args.keys():
        args[key] = args[key][0]
    args.update(values or {})
    return args


def show_top():
    __add_directory_item(name="総合ランキング", action="show_ranking_all")
    __add_directory_item(name="ドラマランキング", action="show_ranking_drama")
    __add_directory_item(name="バラエティランキング", action="show_ranking_variety")
    __add_directory_item(name="すべて 新着", action="show_newer_all")
    __add_directory_item(name="ドラマ 新着", action="show_newer_drama")
    __add_directory_item(name="バラエティ 新着", action="show_newer_variety")
    xbmcplugin.endOfDirectory(int(sys.argv[1]))


def show_ranking_all():
    url = "https://service-api.tver.jp/api/v1/callEpisodeRankingDetail/all"
    buf = urlread(url, ("x-tver-platform-type", "web"))
    contents = json.loads(buf).get("result").get("contents").get("contents")
    __add_itemV2(contents)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))


def show_ranking_drama():
    url = "https://service-api.tver.jp/api/v1/callEpisodeRankingDetail/drama"
    buf = urlread(url, ("x-tver-platform-type", "web"))
    contents = json.loads(buf).get("result").get("contents").get("contents")
    __add_itemV2(contents)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))


def show_ranking_variety():
    url = "https://service-api.tver.jp/api/v1/callEpisodeRankingDetail/variety"
    buf = urlread(url, ("x-tver-platform-type", "web"))
    contents = json.loads(buf).get("result").get("contents").get("contents")
    __add_itemV2(contents)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))


def show_newer_all():
    url = "https://service-api.tver.jp/api/v1/callNewerDetail/all"
    buf = urlread(url, ("x-tver-platform-type", "web"))
    contents = json.loads(buf).get("result").get("contents").get("contents")
    __add_itemV2(contents)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))


def show_newer_drama():
    url = "https://service-api.tver.jp/api/v1/callNewerDetail/drama"
    buf = urlread(url, ("x-tver-platform-type", "web"))
    contents = json.loads(buf).get("result").get("contents").get("contents")
    __add_itemV2(contents)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))


def show_newer_variety():
    url = "https://service-api.tver.jp/api/v1/callNewerDetail/variety"
    buf = urlread(url, ("x-tver-platform-type", "web"))
    contents = json.loads(buf).get("result").get("contents").get("contents")
    __add_itemV2(contents)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))


def __url(url):
    # episodeをダウンロード
    # https://statics.tver.jp/content/episode/epv3o3rrpl.json?v=18
    buf = urlread(url)
    episode = json.loads(buf)
    # "video": {
    #     "videoRefID": "37255_37254_38777",
    #     "accountID": "4394098883001",
    #     "playerID": "MfxS5MXtZ",
    #     "channelID": "ex"
    # },
    # "video": {
    #     "videoID": "6322519809112",
    #     "accountID": "3971130137001",
    #     "playerID": "Eyc2R2Jow",
    #     "channelID": "tx"
    # },
    video = episode.get("video")
    videoRefID = video.get("videoRefID")
    videoID = video.get("videoID")
    accountID = video.get("accountID")
    playerID = video.get("playerID")
    # ポリシーキーを取得
    # 　https://players.brightcove.net/4394098883001/MfxS5MXtZ_default/index.min.js
    url = f"https://players.brightcove.net/{accountID}/{playerID}_default/index.min.js"
    buf = urlread(url)
    # {accountId:"4394098883001",policyKey:"BCpkADawqM2XqfdZX45o9xMUoyUbUrkEjt-dMFupSdYwCw6YH7Dgd_Aj4epNSPEGgyBOFGHmLa_IPqbf8qv8CWSZaI_8Cd8xkpoMSNkyZrzzX7_TGRmVjAmZ_q_KxemVvC2gsMyfCqCzRrRx"}
    policykey = re.search(
        r'options:\{accountId:"(.*?)",policyKey:"(.*?)"\}', buf.decode()
    ).group(2)
    # playbackをダウンロード
    if videoRefID:
        # https://edge.api.brightcove.com/playback/v1/accounts/4394098883001/videos/ref%3A18_1390_39076
        url = f"https://edge.api.brightcove.com/playback/v1/accounts/{accountID}/videos/ref%3A{videoRefID}"
    elif videoID:
        # https://edge.api.brightcove.com/playback/v1/accounts/3971130137001/videos/6322259035112?config_id=f0876aa7-0bab-4049-ab23-1b2001ff7c79
        url = f"https://edge.api.brightcove.com/playback/v1/accounts/{accountID}/videos/{videoID}"
    buf = urlread(url, ("accept", f"application/json;pk={policykey}"))
    playback = json.loads(buf)
    sources = playback.get("sources")
    filtered = filter(
        lambda source: source.get("ext_x_version")
        and source.get("src").startswith("https://"),
        sources,
    )
    url = list(filtered)[-1].get("src")
    return url


def play(url):
    url = __url(url)
    xbmcplugin.setResolvedUrl(
        int(sys.argv[1]), succeeded=True, listitem=xbmcgui.ListItem(path=url)
    )


def __add_itemV2(contents):
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
        elif item.get("title"):
            title.append(item.get("title"))
        title = " ".join(title)
        description = []
        if item.get("title"):
            description.append(item.get("title"))
        if item.get("broadcastDateLabel"):
            description.append(item.get("broadcastDateLabel"))
        description = "\n".join(description)
        broadcasterName = item.get("broadcasterName")
        thumbnail = (
            f"https://statics.tver.jp/images/content/thumbnail/episode/small/{id}.jpg"
        )
        url = f"https://statics.tver.jp/content/episode/{id}.json"
        pg = item["_summary"] = {
            "title": title,
            "url": url,
            "date": __date(date),
            "description": description,
            "source": broadcasterName,
            "category": "",
            "duration": "",
            "thumbnail": thumbnail,
            "thumbfile": thumbnail,
            "contentid": id,
        }
        labels = {
            "title": pg["title"],
            "plot": pg["description"],
            "plotoutline": pg["description"],
            "studio": pg["source"],
            "date": __labeldate(pg["date"]),
        }
        listitem = xbmcgui.ListItem(pg["title"])
        listitem.setArt(
            {
                "icon": pg["thumbnail"],
                "thumb": pg["thumbnail"],
                "poster": pg["thumbnail"],
            }
        )
        listitem.setInfo(type="video", infoLabels=labels)
        listitem.setProperty("IsPlayable", "true")
        contextmenu = []
        contextmenu += [("詳細", "Action(Info)")]  # 詳細情報
        listitem.addContextMenuItems(contextmenu, replaceItems=True)
        url = "%s?action=%s&url=%s" % (sys.argv[0], "play", quote_plus(pg["url"]))
        items += [(url, listitem, False)]
    xbmcplugin.addDirectoryItems(int(sys.argv[1]), items, len(contents))


def __add_directory_item(name, action):
    listitem = xbmcgui.ListItem(name)
    url = "%s?action=%s" % (sys.argv[0], action)
    xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, listitem, True)


def __date(itemdate):
    now = datetime.datetime.now()
    year0 = now.strftime("%Y")
    date0 = now.strftime("%m-%d")
    # 日時を抽出
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
    # 抽出結果
    return date


def __labeldate(date):
    # listitem.date用に変換
    m = re.search("^([0-9]{4})-([0-9]{2})-([0-9]{2})", date)
    if m:
        date = "%s.%s.%s" % (m.group(3), m.group(2), m.group(1))
    return date
