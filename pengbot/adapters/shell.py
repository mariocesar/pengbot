import cmd
import getpass

from pengbot.adapters.base import BaseAdapter, UnknownCommand
from pengbot.utils import colorize


class Event:
    pass


class Shell(cmd.Cmd):
    def __init__(self, adapter, *args, **kwargs):
        self.adapter = adapter
        adapter.context['user'] = getpass.getuser()
        self.prompt = "{0}> ".format(adapter.context['user'])
        super().__init__(*args, **kwargs)
        setattr(self, 'do_%s' % self.adapter.name, self.do_bot)

    def do_exit(self, line):
        """Exit the session"""
        with colorize('blue'):
            print('Good bye')
        return -1

    do_EOF = do_exit
    do_bye = do_exit

    def do_directives(self, line):
        """List all directives supported by the bot"""
        for name, cmd in self.adapter.directives.items():
            with colorize('blue'):
                print('bot %s:' % name)
                if cmd.__doc__:
                    for line in cmd.__doc__.split('\n'):
                        print('  %s' % line)
                else:
                    print()

    def says(self, message):
        with colorize('blue'):
            print('%s> %s' % (self.adapter.context.bot_name, message))

    def do_bot(self, line):
        """Call the bot"""
        with colorize('blue'):
            if not line:
                self.says('what?')

            try:
                res = self.adapter.receive(message=line)
            except UnknownCommand:
                self.says("I do not known what the '%s' directive is" % line)
            else:
                self.says(res)

    def cmdloop(self, intro=None):
        try:
            super().cmdloop()
        except KeyboardInterrupt:
            self.do_exit(self)


class MainAdapter(BaseAdapter):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.shell = Shell(self)

    def receive(self, *args, **kwargs):
        with colorize('green'):
            print('\nHello %s\n' % self.context['user'])

        self.shell.cmdloop()

    def close(self):
        return True
