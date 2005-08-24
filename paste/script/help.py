from command import Command, get_commands
import sys

class HelpCommand(Command):

    summary = "Display help"
    usage = '[COMMAND]'

    max_args = 1

    parser = Command.standard_parser()

    def command(self):
        if not self.args:
            self.generic_help()
            return

        name = self.args[0]
        commands = get_commands()
        if name not in commands:
            print 'No such command: %s' % name
            self.generic_help()
            return

        command = commands[name].load()
        runner = command(name)
        sys.argv[0] = sys.old_argv0
        runner.run(['-h'])
        
    def generic_help(self):
        commands = get_commands().items()
        commands.sort()
        longest = max([len(n) for n, c in commands])
        print 'Commands:'
        for name, command in commands:
            command = command.load()
            print '  %s  %s' % (self.pad(name, length=longest),
                                command.summary)
            if command.description:
                print '    %s' % command.description
        
