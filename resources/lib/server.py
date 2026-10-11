from urllib.parse import urlparse

import requests
import xbmcaddon
import xbmcgui


ADDON = xbmcaddon.Addon()
NOTIFICATION_TITLE = "TVer"


def send_to_server(content_url: str):
    destination_url = ADDON.getSettingString("destination_url").strip()
    if not destination_url:
        xbmcgui.Dialog().notification(
            NOTIFICATION_TITLE,
            "送信先URLを設定してください",
            xbmcgui.NOTIFICATION_WARNING,
        )
        return

    parsed_destination_url = urlparse(destination_url)
    if parsed_destination_url.scheme != "https" or not parsed_destination_url.netloc:
        xbmcgui.Dialog().notification(
            NOTIFICATION_TITLE,
            "https://から始まるURLを設定してください",
            xbmcgui.NOTIFICATION_ERROR,
        )
        return

    try:
        response = requests.post(
            destination_url,
            json={"url": content_url},
            timeout=5,
        )
        response.raise_for_status()
    except requests.RequestException:
        xbmcgui.Dialog().notification(
            NOTIFICATION_TITLE,
            "送信に失敗しました",
            xbmcgui.NOTIFICATION_ERROR,
        )
        return

    xbmcgui.Dialog().notification(
        NOTIFICATION_TITLE,
        "送信しました",
        xbmcgui.NOTIFICATION_INFO,
    )
