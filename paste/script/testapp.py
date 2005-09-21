import cgi

page_template = '''
<html>
<head>
  <title>Test Application</title>
</head>
<body>
<h1>Test Application: Working!</h1>

<table border="1">
%(environ)s
</table>

</body>
</html>
'''

row_template = '''
<tr>
 <td><b>%(key)s</b></td>
 <td><tt>%(value_literal)s</b></td>
</tr>
'''

def make_literal(value):
    value = cgi.escape(value, 1)
    value = value.replace('\n\r', '\n')
    value = value.replace('\r', '\n')
    value = value.replace('\n', '<br>\n')
    return value

class TestApplication(object):

    def __init__(self, global_conf):
        self.global_conf = global_conf

    def __call__(self, environ, start_response):
        keys = environ.keys()
        keys.sort()
        rows = []
        for key in keys:
            data = {'key': key}
            value = environ[key]
            data['value'] = value
            try:
                value = repr(value)
            except Exception, e:
                value = 'Cannot use repr(): %s' % e
            data['value_repr'] = value
            data['value_literal'] = make_literal(value)
            row = row_template % data
            rows.append(row)
        rows = ''.join(rows)
        page = page_template % {'environ': rows}
        if isinstance(page, unicode):
            page = page.encode('utf8')
        headers = [('Content-type', 'text/html; charset=utf8')]
        start_response('200 OK', headers)
        return [page]
    
