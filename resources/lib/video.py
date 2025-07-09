import sys
from typing import TypedDict

import xbmcgui
import xbmcplugin
from resources.lib.http import get_json


class PlayableMedia(TypedDict):
    video_url: str
    subtitle_urls: list[str]


def _get_video(episode_url: str) -> PlayableMedia:
    episode = get_json(episode_url)
    streaks = episode["streaks"]
    video_ref_id = streaks.get("videoRefID")
    project_id = streaks["projectID"]
    streaks_url = f"https://playback.api.streaks.jp/v1/projects/{project_id}/medias/ref:{video_ref_id}"
    streaks_data = get_json(streaks_url, {"origin": "https://tver.jp/"})
    video_url = streaks_data["sources"][0]["src"]
    subtitle_urls = [
        track["src"]
        for track in streaks_data.get("tracks", [])
        if track.get("kind") == "captions"
    ]
    return {"video_url": video_url, "subtitle_urls": subtitle_urls}


def play(url: str):
    playable_media = _get_video(url)
    video_url = playable_media["video_url"]
    subtitle_urls = playable_media["subtitle_urls"]
    listitem = xbmcgui.ListItem(path=video_url)
    if len(subtitle_urls) > 0:
        listitem.setSubtitles(subtitle_urls)
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), succeeded=True, listitem=listitem)
