# -*- coding: utf-8 -*-

import re
from pyload.plugins.Crypter import Crypter


class QuickshareCz(Crypter):
    __name__    = "QuickshareCz"
    __type__    = "crypter"
    __version__ = "0.10"

    __pattern__ = r'http://(?:www\.)?quickshare\.cz/slozka-\d+.*'
    __config__  = [("use_subfolder", "bool", "Save package to subfolder", True),
                   ("subfolder_per_package", "bool", "Create a subfolder for each package", True)]

    __description__ = """Quickshare.cz folder decrypter plugin"""
    __license__     = "GPLv3"
    __authors__     = [("zoidberg", "zoidberg@mujmail.cz")]


    FOLDER_PATTERN = r'<textarea[^>]*>(.*?)</textarea>'
    LINK_PATTERN = r'(http://www\.quickshare\.cz/\S+)'


    def decrypt(self, pyfile):
        html = self.load(pyfile.url)

        m = re.search(self.FOLDER_PATTERN, html, re.S)
        if m is None:
            self.error(_("FOLDER_PATTERN not found"))
        self.urls.extend(re.findall(self.LINK_PATTERN, m.group(1)))
