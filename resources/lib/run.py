import sys
from urllib.parse import parse_qs

from resources.lib.browse import (
    dashboard,
    play,
    show_keyword_search,
    show_top,
)


def run():
    args = parse_qs(sys.argv[2][1:], keep_blank_values=True)
    for key in args.keys():
        args[key] = args[key][0]
    args.update(None or {})
    action = args.get("action", "")

    if action == "":
        show_top()

    elif action == "dashboard":
        (dashboard_url := args.get("dashboard_url")) and dashboard(dashboard_url)

    elif action == "show_keyword_search":
        show_keyword_search()

    elif action == "search_with_keyword_params":
        (keyword := args.get("keyword")) and show_keyword_search(keyword)

    elif action == "play":
        play(args["url"])
