import pkg_resources
import sys
import optparse
import os

parser = optparse.OptionParser()
parser.add_option(
    '--plugin',
    action='append',
    dest='plugins',
    help="Add a plugin to the list of commands (plugins are Egg specs)")

# @@: Add an option to run this in another Python interpreter

def run():
    options, args = parser.parse_args()
    plugins = options.plugins or []
    plugins.append('PasteScript')
    egg_info_dir = find_egg_info_dir(os.getcwd())
    if egg_info_dir:
        plugins.append(os.path.basename(egg_info_dir))
    plugins = resolve_plugins(plugins)
    
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
        dist = pkg_resources.find(plugin)
        if dist.resource_exists('paster_plugins.txt'):
            data = dist.resource_string('paster_plugins.txt')
            for add_plugin in parse_lines(data):
                if add_plugin not in found:
                    plugin_list.append(add_plugin)
    return found

def parse_lines(data):
    result = []
    for line in data.splitlines():
        line = line.strip()
        if line and not line.startswith('#'):
            result.append(line)
    return result
