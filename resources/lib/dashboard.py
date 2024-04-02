from resources.lib.content import add_contents
from resources.lib.http import get_json


def dashboard(url: str):
    data = get_json(url, {"x-tver-platform-type": "web"})
    contents = data["result"]["contents"]["contents"]
    add_contents(contents)
