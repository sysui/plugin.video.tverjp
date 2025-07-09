from typing import TypedDict

import requests
from urllib3.util import SKIP_HEADER


class Token(TypedDict):
    platform_uid: str
    platform_token: str


def get_token() -> Token:
    URL_TOKEN_SERVICE = (
        "https://platform-api.tver.jp/v2/api/platform_users/browser/create"
    )
    headers = {
        "User-Agent": SKIP_HEADER,
        "Content-Type": "application/x-www-form-urlencoded",
    }
    r = requests.post(URL_TOKEN_SERVICE, data="device_type=pc", headers=headers)
    data = r.json()
    platform_uid = data["result"]["platform_uid"]
    platform_token = data["result"]["platform_token"]
    return {"platform_uid": platform_uid, "platform_token": platform_token}
