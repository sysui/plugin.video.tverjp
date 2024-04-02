import xbmcgui


def prompt(heading: str = "") -> str:
    kb = xbmcgui.Dialog().input(heading)
    return kb or ""
