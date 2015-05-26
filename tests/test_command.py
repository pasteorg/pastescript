#!/usr/bin/env python
from paste.script import command
from paste.script import create_distro
import six
import sys
import textwrap
import unittest


class TestCommand(unittest.TestCase):
   def test_help(self):
        usage = textwrap.dedent('''
            Usage: test_command.py [paster_options] COMMAND [command_options]

            Options:
              --version         show program's version number and exit
              --plugin=PLUGINS  Add a plugin to the list of commands (plugins are Egg
                                specs; will also require() the Egg)
              -h, --help        Show this help message

            Commands:
              create       Create the file layout for a Python distribution
              grep         Search project for symbol
              help         Display help
              make-config  Install a package and create a fresh config file/directory
              points       Show information about entry points
              post         Run a request for the described application
              request      Run a request for the described application
              serve        Serve the described application
              setup-app    Setup an application, given a config file
        ''').strip() + "\n\n"

        stdout = sys.stdout
        try:
            sys.stdout = six.StringIO()
            try:
                command.run(['--help'])
            except SystemExit as exc:
                self.assertEqual(exc.code, 0)
            else:
                self.fail("SystemExit not raised")
            self.assertEqual(usage, sys.stdout.getvalue())
        finally:
            sys.stdout = stdout


class TestCreateDistroCommand(unittest.TestCase):
    def setUp(self):
        self.cmd = create_distro.CreateDistroCommand('create_distro')

    def test_list_templates(self):
        self.cmd.run(['--list-templates'])

    def test_template(self):
        self.cmd.run(['--template=basic_package', 'test'])


if __name__ == "__main__":
    unittest.main()
