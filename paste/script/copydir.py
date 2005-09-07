import os
import string
import cgi
import urllib
import re

def copy_dir(source, dest, vars, verbosity, simulate, indent=0):
    names = os.listdir(source)
    names.sort()
    pad = ' '*(indent*2)
    if not os.path.exists(dest):
        if verbosity >= 1:
            print '%sCreating %s/' % (pad, dest)
        if not simulate:
            os.makedirs(dest)
    elif verbosity >= 2:
        print '%sDirectory %s exists' % (pad, dest)
    for name in names:
        full = os.path.join(source, name)
        if name.startswith('.'):
            if verbosity >= 2:
                print '%sSkipping hidden file %s' % (pad, full)
            continue
        dest_full = os.path.join(dest, _substitute_filename(name, vars))
        if dest_full.endswith('_tmpl'):
            dest_full = dest_full[:-5]
        if os.path.isdir(full):
            if verbosity:
                print '%sRecursing into %s' % (pad, os.path.basename(full))
            copy_dir(full, dest_full, vars, verbosity, simulate,
                     indent=indent+1)
            continue
        f = open(full, 'rb')
        content = f.read()
        f.close()
        content = _substitute_content(content, vars, filename=full)
        if verbosity:
            print '%sCopying %s to %s' % (pad, os.path.basename(full), dest_full)
        if not simulate:
            f = open(dest_full, 'wb')
            f.write(content)
            f.close()

def _substitute_filename(fn, vars):
    for var, value in vars.items():
        fn = fn.replace('+%s+' % var, str(value))
    return fn

def _substitute_content(content, vars, filename='<string>'):
    v = standard_vars.copy()
    v.update(vars)
    tmpl = LaxTemplate(content)
    try:
        return tmpl.substitute(TypeMapper(v))
    except Exception, e:
        _add_except(e, ' in file %s' % filename)
        raise

def html_quote(s):
    if s is None:
        return ''
    return cgi.escape(str(s), 1)

def url_quote(s):
    if s is None:
        return ''
    return urllib.quote(str(s))

def test(conf, true_cond, false_cond=None):
    if conf:
        return true_cond
    else:
        return false_cond

def _add_except(exc, info):
    if not hasattr(exc, 'args') or exc.args is None:
        return
    args = list(exc.args)
    args[0] += ' ' + info
    exc.args = tuple(args)
    return
    

standard_vars = {
    'nothing': None,
    'html_quote': html_quote,
    'url_quote': url_quote,
    'empty': '""',
    'test': test,
    'repr': repr,
    'str': str,
    'bool': bool,
    }

class TypeMapper(dict):

    def __getitem__(self, item):
        options = item.split('|')
        for op in options[:-1]:
            try:
                value = eval_with_catch(op, dict(self))
                break
            except (NameError, KeyError):
                pass
        else:
            value = eval(options[-1], dict(self))
        if value is None:
            return ''
        else:
            return str(value)

def eval_with_catch(expr, vars):
    try:
        return eval(expr, vars)
    except Exception, e:
        _add_except(e, 'in expression %r' % expr)
        raise
        
class LaxTemplate(string.Template):
    # This change of pattern allows for anything in braces, but
    # only identifiers outside of braces:
    pattern = re.compile(r"""
    \$(?:
      (?P<escaped>\$)             |   # Escape sequence of two delimiters
      (?P<named>[_a-z][_a-z0-9]*) |   # delimiter and a Python identifier
      {(?P<braced>.*?)}           |   # delimiter and a braced identifier
      (?P<invalid>)                   # Other ill-formed delimiter exprs
    )
    """, re.VERBOSE | re.IGNORECASE)
