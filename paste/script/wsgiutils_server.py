from paste.script.serve import ensure_port_cleanup

def run_server(wsgi_app, global_conf, host='localhost',
               port=8080):
    from wsgiutils import wsgiServer
    port = int(port)
    # For some reason this is problematic on this server:
    ensure_port_cleanup([(host, port)], maxtries=2, sleeptime=0.5)
    app_map = {'': wsgi_app}
    server = wsgiServer.WSGIServer((host, port), app_map)
    server.serve_forever()
    
