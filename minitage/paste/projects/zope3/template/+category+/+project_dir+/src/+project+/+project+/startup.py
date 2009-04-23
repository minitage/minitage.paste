import os
import sys
import code
import zdaemon.zdctl
import zope.app.wsgi
import zope.app.debug

def application_factory(global_conf, **local_conf):
    conf=local_conf.get('conf',
                        os.path.join(global_conf['here'],
                                     'zope.conf'))
    return zope.app.wsgi.getWSGIApplication(conf)

def find_zope_conf(zope_conf):
    zc = zope_conf
    if not os.path.exists(zc):
        buildout = os.path.dirname(os.path.dirname(sys.argv[0]))
        zc = os.path.join(buildout, zope_conf)
        if not os.path.exists(zc):
            zc = os.path.join(buildout, 'etc', zope_conf)
            if not os.path.exists(zc):
                zc = os.path.join(buildout, 'parts', zope_conf)
                if not os.path.exists(zc):
                    raise Exception('%s not found in ./, etc/, '
                                    'parts/' % zope_conf)
    else:
        zc = zope_conf
    return zc



def interactive_debug_prompt(zope_conf='parts/zope.conf'):
    if len(sys.argv)>1:
        zope_conf = sys.argv[1]

    db = zope.app.wsgi.config(find_zope_conf(zope_conf))
    debugger = zope.app.debug.Debugger.fromDatabase(db)
    # Invoke an interactive interpreter shell
    banner = ("Welcome to the interactive debug prompt.\n"
              "The 'root' variable contains the ZODB root folder.\n"
              "The 'app' variable contains the Debugger, 'app.publish(path)' "
              "simulates a request.")
    code.interact(banner=banner, local={'debugger': debugger,
                                        'app':      debugger,
                                        'root':     debugger.root()})

class ControllerCommands(zdaemon.zdctl.ZDCmd):

    def do_debug(self, rest):
        interactive_debug_prompt()

    def help_debug(self):
        print "debug -- Initialize the application, providing a debugger"
        print "         object at an interactive Python prompt."

def zdaemon_controller_dev():
    return zdaemon_controller('zdaemon.conf')

def zdaemon_controller(config=None):
    if not config:
        config = 'prod.zdaemon.conf'
    argv = sys.argv[:]
    argv.pop(0)
    launch_args = []
    if not '-C' in argv:
        launch_args.append('-C')
        launch_args.append(find_zope_conf(config))
    launch_args.extend(argv)
    zdaemon.zdctl.main(launch_args,
                       options=None,
                       cmdclass=ControllerCommands)

