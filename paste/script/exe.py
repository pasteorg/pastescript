import command

class ExeCommand(command.Command):

    parser = command.Command.standard_parser(verbose=False)
    summary = 'Run #! executable files'
    hidden = True

    def command(self):
        print "Not very complete, is it?"
        print 'Args', self.args
        print 'Options', self.options
        import sys
        print "Path", sys.path
        
