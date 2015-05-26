#!/usr/bin/env python
from paste.script import command
from paste.script import create_distro
import unittest


class TestCommand(unittest.TestCase):
    def test_help(self):
        command.run(['--help'])


class TestCreateDistroCommand(unittest.TestCase):
    def setUp(self):
        self.cmd = create_distro.CreateDistroCommand('create_distro')

    def test_list_templates(self):
        self.cmd.run(['--list-templates'])

    def test_create_distro(self):
        self.cmd.run(['--template=basic_package', 'test'])


if __name__ == "__main__":
    unittest.main()
