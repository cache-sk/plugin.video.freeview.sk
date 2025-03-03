# -*- coding: utf-8 -*-
# Author: cache-sk
# Created on: 10.10.2019
# License: AGPL v.3 https://www.gnu.org/licenses/agpl-3.0.html

import io
import os
import sys
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs
import traceback
import m3u
import epgprocessor
import datetime
import requests.cookies
import re
import xml.etree.ElementTree as ET

from importlib import import_module

try:
    from urllib import urlencode
    from urlparse import parse_qsl
except ImportError:
    from urllib.parse import urlencode
    from urllib.parse import parse_qsl, urlparse

try:
    from xbmc import translatePath
except ImportError:
    from xbmcvfs import translatePath

sys.path.append(os.path.join (os.path.dirname(__file__), 'resources', 'providers'))

_url = sys.argv[0]
_handle = int(sys.argv[1])
_addon = xbmcaddon.Addon()
_profile = translatePath(_addon.getAddonInfo('profile'))
try:
    _profile = _profile.decode("utf-8")
except AttributeError:
    pass

PLAYLIST = 'special://home/addons/'+_addon.getAddonInfo('id')+'/resources/playlist.m3u'

def get_url(**kwargs):
    return '{0}?{1}'.format(_url, urlencode(kwargs, 'utf-8'))

def playlist():
    show_plot = 'true' == _addon.getSetting('genplot')
    with io.open(translatePath(PLAYLIST), 'r', encoding='utf8') as file:
        m3u_data = file.read()
        file.close()    
    channels = m3u.process(m3u_data)
    if show_plot:
        now = datetime.datetime.now()
        epg = epgprocessor.get_epg(channels, now, 1, False)
    for channel in channels:
        list_item = xbmcgui.ListItem(label=channel['name'])
        if show_plot:
            plot = epgprocessor.generate_plot(epg[channel['id']], now, channel['name'], 4) if u'0' != channel['id'] and epg and channel['id'] in epg else u''
            list_item.setInfo('video', {'title': channel['name'], 'plot': plot})
        else:
            list_item.setInfo('video', {'title': channel['name']})
        list_item.setArt({'icon': channel['logo']})
        list_item.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(_handle, channel['url'], list_item, False)
    xbmcplugin.endOfDirectory(_handle)

def info():
    xbmcgui.Dialog().textviewer(_addon.getAddonInfo('name'), _addon.getLocalizedString(30999))
    xbmcplugin.setResolvedUrl(_handle, False, xbmcgui.ListItem())

def extract():
    destination = xbmcgui.Dialog().browseSingle(3, _addon.getAddonInfo('name'), '')
    if destination is not None and destination:
        try:
            if xbmcvfs.exists(destination + 'playlist.m3u'):
                if not xbmcgui.Dialog().yesno(_addon.getAddonInfo('name'), _addon.getLocalizedString(30902)):
                    return
            xbmcvfs.copy(PLAYLIST, destination + 'playlist.m3u')
            xbmcgui.Dialog().ok(_addon.getAddonInfo('name'), _addon.getLocalizedString(30900))
        except Exception as e:
            xbmcgui.Dialog().ok(_addon.getAddonInfo('name'), _addon.getLocalizedString(30901) + "\n" + str(e))
    xbmcplugin.setResolvedUrl(_handle, False, xbmcgui.ListItem())

def newPisc(pisc):
    ver = pisc.getAddonInfo("version").split(".")
    return int(ver[0]) >= 20 and int(ver[1]) >= 8 

def settingToListItem(path):
    tree = ET.parse(path)
    #root = tree.getroot()
    name = tree.findall("//setting[@id='kodi_addon_instance_name']")[0].text
    return xbmcgui.ListItem(label = name, path = path)

def getNewPiscSettings(pisc):
    pprofile = translatePath(pisc.getAddonInfo('profile'))
    ppfiles = os.listdir(pprofile)
    psettings = [settingToListItem(os.path.join(pprofile,f)) for f in ppfiles if re.search("^instance-settings-\d+.xml$", f)] #TODO os.path.isfile?
    xmlLI = xbmcgui.Dialog().select(heading = _addon.getLocalizedString(30904), list = psettings)
    if xmlLI == -1:
        xbmcgui.Dialog().ok(_addon.getAddonInfo('name'), _addon.getLocalizedString(30905))
        return None
    return psettings[xmlLI].getPath()

def setXmlValue(tree, name, value):
    node = tree.findall("//setting[@id='"+name+"']")[0]
    node.text = str(value)

def setpisc():
    try:
        pisc = xbmcaddon.Addon('pvr.iptvsimple')
    except:
        xbmcgui.Dialog().ok(_addon.getAddonInfo('name'), _addon.getLocalizedString(30010))
        xbmcplugin.setResolvedUrl(_handle, False, xbmcgui.ListItem())
        return
    
    if not xbmcgui.Dialog().yesno(_addon.getAddonInfo('name'), _addon.getLocalizedString(30998)):
        xbmcplugin.setResolvedUrl(_handle, False, xbmcgui.ListItem())
        return

    if newPisc(pisc):
        piscProfileFile = getNewPiscSettings(pisc)
        if piscProfileFile is not None:
            tree = ET.parse(piscProfileFile)
            setXmlValue(tree, 'm3uPathType','0')
            setXmlValue(tree, 'm3uPath',translatePath(PLAYLIST))
            setXmlValue(tree, 'startNum','1')
            setXmlValue(tree, 'logoPathType','1')
            setXmlValue(tree, 'logoBaseUrl','')
            setXmlValue(tree, 'logoFromEpg','1')
            with open(piscProfileFile, 'wb') as f:
                tree.write(f)
        else:
            xbmcplugin.setResolvedUrl(_handle, False, xbmcgui.ListItem())
            return

    else:
        pisc.setSetting('m3uPathType','0')
        pisc.setSetting('m3uPath',translatePath(PLAYLIST))
        pisc.setSetting('startNum','1')
        pisc.setSetting('logoPathType','1')
        pisc.setSetting('logoBaseUrl','')
        pisc.setSetting('logoFromEpg','1')

    xbmcgui.Dialog().ok(_addon.getAddonInfo('name'), _addon.getLocalizedString(30906))
    xbmcplugin.setResolvedUrl(_handle, False, xbmcgui.ListItem())

def setpiscgenepg():
    try:
        pisc = xbmcaddon.Addon('pvr.iptvsimple')
    except:
        xbmcgui.Dialog().ok(_addon.getAddonInfo('name'), _addon.getLocalizedString(30010))
        xbmcplugin.setResolvedUrl(_handle, False, xbmcgui.ListItem())
        return

    if not xbmcgui.Dialog().yesno(_addon.getAddonInfo('name'), _addon.getLocalizedString(30998)):
        xbmcplugin.setResolvedUrl(_handle, False, xbmcgui.ListItem())
        return

    _addon.setSetting('genepg', 'true')

    path = os.path.join(_profile, 'epg.xml')

    if newPisc(pisc):
        piscProfileFile = getNewPiscSettings(pisc)
        if piscProfileFile is not None:
            tree = ET.parse(piscProfileFile)
            setXmlValue(tree, 'epgCache','false')
            setXmlValue(tree, 'epgPath',path)
            setXmlValue(tree, 'epgPathType','0')
            setXmlValue(tree, 'epgTimeShift','0')
            setXmlValue(tree, 'epgTSOverride','false')
            with open(piscProfileFile, 'wb') as f:
                tree.write(f)
        else:
            xbmcplugin.setResolvedUrl(_handle, False, xbmcgui.ListItem())
            return
    else:
        pisc.setSetting('epgCache','false')
        pisc.setSetting('epgPath',path)
        pisc.setSetting('epgPathType','0')
        pisc.setSetting('epgTimeShift','0')
        pisc.setSetting('epgTSOverride','false')

    xbmcgui.Dialog().ok(_addon.getAddonInfo('name'), _addon.getLocalizedString(30906))
    xbmcplugin.setResolvedUrl(_handle, False, xbmcgui.ListItem())

def regenepg():
    _addon.setSetting('genepg', 'false')
    _addon.setSetting('genepg', 'true')
    xbmcgui.Dialog().ok(_addon.getAddonInfo('name'), _addon.getLocalizedString(30903))

def setpiscepg():
    try:
        pisc = xbmcaddon.Addon('pvr.iptvsimple')
    except:
        xbmcgui.Dialog().ok(_addon.getAddonInfo('name'), _addon.getLocalizedString(30010))
        xbmcplugin.setResolvedUrl(_handle, False, xbmcgui.ListItem())
        return
    
    user = xbmcgui.Dialog().input(_addon.getLocalizedString(30011), '', xbmcgui.INPUT_ALPHANUM)
    email = xbmcgui.Dialog().input(_addon.getLocalizedString(30012), '', xbmcgui.INPUT_ALPHANUM)

    if not xbmcgui.Dialog().yesno(_addon.getAddonInfo('name'), _addon.getLocalizedString(30998)):
        xbmcplugin.setResolvedUrl(_handle, False, xbmcgui.ListItem())
        return

    pisc.setSetting('epgCache','true')
    pisc.setSetting('epgPathType','1')
    pisc.setSetting('epgTimeShift','0')
    pisc.setSetting('epgTSOverride','false')
    pisc.setSetting('epgUrl','https://phazebox.com/epg.php?user=' + user + '&email=' + email)


    xbmcplugin.setResolvedUrl(_handle, False, xbmcgui.ListItem())

def settings():
    _addon.openSettings()
    xbmcplugin.setResolvedUrl(_handle, False, xbmcgui.ListItem())

def piscsettings():
    try:
        pisc = xbmcaddon.Addon('pvr.iptvsimple')
    except:
        xbmcgui.Dialog().ok(_addon.getAddonInfo('name'), _addon.getLocalizedString(30010))
        xbmcplugin.setResolvedUrl(_handle, False, xbmcgui.ListItem())
        return
    pisc.openSettings()
    xbmcplugin.setResolvedUrl(_handle, False, xbmcgui.ListItem())

def menu():
    xbmcplugin.addDirectoryItem(_handle, get_url(action='playlist'), xbmcgui.ListItem(label=_addon.getLocalizedString(30000)), True)
    xbmcplugin.addDirectoryItem(_handle, get_url(action='info'), xbmcgui.ListItem(label=_addon.getLocalizedString(30001)), False)
    xbmcplugin.addDirectoryItem(_handle, get_url(action='extract'), xbmcgui.ListItem(label=_addon.getLocalizedString(30002)), False)
    xbmcplugin.addDirectoryItem(_handle, get_url(action='setpisc'), xbmcgui.ListItem(label=_addon.getLocalizedString(30003)), False)
    xbmcplugin.addDirectoryItem(_handle, get_url(action='setpiscgenepg'), xbmcgui.ListItem(label=_addon.getLocalizedString(30007)), False)
    xbmcplugin.addDirectoryItem(_handle, get_url(action='regenepg'), xbmcgui.ListItem(label=_addon.getLocalizedString(30008)), False)
    #xbmcplugin.addDirectoryItem(_handle, get_url(action='setpiscepg'), xbmcgui.ListItem(label=_addon.getLocalizedString(30006)), False)
    xbmcplugin.addDirectoryItem(_handle, get_url(action='settings'), xbmcgui.ListItem(label=_addon.getLocalizedString(30004)), False)
    xbmcplugin.addDirectoryItem(_handle, get_url(action='piscsettings'), xbmcgui.ListItem(label=_addon.getLocalizedString(30005)), False)
    xbmcplugin.endOfDirectory(_handle)

def router(paramstring):
    try:
        params = dict(parse_qsl(paramstring))
        if params:
            if 'provider' in params:
                epgprocessor.get_info(_addon, xbmcgui)
                provider = params['provider']
                module = import_module(provider)
                module.play(_handle, _addon, params)
            elif 'action' in params:
                globals()[params['action']]()
            else:
                menu()
        else:
            menu()
    except Exception as e:
        xbmcgui.Dialog().ok(_addon.getAddonInfo('name'), str(e))
        traceback.print_exc()

if __name__ == '__main__':
    router(sys.argv[2][1:])