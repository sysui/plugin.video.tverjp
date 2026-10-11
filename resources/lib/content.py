import re
import sys
from datetime import datetime
from typing import Any, TypedDict
from urllib.parse import quote_plus, urlencode

import xbmcaddon
import xbmcgui
import xbmcplugin


ADDON = xbmcaddon.Addon()


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
    isEndingSoon: bool


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
    rank: int


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
            title = f"{broadcastDateLabelForTitle} {item['seriesTitle']}  {item['title']}".strip()
            # Year 2038 problem
            endAtStr = (
                datetime.fromtimestamp(item["endAt"]).strftime("%Y-%m-%d %H:%M:%S")
                if item["endAt"] < 2147483647
                else "期限なし"
            )

            description = (
                f"{item['seriesTitle']}\n"
                f"{item['title']}\n\n"
                f"{item['broadcastDateLabel']}\n"
                f"配信終了: {endAtStr}\n"
                f"字幕: {'あり' if item['isSubtitle'] else 'なし'}\n"
                f"{item['broadcasterName']}"
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
            search_serise_title = "{}?action={}&keyword={}".format(
                sys.argv[0], "search_with_keyword_params", item["seriesTitle"]
            )
            command_search = f"Container.Update({search_serise_title})"
            context_menu_items = [("この番組名で検索", command_search)]
            if ADDON.getSettingString("destination_url").strip():
                send_url = "{}?{}".format(
                    sys.argv[0],
                    urlencode(
                        {
                            "action": "send_to_server",
                            "url": f"https://tver.jp/episodes/{id}",
                        }
                    ),
                )
                command_send = f"RunPlugin({send_url})"
                context_menu_items.append(
                    ("番組URLをサーバーへ送信", command_send)
                )
            listitem.addContextMenuItems(context_menu_items)
            episode_url = f"https://statics.tver.jp/content/episode/{id}.json"
            url = "{}?action={}&url={}".format(
                sys.argv[0], "play", quote_plus(episode_url)
            )
            items.append((url, listitem, False))
    xbmcplugin.addDirectoryItems(int(sys.argv[1]), items)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
