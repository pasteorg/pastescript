import re
import os
import sys
import shlex
import pkg_resources
import command

class ExeCommand(command.Command):

    parser = command.Command.standard_parser(verbose=False)
    summary = 'Run #! executable files'
    hidden = True

    _exe_section_re = re.compile(r'^\s*\[\s*exe\s*\]\s*$')
    _section_re = re.compile(r'^\s*\[')

    def run(self, argv):
        if os.environ.get('REQUEST_METHOD'):
            # We're probably in a CGI environment
            sys.stdout = sys.stderr
            os.environ['PASTE_DEFAULT_QUIET'] = 'true'
            # Maybe import cgitb or something?
            
        print "content-type: text/html\n"
        filename = argv[-1]
        f = open(filename)
        lines = f.readlines()
        f.close()
        options = {}
        lineno = 1
        while lines:
            if self._exe_section_re.search(lines[0]):
                lines.pop(0)
                break
            lines.pop(0)
            lineno += 1
        pre_options = []
        options = argv[:-1]
        for line in lines:
            lineno += 1
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if self._section_re.search(line):
                break
            if '=' not in line:
                raise command.BadCommand('Missing = in %s at %s: %r'
                                         % (filename, lineno, line))
            name, value = line.split('=', 1)
            name = name.strip()
            value = value.strip()
            if name == 'require':
                pkg_resources.require(value)
            elif name == 'command' or name == 'add':
                options.extend(shlex.split(value))
            elif name == 'plugin':
                options[:0] = ['--plugin', value]
            else:
                options.extend(['--' + name.replace('_', '-'), value])
        os.environ['PASTE_CONFIG_FILE'] = filename
        command.run(options)

    def command(self):
        filename = self.args
        print "Not very complete, is it?"
        print 'Args', self.args
        print 'Options', self.options
        import sys
        print "Path", sys.path
        
