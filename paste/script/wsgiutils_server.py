from paste.script.serve import ensure_port_cleanup

def run_server(wsgi_app, global_conf, host='localhost',
               port=8080):
    from wsgiutils import wsgiServer
    port = int(port)
    ensure_port_cleanup([(host, port)])
    app_map = {'': wsgi_app}
    server = wsgiServer.WSGIServer((host, port), app_map)
    server.serve_forever()
    
