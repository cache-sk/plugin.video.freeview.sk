# -*- coding: utf-8 -*-
# Author: cache-sk
# Source: https://github.com/curif/cumulus-tv-m3u8-loader/blob/master/src/m3u8_loader.py
# Created on: 19.11.2019
# License: AGPL v.3 https://www.gnu.org/licenses/agpl-3.0.html

import re

m3u_regex = '(.+?),(.+)\s*(.+)\s*'
name_regex = '.*?tvg-name=[\'"](.*?)[\'"]'
group_regex = '.*?group-title=[\'"](.*?)[\'"]'
logo_regex = '.*?tvg-logo=[\'"](.*?)[\'"]'
lang_regex = '.*?tvg-language=[\'"](.*?)[\'"]'
country_regex = '.*?tvg-country=[\'"](.*?)[\'"]'
id_regex = '.*?tvg-id=[\'"](.*?)[\'"]'

m3uRe = re.compile(m3u_regex)
nameRe = re.compile(name_regex)
logoRe = re.compile(logo_regex)
langRe = re.compile(lang_regex)
countryRe = re.compile(country_regex)
idRe = re.compile(id_regex)
groupRe = re.compile(group_regex)

def process(m3u):
  match = m3uRe.findall(m3u)

  channels = []

  for extInfData, name, url in match:

    if not url.startswith('#'):

        id = regParse(idRe, extInfData)
        logo = regParse(logoRe, extInfData)
        country = regParse(countryRe, extInfData)
        group = regParse(groupRe, extInfData)
        lang = regParse(langRe, extInfData)

        if name is None or name == "":
            name = regParse(nameRe, extInfData)

        channelData = {
            "id": id,
            "name": name,
            "logo": logo,
            "url": url,
            "lang": lang,
            "country": country
        }

        channels.append(channelData)

  return channels

def regParse(parser, data):
  foundString = parser.search(data)
  if foundString:
    #print "regParse result", x.group(1)
    return foundString.group(1).strip()
  return None