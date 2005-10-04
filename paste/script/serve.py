# @@: This should be moved to paste.deploy
import re
import os
import signal
import sys
from command import Command, BadCommand
from paste.deploy import loadapp, loadserver
import threading
import atexit

class ServeCommand(Command):

    max_args = 1
    min_args = 0
    usage = 'CONFIG_FILE'
    summary = "Serve the described application"

    parser = Command.standard_parser(quiet=True)
    parser.add_option('-n', '--app-name',
                      dest='app_name',
                      metavar='NAME',
                      help="Load the named application (default main)")
    parser.add_option('-s', '--server',
                      dest='server',
                      metavar='SERVER_TYPE',
                      help="Use the named server.")
    parser.add_option('--server-name',
                      dest='server_name',
                      metavar='SECTION_NAME',
                      help="Use the named server as defined in the configuration file (default: main)")
    parser.add_option('--daemon',
                      dest="daemon",
                      action="store_true",
                      help="Run in daemon (background) mode")
    parser.add_option('--pid-file',
                      dest='pid_file',
                      metavar='FILENAME',
                      help="Save PID to file (default to paster.pid if running in daemon mode)")
    parser.add_option('--log-file',
                      dest='log_file',
                      metavar='LOG_FILE',
                      help="Save output to the given log file (redirects stdout)")
    parser.add_option('--reload',
                      dest='reload',
                      action='store_true',
                      help="Use auto-restart file monitor")
    parser.add_option('--reload-interval',
                      dest='reload_interval',
                      default=1,
                      help="Seconds between checking files (low number can cause significant CPU usage)")

    if hasattr(os, 'setuid'):
        # I don't think these are availble on Windows
        parser.add_option('--user',
                          dest='set_user',
                          metavar="USERNAME",
                          help="Set the user (usually only possible when run as root)")
        parser.add_option('--group',
                          dest='set_group',
                          metavar="GROUP",
                          help="Set the group (usually only possible when run as root)")

    parser.add_option('--stop-daemon',
                      dest='stop_daemon',
                      action='store_true',
                      help='Stop a daemonized server (given a PID file, or default paster.pid file)')


    _scheme_re = re.compile(r'^[a-zA-Z0-9_-]+:')

    default_verbosity = 1

    _reloader_environ_key = 'PYTHON_RELOADER_SHOULD_RUN'

    def command(self):
        if self.options.stop_daemon:
            return self.stop_daemon()

        if not hasattr(self.options, 'set_user'):
            # Windows case:
            self.options.set_user = self.options.set_group = None
        # @@: Is this the right stage to set the user at?
        self.change_user_group(
            self.options.set_user, self.options.set_group)

        if self.options.reload:
            if os.environ.get(self._reloader_environ_key):
                from paste import reloader
                if self.verbose > 1:
                    print 'Running reloading file monitor'
                reloader.install(int(self.options.reload_interval), False)
            else:
                return self.restart_with_reloader()
                
        if not self.args:
            raise BadCommand('You must give a config file')
        app_spec = self.args[0]
        app_name = self.options.app_name
        if not self._scheme_re.search(app_spec):
            app_spec = 'config:' + app_spec
        server_name = self.options.server_name
        if self.options.server:
            server_spec = 'egg:PasteScript'
            assert server_name is None
            server_name = self.options.server
        else:
            server_spec = app_spec
        base = os.getcwd()

        if self.options.daemon:
            self.daemonize()

        if self.options.pid_file:
            self.record_pid(self.options.pid_file)

        if self.options.log_file:
            stdout_log = LazyWriter(self.options.log_file)
            sys.stdout = stdout_log
            sys.stderr = stdout_log

        server = loadserver(server_spec, name=server_name,
                            relative_to=base)
        app = loadapp(app_spec, name=app_name,
                      relative_to=base)

        if self.verbose > 0:
            print 'Starting server in PID %i.' % os.getpid()
        try:
            server(app)
        except (SystemExit, KeyboardInterrupt), e:
            if self.verbose > 1:
                raise
            if str(e):
                msg = ' '+str(e)
            else:
                msg = ''
            print 'Exiting%s (-v to see traceback)' % msg

    def daemonize(self):
        if self.verbose > 0:
            print 'Entering daemon mode'
        pid = os.fork()
        if pid:
            sys.exit()
        if not self.options.pid_file:
            self.options.pid_file = 'paster.pid'
        if not self.options.log_file:
            self.options.log_file = 'paster.log'

    def record_pid(self, pid_file):
        pid = os.getpid()
        if self.verbose > 1:
            print 'Writing PID %s to %s' % (pid, pid_file)
        f = open(pid_file, 'w')
        f.write(str(pid))
        f.close()
        atexit.register(_remove_pid_file, pid_file, self.verbose)

    def stop_daemon(self):
        pid_file = self.options.pid_file or 'paster.pid'
        if not os.path.exists(pid_file):
            print 'No PID file exists in %s' % pid_file
            return 1
        f = open(pid_file)
        pid = int(f.read().strip())
        f.close()
        os.kill(pid, signal.SIGTERM)
        if self.verbose > 0:
            print 'Process %i killed' % pid

    def restart_with_reloader(self):
        if self.verbose > 0:
            print 'Starting subprocess with file monitor'
        while 1:
            args = [sys.executable] + sys.argv
            new_environ = os.environ.copy()
            new_environ[self._reloader_environ_key] = 'true'
            exit_code = os.spawnve(os.P_WAIT, sys.executable,
                                   args, new_environ)
            if exit_code != 3:
                return exit_code
            if self.verbose > 0:
                print '-'*20, 'Restarting', '-'*20

    def change_user_group(self, user, group):
        if not user and not group:
            return
        import pwd, grp
        uid = gid = None
        if group:
            try:
                gid = int(group)
                group = grp.getgrgid(gid).gr_name
            except ValueError:
                import grp
                try:
                    entry = grp.getgrnam(group)
                except KeyError:
                    raise BadCommand(
                        "Bad group: %r; no such group exists" % group)
                gid = entry.gr_gid
        try:
            uid = int(user)
            user = pwd.getpwuid(uid).pw_name
        except ValueError:
            try:
                entry = pwd.getpwnam(user)
            except KeyError:
                raise BadCommand(
                    "Bad username: %r; no such user exists" % user)
            if not gid:
                gid = entry.pw_gid
            uid = entry.pw_uid
        if self.verbose > 0:
            print 'Changing user to %s:%s (%s:%s)' % (
                user, group or '(unknown)', uid, gid)
        if gid:
            os.setgid(gid)
        if uid:
            os.setuid(uid)
            
class LazyWriter(object):

    def __init__(self, filename):
        self.filename = filename
        self.fileobj = None
        self.lock = threading.Lock()
        
    def open(self):
        if self.fileobj is None:
            self.lock.acquire()
            try:
                if self.fileobj is None:
                    self.fileobj = open(self.filename, 'a')
            finally:
                self.lock.release()
        return self.fileobj

    def write(self, text):
        fileobj = self.open()
        fileobj.write(text)
        fileobj.flush()

    def flush(self):
        self.open().flush()
        
def _remove_pid_file(filename, verbosity):
    if verbosity > 0:
        print "Removing PID file %s" % filename
    try:
        os.unlink(filename)
        return
    except OSError, e:
        # Record, but don't give traceback
        print "Cannot remove PID file: %s" % e
    # well, at least lets not leave the invalid PID around...
    try:
        f = open(filename, 'w')
        f.write('')
        f.close()
    except OSError, e:
        print 'Stale PID left in file: %s (%e)' % (filename, e)
    else:
        print 'Stale PID removed'
        
            
        
