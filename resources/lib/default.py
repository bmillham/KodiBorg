import xbmcaddon
import xbmcgui

addon = xbmcaddon.Addon()
addonname = addon.getAddonInfo('name')

xbmcgui.Dialog().ok(addonname, "This is my test")
