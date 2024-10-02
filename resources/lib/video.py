import json
import re
import sys
from typing import TypedDict

import requests
import xbmcgui
import xbmcplugin
from resources.lib.http import get_json


class PlayableMedia(TypedDict):
    video_url: str
    subtitle_urls: list[str]


def _get_video(url: str) -> PlayableMedia:
    buf = requests.get(url, headers={"User-Agent": ""}).content
    episode = json.loads(buf)
    video = episode["video"]
    videoRefID = video.get("videoRefID")
    videoID = video.get("videoID")
    accountID = video["accountID"]
    playerID = video["playerID"]
    url = f"https://players.brightcove.net/{accountID}/{playerID}_default/index.min.js"
    buf = requests.get(url, headers={"User-Agent": ""}).content
    match = re.search(r'options:\{accountId:"(.*?)",policyKey:"(.*?)"\}', buf.decode())
    if match is None:
        raise Exception
    policykey = match.group(2)
    if not isinstance(policykey, str):
        raise ValueError
    if videoRefID:
        url = f"https://edge.api.brightcove.com/playback/v1/accounts/{accountID}/videos/ref%3A{videoRefID}"
    elif videoID:
        url = f"https://edge.api.brightcove.com/playback/v1/accounts/{accountID}/videos/{videoID}"
    playback = get_json(url, {"accept": f"application/json;pk={policykey}"})
    subtitle_urls = []
    if text_tracks := playback["text_tracks"][0]["sources"]:
        subtitle_urls = [text_track["src"] for text_track in text_tracks]
    filtered_video_url_list = [
        source
        for source in playback.get("sources", [])
        if source.get("ext_x_version") and source.get("src").startswith("https://")
    ]
    video_url = list(filtered_video_url_list)[-1].get("src")
    return {"video_url": video_url, "subtitle_urls": subtitle_urls}


def play(url: str):
    playable_media = _get_video(url)
    video_url = playable_media["video_url"]
    subtitle_urls = playable_media["subtitle_urls"]
    listitem = xbmcgui.ListItem(path=video_url)
    if len(subtitle_urls) > 0:
        listitem.setSubtitles(subtitle_urls)
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), succeeded=True, listitem=listitem)
