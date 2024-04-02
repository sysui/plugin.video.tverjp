import sys
from urllib.parse import quote_plus

import xbmcgui
import xbmcplugin


def show_top():
    _add_dashboard()
    listitem = xbmcgui.ListItem("検索 / 検索履歴")
    url = "{}?action={}".format(sys.argv[0], "show_keyword_history")
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
            "name": "全て 新着",
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
        url = "{}?action={}&dashboard_url={}".format(
            sys.argv[0],
            "dashboard",
            quote_plus(dashboard_endpoint["url"]),
        )
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, listitem, True)
