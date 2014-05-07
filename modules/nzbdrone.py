import cherrypy
import htpc
from urllib import quote
from urllib2 import urlopen, Request
from json import loads
import logging


class NZBDrone:
    def __init__(self):
        self.logger = logging.getLogger('modules.sickbeard')
        htpc.MODULES.append({
            'name': 'NZBDrone',
            'id': 'nzbdrone',
            'test': htpc.WEBDIR + 'nzbdrone/status',
            'fields': [
                {'type': 'bool', 'label': 'Enable', 'name': 'nzbdrone_enable'},
                {'type': 'text', 'label': 'Menu name', 'name': 'nzbdrone_name'},
                {'type': 'text', 'label': 'IP / Host', 'placeholder':'localhost','name': 'nzbdrone_host'},
                {'type': 'text', 'label': 'Port', 'placeholder':'8989', 'name': 'nzbdrone_port'},
                {'type': 'text', 'label': 'Basepath', 'placeholder':'/' ,'name': 'nzbdrone_basepath'},
                {'type': 'text', 'label': 'API key', 'name': 'nzbdrone_apikey'},
                {'type': 'bool', 'label': 'Use SSL', 'name': 'nzbdrone_ssl'}
        ]})

    @cherrypy.expose()
    def index(self):
        return htpc.LOOKUP.get_template('nzbdrone.html').render(scriptname='nzbdrone')

#TODO
    @cherrypy.expose()
    def view(self, tvdbid):
        if not (tvdbid.isdigit()):
            raise cherrypy.HTTPError("500 Error", "Invalid show ID.")
            self.logger.error("Invalid show ID was supplied: " + str(tvdbid))
            return False

        return htpc.LOOKUP.get_template('sickbeard_view.html').render(scriptname='sickbeard_view', tvdbid=tvdbid)


    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def status(self, nzbdrone_host, nzbdrone_port, nzbdrone_apikey, nzbdrone_basepath, nzbdrone_ssl = False, **kwargs):
        ssl = 's' if nzbdrone_ssl else ''
        self.logger.debug("Testing connectivity")
        if not (nzbdrone_basepath.endswith('/')):
                nzbdrone_basepath += "/"
        url = 'http' + ssl + '://' + nzbdrone_host + ':' + nzbdrone_port + nzbdrone_basepath + 'api/system/status'

        try:
            request = Request(url)
            request.add_header("X-Api-Key", nzbdrone_apikey)
            self.logger.debug("Trying to contact nzbdrone via " + url)
            return loads(urlopen(request, timeout=10).read())

        except:
            self.logger.error("Unable to contact sickbeard via " + url)
            return

#TODO
    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def GetShowList(self):
        self.logger.debug("Fetching Show list")
        return self.fetch('series')

#TODO
    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def GetNextAired(self):
        self.logger.debug("Fetching Next Aired Episodes")
        return self.fetch('future')

#TODO
    @cherrypy.expose()
    def GetBanner(self, tvdbid):
        self.logger.debug("Fetching Banner")
        cherrypy.response.headers['Content-Type'] = 'image/jpeg'
        return self.fetch('show.getbanner&tvdbid=' + tvdbid, True)

#TODO
    @cherrypy.expose()
    def GetPoster(self, tvdbid):
        self.logger.debug("Fetching Poster")
        cherrypy.response.headers['Content-Type'] = 'image/jpeg'
        return self.fetch('show.getposter&tvdbid=' + tvdbid, True)

#TODO
    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def GetHistory(self, limit=''):
        self.logger.debug("Fetching History")
        return self.fetch('history&limit=' + limit)

#TODO
    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def GetLogs(self):
        self.logger.debug("Fetching Logs")
        return self.fetch('logs&min_level=info')

#TODO
    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def AddShow(self, tvdbid):
        self.logger.debug("Adding a Show")
        return self.fetch('show.addnew&tvdbid=' + tvdbid)

#TODO
    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def GetShow(self, tvdbid):
        self.logger.debug("Fetching Show")
        return self.fetch('show&tvdbid=' + tvdbid)

#TODO
    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def GetEpisode(self, strShowID, strSeason, strEpisode):
        return self.fetch("episode&tvdbid=" + strShowID + "&season=" + strSeason + "&episode=" + strEpisode + "&full_path=1")

#TODO
    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def GetSeason(self, tvdbid, season):
        self.logger.debug("Fetching Season")
        return self.fetch('show.seasons&tvdbid=' + tvdbid + '&season=' + season)

#TODO
    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def SearchEpisodeDownload(self, tvdbid, season, episode):
        self.logger.debug("Fetching Episode Downloads")
        return self.fetch('episode.search&tvdbid=' + tvdbid + '&season=' + season + '&episode=' + episode, False, 45)

#TODO
    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def ForceFullUpdate(self, tvdbid):
        self.logger.debug("Force full update for tvdbid " + tvdbid)
        return self.fetch("show.update&tvdbid=" + tvdbid)

#TODO
    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def RescanFiles(self, tvdbid):
        self.logger.debug("Rescan all local files for tvdbid " + tvdbid)
        return self.fetch("show.refresh&tvdbid=" + tvdbid)

#TODO
    @cherrypy.expose()
    def SearchShow(self, query):
        try:
            url = 'http://www.thetvdb.com/api/GetSeries.php?seriesname=' + quote(query)
            return urlopen(url, timeout=10).read()
        except:
            return

#TODO
    def fetch(self, cmd, img=False, timeout=10):
        try:
            host = htpc.settings.get('nzbdrone_host', '')
            port = str(htpc.settings.get('nzbdrone_port', ''))
            apikey = htpc.settings.get('nzbdrone_apikey', '')
            ssl = 's' if htpc.settings.get('nzbdrone_ssl', 0) else ''
            nzbdrone_basepath = htpc.settings.get('nzbdrone_basepath', '/')

            if not (nzbdrone_basepath.endswith('/')):
                nzbdrone_basepath += "/"
            url = 'http' + ssl + '://' + host + ':' + str(port) + nzbdrone_basepath + 'api/' + cmd
            request = Request(url)
            request.add_header("X-Api-Key", apikey)

            self.logger.debug("Fetching information from: " + url)

            if (img == True):
                return urlopen(request, timeout=timeout).read()

            return loads(urlopen(request, timeout=timeout).read())
        except:
            self.logger.error("Unable to fetch information")
            return
