import os
from Component import CPage
from Component.notify import NotifyComponent
from ZPTKit import ZPTComponent

from paste import CONFIG
from paste.url import URL
from ${package}.db import *
import string
from mx import DateTime

from iscape import clientconfig

class SitePage(CPage):

    components = [
        ZPTComponent([os.path.join(os.path.dirname(__file__),
                                   'templates')]),
        NotifyComponent()]
    
    def title(self):
        return self.options.get('title', CPage.title(self))

    def awake(self, trans):
        CPage.awake(self, trans)
        env = self.request().environ()

        self.user_role_permitted = CONFIG['user_role_permitted']
        if callable(self.user_role_permitted):
            self.user_role_permitted = self.user_role_permitted()

        self.tool = clientconfig.setup_options(
            env, self.options,
            client_name=CONFIG['client_name'],
            app_name=CONFIG['app_name'],
            static_url=CONFIG['static_url'])
        self.appurl = URL(self.request().environ()['%s.base_href' %
                                                   CONFIG['app_name']])

        self.copyright = CONFIG['copyright']
        if callable(self.copyright):
            self.copyright = self.copyright()

        self.config = self.request().environ()['paste.config']
        self.config['error_email'] = ${repr(author_email)|empty}

        self.setup()

    def setup(self):
        pass

    def sleep(self, trans):
        self.teardown()
        CPage.sleep(self, trans)

    def teardown(self):
        pass

    def writeHTML(self):
        self.writeTemplate()

    def preAction(self, action):
        self.setView('writeContent')

    def postAction(self, action):
        if self.view() is not None:
            self.writeHTML()

