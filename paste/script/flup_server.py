from paste.deploy.converters import aslist, asbool

def run_ajp_thread(wsgi_app, global_conf,
                   scriptName='', host='localhost', port='8009',
                   allowedServers='127.0.0.1'):
    import flup.server.ajp
    s = flup.server.ajp.WSGIServer(
        wsgi_app,
        scriptName=scriptName,
        bindAddress=(host, int(port)),
        allowedServers=aslist(allowedServers),
        )
    s.run()
    
def run_ajp_fork(wsgi_app, global_conf,
                 scriptName='', host='localhost', port='8009',
                 allowedServers='127.0.0.1'):
    import flup.server.ajp_fork
    s = flup.server.ajp_fork.WSGIServer(
        wsgi_app,
        scriptName=scriptName,
        bindAddress=(host, int(port)),
        allowedServers=aslist(allowedServers),
        )
    s.run()

def run_fcgi_thread(wsgi_app, global_conf,
                    host=None, port=None,
                    socket=None,
                    multiplexed=False):
    import flup.server.fcgi
    if socket:
        assert host is None and port is None
        sock = socket
    else:
        assert host is not None and port is not None
        sock = (host, port)
    s = flup.server.ajp.WSGIServer(
        wsgi_app,
        bindAddress=sock,
        multiplexed=asbool(multiplexed))
    s.run()

def run_fcgi_fork(wsgi_app, global_conf,
                  host=None, port=None,
                  socket=None,
                  multiplexed=False):
    import flup.server.fcgi_fork
    if socket:
        assert host is None and port is None
        sock = socket
    else:
        assert host is not None and port is not None
        sock = (host, port)
    s = flup.server.ajp_fork.WSGIServer(
        wsgi_app,
        bindAddress=sock,
        multiplexed=asbool(multiplexed))
    s.run()

def run_scgi_thread(wsgi_app, global_conf,
                    scriptName='', host='localhost', port='4000',
                    allowedServers='127.0.0.1'):
    import flup.server.scgi
    s = flup.server.scgi.WSGIServer(
        wsgi_app,
        scriptName=scriptName,
        bindAddress=(host, int(port)),
        allowedServers=aslist(allowedServers),
        )
    s.run()

def run_scgi_fork(wsgi_app, global_conf,
                  scriptName='', host='localhost', port='4000',
                  allowedServers='127.0.0.1'):
    import flup.server.scgi_fork
    s = flup.server.scgi_fork.WSGIServer(
        wsgi_app,
        scriptName=scriptName,
        bindAddress=(host, int(port)),
        allowedServers=aslist(allowedServers),
        )
    s.run()
    
