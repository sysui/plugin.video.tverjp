import sys
from urllib.parse import parse_qs

from resources.lib.dashboard import dashboard
from resources.lib.history import remove_all_keyword, remove_keyword
from resources.lib.search import show_keyword_history, show_keyword_search
from resources.lib.top import show_top
from resources.lib.video import play


def router():
    args = parse_qs(sys.argv[2][1:])
    action = args.get("action", [None])[0]

    if action is None:
        show_top()

    elif action == "dashboard":
        dashboard_url = args.get("dashboard_url", [None])[0]
        if dashboard_url is not None:
            dashboard(dashboard_url)

    elif action == "show_keyword_history":
        show_keyword_history()

    elif action == "show_keyword_search":
        show_keyword_search()

    elif action == "search_with_keyword_params":
        keyword = args.get("keyword", [None])[0]
        if keyword is not None:
            show_keyword_search(keyword)

    elif action == "remove_keyword":
        keywords = args.get("keyword", None)
        if keywords is not None:
            remove_keyword(keywords)

    elif action == "remove_all_keyword":
        remove_all_keyword()

    elif action == "play":
        url = args.get("url", [None])[0]
        if url is not None:
            play(url)
