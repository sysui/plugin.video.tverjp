import xbmcaddon

from urllib.request import build_opener
from urllib.request import HTTPError


class Const:
    ADDON = xbmcaddon.Addon()
    STR = ADDON.getLocalizedString


def urlread(url, *headers):
    opener = build_opener()
    h = [("User-Agent", "")]
    for header in headers:
        h.append(header)
    opener.addheaders = h
    try:
        response = opener.open(url)
        buf = response.read()
        response.close()
    except HTTPError as e:
        # log("HTTPError: url=", url, error=True)
        # log("HTTPError: code=", e.code, error=True)
        # log("HTTPError: reason=", e.reason, error=True)
        # log("HTTPError: read=", e.read(), error=True)
        buf = ""
    return buf
