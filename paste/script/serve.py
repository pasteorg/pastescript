# @@: This should be moved to paste.deploy
import re
import os
from command import Command
from paste.deploy import loadapp, loadserver

class ServeCommand(Command):

    max_args = 1
    min_args = 1
    usage = 'CONFIG_FILE'
    summary = "Serve the described application"

    parser = Command.standard_parser()
    parser.add_option('-n', '--app-name',
                      dest='app_name',
                      metavar='NAME',
                      help="Load the named application (default main)")
    parser.add_option('-s', '--server',
                      dest='server',
                      metavar='SERVER_TYPE',
                      help="Use the named server.")
    parser.add_option('--server-name',
                      dest='server_name',
                      metavar='SECTION_NAME',
                      help="Use the named server as defined in the configuration file (default: main)")

    _scheme_re = re.compile(r'^[a-zA-Z0-9_-]+:')

    def command(self):
        app_spec = self.args[0]
        app_name = self.options.app_name
        if not self._scheme_re.search(app_spec):
            app_spec = 'config:' + app_spec
        server_name = self.options.server_name
        if self.options.server:
            server_spec = 'egg:PasteScript'
            assert server_name is None
            server_name = self.options.server
        else:
            server_spec = app_spec
        base = os.getcwd()
        server = loadserver(server_spec, name=server_name,
                            relative_to=base)
        app = loadapp(app_spec, name=app_name,
                      relative_to=base)
        server(app)
        
            
