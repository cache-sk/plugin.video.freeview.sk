import datetime
import io
import os
import skylink
import m3u
import xbmc
import xbmcaddon
import traceback

class SkylinkMonitor(xbmc.Monitor):
    _addon = None
    _next_update = 0

    def __init__(self):
        xbmc.Monitor.__init__(self)
        self._addon = xbmcaddon.Addon()
        ts = self._addon.getSetting('genepg_next_update')
        self._next_update = datetime.datetime.now() if ts == '' else datetime.datetime.fromtimestamp(float(ts))

    def __del__(self):
        print 'service destroyed'

    def notify(self, text, error=False):
        text = text.encode("utf-8") if type(text) is unicode else text
        icon = 'DefaultIconError.png' if error else ''
        xbmc.executebuiltin('Notification("%s","%s",5000,%s)' % (self._addon.getAddonInfo('name').encode("utf-8"), text, icon))

    def onSettingsChanged(self):
        self._addon = xbmcaddon.Addon()  # refresh for updated settings!
        if not self.abortRequested():
            try:
                if self.update():
                    self.notify(self._addon.getLocalizedString(30092))
            except Exception as e:
                traceback.print_exc()
                self.notify(str(e), True)

    def schedule_next(self, seconds):
        dt = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
        print 'Next update %s' % dt
        self._next_update = dt

    def update(self):
        gse = 'true' == self._addon.getSetting('genepg')
        if not gse:
            return False

        _profile = xbmc.translatePath(self._addon.getAddonInfo('profile')).decode("utf-8")
        _playlist = 'special://home/addons/'+self._addon.getAddonInfo('id')+'/resources/playlist.m3u'
        if not os.path.exists(_profile):
            os.makedirs(_profile)
        path = os.path.join(_profile, 'epg.xml')

        with io.open(xbmc.translatePath(_playlist), 'r', encoding='utf8') as file:
            m3u_data = file.read()
            file.close()    
        channels = m3u.process(m3u_data)
        now = datetime.datetime.now()
        epg = skylink.get_epg(channels)
        skylink.generate_xmltv(channels,epg,path)

        return True

    def tick(self):
        if datetime.datetime.now() > self._next_update:
            try:
                self.schedule_next(12 * 60 * 60)
                self.update()
            except Exception as e:
                traceback.print_exc()
                self.notify(str(e), True)

    def save(self):
        self._addon.setSetting('genepg_next_update', str(time.mktime(self._next_update.timetuple())))
        print 'Saving next update %s' % self._next_update


if __name__ == '__main__':
    monitor = SkylinkMonitor()
    while not monitor.abortRequested():
        if monitor.waitForAbort(10):
            monitor.save()
            break
        monitor.tick()
