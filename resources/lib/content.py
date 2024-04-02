import re
import sys
from datetime import datetime
from typing import Any, TypedDict
from urllib.parse import quote_plus

import xbmcgui
import xbmcplugin


class EpisodeContent(TypedDict):
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


class LiveContent(TypedDict):
    id: str
    version: int
    title: str
    startAt: int
    endAt: int
    liveType: int
    dvr: dict[Any, Any]
    isNHKContent: bool
    onairStartAt: int
    onairEndAt: int
    allowPlatforms: list[str]
    episodeCc: int
    seriesTitle: str
    isDVRNow: bool


class Content(TypedDict):
    type: str
    content: EpisodeContent


def add_contents(contents: list[Content]):
    items: list[tuple[str, Any, bool]] = []
    for data in contents:
        if data["type"] == "episode":
            item = data["content"]
            id = item["id"]
            broadcastDateLabelForTitle = re.sub(
                r"(^\d{1,2})月(\d{1,2})日(.+)",
                r"\1/\2\3",
                item["broadcastDateLabel"].replace("放送分", ""),
            )
            title = (
                f'{broadcastDateLabelForTitle} {item["seriesTitle"]}  {item["title"]}'
            )
            # Year 2038 problem
            endAtStr = (
                datetime.fromtimestamp(item["endAt"]).strftime("%Y-%m-%d %H:%M:%S")
                if item["endAt"] < 2147483647
                else "期限なし"
            )

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
            thumbnail = f"https://statics.tver.jp/images/content/thumbnail/episode/small/{id}.jpg"
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
            items.append((url, listitem, False))
    xbmcplugin.addDirectoryItems(int(sys.argv[1]), items)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
