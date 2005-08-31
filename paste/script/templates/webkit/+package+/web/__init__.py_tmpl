import os
from paste import wsgilib
from ${package}.sitepage import CONFIG

def urlparser_hook(environ):
    if not environ.has_key('${package}.base_href'):
        environ['${package}.base_href'] = environ.get('SCRIPT_NAME', '') or '/'

