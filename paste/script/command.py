import pkg_resources
import sys
import optparse
import os

class BadCommand(Exception):

    def __init__(self, message, exit_code=2):
        self.message = message
        self.exit_code = exit_code
        Exception.__init__(self, message)

parser = optparse.OptionParser()
parser.add_option(
    '--plugin',
    action='append',
    dest='plugins',
    help="Add a plugin to the list of commands (plugins are Egg specs)")
parser.disable_interspersed_args()

# @@: Add an option to run this in another Python interpreter

system_plugins = ['PasteScript']

def run():
    options, args = parser.parse_args()
    system_plugins.extend(options.plugins or [])
    commands = get_commands()
    if not args:
        print 'Usage: %s COMMAND' % sys.argv[0]
        args = ['help']
    command_name = args[0]
    if command_name not in commands:
        command = NotFoundCommand
    else:
        command = commands[command_name].load()
    invoke(command, command_name, options, args[1:])

def get_commands():
    plugins = system_plugins[:]
    egg_info_dir = find_egg_info_dir(os.getcwd())
    if egg_info_dir:
        plugins.append(os.path.splitext(os.path.basename(egg_info_dir))[0])
    plugins = resolve_plugins(plugins)
    commands = load_commands_from_plugins(plugins)
    return commands

def invoke(command, command_name, options, args):
    sys.old_argv0 = sys.argv[0]
    sys.argv[0] = '%s %s' % (sys.argv[0], command_name)
    try:
        runner = command(command_name)
        exit_code = runner.run(args)
    except BadCommand, e:
        print e.message
        exit_code = e.exit_code
    sys.exit(exit_code)
    
def find_egg_info_dir(dir):
    while 1:
        for fn in os.listdir(dir):
            if fn.endswith('.egg-info'):
                return os.path.join(dir, fn)
        parent = os.path.dirname(dir)
        if parent == dir:
            # Top-most directory
            return None
        dir = parent

def resolve_plugins(plugin_list):
    found = []
    while plugin_list:
        plugin = plugin_list.pop()
        pkg_resources.require(plugin)
        found.append(plugin)
        dist = get_distro(plugin)
        if dist.has_metadata('paster_plugins.txt'):
            data = dist.get_metadata('paster_plugins.txt')
            for add_plugin in parse_lines(data):
                if add_plugin not in found:
                    plugin_list.append(add_plugin)
    return map(get_distro, found)

def get_distro(spec):
    return pkg_resources.working_set.find(
        pkg_resources.Requirement(spec))

def load_commands_from_plugins(plugins):
    commands = {}
    for plugin in plugins:
        commands.update(pkg_resources.get_entry_map(
            plugin, group='paste.paster_command'))
    return commands

def parse_lines(data):
    result = []
    for line in data.splitlines():
        line = line.strip()
        if line and not line.startswith('#'):
            result.append(line)
    return result


class Command(object):

    def __init__(self, name):
        self.command_name = name

    max_args = None
    max_args_error = 'You must provide no more than %(max_args)s arguments'
    min_args = None
    min_args_error = 'You must provide at least %(min_args)s arguments'
    required_args = None

    aliases = ()
    required_args = ()
    description = None
    usage = ''

    BadCommand = BadCommand

    # Must define:
    #   parser
    #   summary
    #   command()

    def run(self, args):
        self.parse_args(args)
        
        # Setup defaults:
        if not hasattr(self.options, 'verbose'):
            self.options.verbose = 0
        if not hasattr(self.options, 'interactive'):
            self.options.interactive = 0
        if (getattr(self.options, 'simulate', False)
            and not self.options.verbose):
            self.options.verbose = max(self.options.verbose, 1)
        self.verbose = self.options.verbose
        self.interactive = self.options.interactive
        self.simulate = getattr(self.options, 'simulate', False)

        # Validate:
        if self.min_args is not None and len(self.args) < self.min_args:
            raise BadCommand(
                self.min_args_error % {'min_args': self.min_args,
                                       'actual_args': len(self.args)})
        if self.max_args is not None and len(self.args) > self.max_args:
            raise BadCommand(
                self.max_args_error % {'max_args': self.max_args,
                                       'actual_args': len(self.args)})
        for var_name, option_name in self.required_args:
            if not getattr(self.options, var_name, None):
                raise BadCommand(
                    'You must provide the option %s' % option_name)
        self.command()

    def parse_args(self, args):
        if self.usage:
            usage = ' '+self.usage
        else:
            usage = ''
        self.parser.usage = "%%prog [options]%s\n%s" % (
            usage, self.summary)
        self.parser.prog = '%s %s' % (sys.argv[0], self.command_name)
        if self.description:
            self.parser.description = self.description
        self.options, self.args = self.parser.parse_args(args)

    ########################################
    ## Utility methods
    ########################################

    def here(cls):
        mod = sys.modules[cls.__module__]
        return os.path.dirname(mod.__file__)

    here = classmethod(here)

    def ask(self, prompt, safe=False, default=True):
        """
        Prompt the user.  Default can be true, false, ``'careful'`` or
        ``'none'``.  If ``'none'`` then the user must enter y/n.  If
        ``'careful'`` then the user must enter yes/no (long form).

        If the interactive option is over two (``-ii``) then ``safe``
        will be used as a default.  This option should be the
        do-nothing option.
        """
        # @@: Should careful be a separate argument?

        if self.options.interactive >= 2:
            default = safe
        if default == 'careful':
            prompt += ' [yes/no]?'
        elif default == 'none':
            prompt += ' [y/n]?'
        elif default:
            prompt += ' [Y/n]? '
        else:
            prompt += ' [y/N]? '
        while 1:
            response = raw_input(prompt).strip().lower()
            if not response:
                if default in ('careful', 'none'):
                    print 'Please enter yes or no'
                    continue
                return default
            if default == 'careful':
                if response in ('yes', 'no'):
                    return response == 'yes'
                print 'Please enter "yes" or "no"'
                continue
            if response[0].lower() in ('y', 'n'):
                return response[0].lower() == 'y'
            print 'Y or N please'

    def pad(self, s, length, dir='left'):
        if len(s) >= length:
            return s
        if dir == 'left':
            return s + ' '*(length-len(s))
        else:
            return ' '*(length-len(s)) + s

    def standard_parser(cls, verbose=True,
                        interactive=False,
                        simulate=False):
        """
        Typically used like::

            class MyCommand(Command):
                parser = Command.standard_parser()

        Subclasses may redefine ``standard_parser``, so use the
        nearest superclass's class method.
        """
        parser = optparse.OptionParser()
        if verbose:
            parser.add_option('-v', '--verbose',
                              action='count',
                              dest='verbose',
                              default=0)
        if interactive:
            parser.add_option('-i', '--interactive',
                              action='count',
                              dest='interactive',
                              default=0)
        if simulate:
            parser.add_option('-n', '--simulate',
                              action='store_true',
                              dest='simulate',
                              default=False)
                              
        return parser

    standard_parser = classmethod(standard_parser)

class NotFoundCommand(Command):

    def run(self, args):
        print 'Command %s not known' % self.command_name
        commands = get_commands().items()
        commands.sort()
        print 'Known commands:'
        longest = max([len(n) for n, c in commands])
        for name, command in commands:
            print '  %s  %s' % (self.pad(name, length=longest),
                                command.load().summary)
        return 2
    
        
