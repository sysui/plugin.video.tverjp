import os
import sys
from urllib.parse import urlencode

import xbmcaddon
import xbmcgui
import xbmcplugin
from resources.lib.content import add_contents
from resources.lib.history import append_keyword_history, get_keyword_history
from resources.lib.http import get_json
from resources.lib.token import get_token
from resources.lib.ui.prompt import prompt
from xbmcvfs import translatePath


def _keyword_search(platform_uid: str, platform_token: str, keyword: str):
    endpoint = "https://platform-api.tver.jp/service/api/v2/callKeywordSearch"
    params = urlencode(
        {
            "platform_uid": platform_uid,
            "platform_token": platform_token,
            "keyword": keyword,
        }
    )
    url = f"{endpoint}?{params}"
    return get_json(url, {"x-tver-platform-type": "web"})


def show_keyword_search(keyword: str = ""):
    keyword = keyword or prompt("検索")
    if not keyword:
        return
    append_keyword_history(keyword)
    token = get_token()
    data = _keyword_search(token["platform_uid"], token["platform_token"], keyword)
    contents = data["result"]["contents"]
    if contents:
        add_contents(contents)


def show_keyword_history():
    listitem = xbmcgui.ListItem("新しい検索")
    listitem.setArt(
        {
            "icon": os.path.join(
                translatePath(xbmcaddon.Addon().getAddonInfo("path")),
                "resources",
                "media",
                "material-symbols_search.png",
            )
        }
    )
    url = "{}?action={}".format(sys.argv[0], "show_keyword_search")
    xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, listitem, True)

    for keyword in get_keyword_history():
        listitem = xbmcgui.ListItem(keyword)
        listitem.setArt(
            {
                "icon": os.path.join(
                    translatePath(xbmcaddon.Addon().getAddonInfo("path")),
                    "resources",
                    "media",
                    "material-symbols_saved-search.png",
                )
            }
        )
        url = "{}?action={}&keyword={}".format(
            sys.argv[0],
            "search_with_keyword_params",
            keyword,
        )
        remove_keyword_url = "{}?action={}&keyword={}".format(
            sys.argv[0], "remove_keyword", keyword
        )
        command_remove = f"Container.Update({remove_keyword_url})"
        remove_all_keyword_url = "{}?action={}".format(
            sys.argv[0],
            "remove_all_keyword",
        )
        command_remove_all = f"Container.Update({remove_all_keyword_url})"
        listitem.addContextMenuItems(
            [
                ("この検索ワードを削除", command_remove),
                ("全ての検索ワードを削除", command_remove_all),
            ]
        )
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, listitem, True)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
