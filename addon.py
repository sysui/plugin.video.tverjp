import sys

from resources.lib.browse import (
    update_query,
    show_top,
    show_ranking_all,
    show_ranking_drama,
    show_ranking_variety,
    show_newer_all,
    show_newer_drama,
    show_newer_variety,
    play,
)


args = update_query(sys.argv[2][1:])
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

elif action == "play":
    play(args["url"])
