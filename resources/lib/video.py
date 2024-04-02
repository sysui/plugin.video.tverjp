import json
import re
import sys

import requests
import xbmcgui
import xbmcplugin
from resources.lib.http import get_json


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
    playback = get_json(url, {"accept": f"application/json;pk={policykey}"})
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
