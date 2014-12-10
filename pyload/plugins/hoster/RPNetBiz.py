# -*- coding: utf-8 -*-

import re

from pyload.plugins.Hoster import Hoster
from pyload.utils import json_loads


class RPNetBiz(Hoster):
    __name__    = "RPNetBiz"
    __type__    = "hoster"
    __version__ = "0.10"

    __description__ = """RPNet.biz hoster plugin"""
    __license__     = "GPLv3"

    __pattern__ = r'https?://.*rpnet\.biz'
    __authors__     = [("Dman", "dmanugm@gmail.com")]


    def setup(self):
        self.chunkLimit = -1
        self.resumeDownload = True


    def process(self, pyfile):
        if re.match(self.__pattern__, pyfile.url):
            link_status = {'generated': pyfile.url}
        elif not self.account:
            # Check account
            self.logError(_("Please enter your %s account or deactivate this plugin") % "rpnet")
            self.fail(_("No rpnet account provided"))
        else:
            (user, data) = self.account.selectAccount()

            self.logDebug("Original URL: %s" % pyfile.url)
            # Get the download link
            res = self.load("https://premium.rpnet.biz/client_api.php",
                            get={"username": user,
                                 "password": data['password'],
                                 "action": "generate",
                                 "links": pyfile.url})

            self.logDebug("JSON data: %s" % res)
            link_status = json_loads(res)['links'][0]  # get the first link... since we only queried one

            # Check if we only have an id as a HDD link
            if 'id' in link_status:
                self.logDebug("Need to wait at least 30 seconds before requery")
                self.setWait(30)  # wait for 30 seconds
                self.wait()
                # Lets query the server again asking for the status on the link,
                # we need to keep doing this until we reach 100
                max_tries = 30
                my_try = 0
                while (my_try <= max_tries):
                    self.logDebug("Try: %d ; Max Tries: %d" % (my_try, max_tries))
                    res = self.load("https://premium.rpnet.biz/client_api.php",
                                    get={"username": user,
                                         "password": data['password'],
                                         "action": "downloadInformation",
                                         "id": link_status['id']})
                    self.logDebug("JSON data hdd query: %s" % res)
                    download_status = json_loads(res)['download']

                    if download_status['status'] == '100':
                        link_status['generated'] = download_status['rpnet_link']
                        self.logDebug("Successfully downloaded to rpnet HDD: %s" % link_status['generated'])
                        break
                    else:
                        self.logDebug("At %s%% for the file download" % download_status['status'])

                    self.setWait(30)
                    self.wait()
                    my_try += 1

                if my_try > max_tries:  # We went over the limit!
                    self.fail(_("Waited for about 15 minutes for download to finish but failed"))

        if 'generated' in link_status:
            self.download(link_status['generated'], disposition=True)
        elif 'error' in link_status:
            self.fail(link_status['error'])
        else:
            self.fail(_("Something went wrong, not supposed to enter here"))
