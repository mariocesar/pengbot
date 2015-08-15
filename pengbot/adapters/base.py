import logging

logger = logging.getLogger('pengbot')


class UnknownCommand(Exception):
    pass


class BaseAdapter:
    def __init__(self, env, directives):
        self.env = env
        self.directives = directives

    def send(self, data):
        raise NotImplementedError()

    def run(self):
        raise NotImplementedError()

    def close(self):
        raise NotImplementedError()

    def receive(self, message):
        logger.debug('Message received: "%s"', message)

        if not message:
            return

        _message = message.split()
        command = _message.pop()
        args = ' '.join(_message)

        logger.debug('command=%s, args=%s', command, args)

        if command in self.directives:
            cmd = self.directives[command]
            return cmd.run()
        else:
            raise UnknownCommand('Unknown command "%s"' % command)