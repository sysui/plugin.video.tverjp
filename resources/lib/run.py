import sys
from urllib.parse import parse_qs

from resources.lib.browse import (
    play,
    show_keyword_search,
    show_newer_all,
    show_newer_drama,
    show_newer_variety,
    show_ranking_all,
    show_ranking_drama,
    show_ranking_variety,
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

    elif action == "show_ranking_all":
        show_ranking_all()

    elif action == "show_ranking_drama":
        show_ranking_drama()

    elif action == "show_ranking_variety":
        show_ranking_variety()

    elif action == "show_newer_all":
        show_newer_all()

    elif action == "show_newer_drama":
        show_newer_drama()

    elif action == "show_newer_variety":
        show_newer_variety()

    elif action == "show_keyword_search":
        show_keyword_search()

    elif action == "search_with_keyword_params":
        (keyword := args.get("keyword")) and show_keyword_search(keyword)

    elif action == "play":
        play(args["url"])
