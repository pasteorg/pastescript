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
    invoke(command, command_name, options, args)

def get_commands():
    plugins = system_plugins[:]
    egg_info_dir = find_egg_info_dir(os.getcwd())
    if egg_info_dir:
        plugins.append(os.path.splitext(os.path.basename(egg_info_dir))[0])
    plugins = resolve_plugins(plugins)
    commands = load_commands_from_plugins(plugins)
    return commands

def invoke(command, command_name, options, args):
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
        self.name = name

    short_description = None

    ########################################
    ## Utility methods
    ########################################

    def pad(self, s, length, dir='left'):
        if len(s) >= length:
            return s
        if dir == 'left':
            return s + ' '*(length-len(s))
        else:
            return ' '*(length-len(s)) + s

class NotFoundCommand(Command):

    def run(self, args):
        print 'Command %s not known' % self.name
        commands = get_commands().items()
        commands.sort()
        print 'Known commands:'
        longest = max([len(n) for n, c in commands])
        for name, command in commands:
            print '  %s  %s' % (self.pad(name, length=longest),
                                command.load().short_description)
        return 2
    
        
