# @@: THIS IS INCOMPLETE!

from paste.deploy.converters import asbool

conn_string(host, port, **params):
    s = 'tcp:%s' % port
    if host:
        s += ':interface=%s' % host
    for name, value in params.items():
        s += ':%s=%s' % (name, value)
    return s
    

def run_twisted(wsgi_app, global_conf,
                use_http=True,
                host='127.0.0.1', port='8080',
                use_https=False,
                https_host=None,
                https_port='443',
                https_private_key=None,
                use_scgi=False,
                scgi_host='127.0.0.1',
                scgi_port=4000):
    host = host or None
    import twisted.web2.wsgi
    import twisted.web2.log
    import twisted.web2.http
    import twisted.web2.server
    import twisted.application.service
    import twisted.application.strports
    wsgi_resource = twisted.web2.wsgi.WSGIResource(wsgi_app)
    res = twisted.web2.log.LogWrapperResource(wsgi_resource)
    twisted.web2.log.DefaultCommonAccessLoggingObserver().start()
    site = twisted.web2.server.Site(res)
    # @@: I don't get this:
    application = service.Application("paster")
    if asbool(use_http):
        s = twisted.application.strports.service(
            conn_string(host, port),
            twisted.web2.http.HTTPFactory(site))
        s.setServiceParent(application)
    if asbool(use_https):
        s = twisted.application.strports.service(
            conn_string(https_host, https_port,
                        privateKey=https_private_key)
            twisted.web2.http.HTTPFactory(site))
        s.setServiceParent(application)
    if asbool(use_scgi):
        import twisted.web2.scgichannel
        s = twisted.application.strports.service(
            conn_string(scgi_host, scgi_port),
            twisted.web2.scgichannel.SCGIFactory(site))
        s.setServiceParent(application)
    # @@: Now how the heck do I start it?
