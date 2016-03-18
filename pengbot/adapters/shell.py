import re
import sys
import cmd

from pengbot.utils import colorizer
from pengbot.adapters.base import BaseAdapter, UnknownCommand


class Shell(cmd.Cmd):
    def __init__(self, adapter, *args, **kwargs):
        self.adapter = adapter
        super().__init__(*args, **kwargs)
        setattr(self, 'do_%s' % self.adapter.env.bot_name, self.do_bot)

    def do_exit(self, line):
        """Exit the session"""
        with colorizer('blue'):
            print('Good bye')
        return -1

    do_EOF = do_exit
    do_bye = do_exit

    def do_directives(self, line):
        """List all directives supported by the bot"""
        for name, cmd in self.adapter.directives.items():
            with colorizer('blue'):
                print('bot %s:' % name)
                if cmd.__doc__:
                    for line in cmd.__doc__.split('\n'):
                        print('  %s' % line)
                else:
                    print()

    def says(self, message):
        with colorizer('blue'):
            print('%s> %s' % (self.adapter.env.bot_name, message))

    def do_bot(self, line):
        """Call the bot"""
        with colorizer('blue'):
            if not line:
                self.says('what?')

            try:
                res = self.adapter.receive(message=line)
            except UnknownCommand:
                self.says("I do not known what the '%s' directive is" % line)
            else:
                self.says(res)

    def cmdloop(self):
        try:
            super().cmdloop()
        except KeyboardInterrupt:
            self.do_exit(self)


class Adapter(BaseAdapter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.shell = Shell(self)
        self.shell.prompt = "{env.host_user}> ".format(env=self.env)

    def receive(self, *args, **kwargs):
        with colorizer('green'):
            print('\n  Hello {env.host_user}\n'.format(env=self.env))

        self.shell.cmdloop()

    def close(self):
        return True
