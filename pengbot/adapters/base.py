import logging

logger = logging.getLogger('pengbot')


class UnknownCommand(Exception):
    pass


class BaseAdapter:
    def __init__(self, *args, **kwargs):
        self.env = kwargs['env']
        self.directives = kwargs['directives']
        self.listeners = kwargs['listeners']

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
        command = _message.pop(0)
        command_args = _message

        logger.debug('command=%s, args=%s', command, command_args)

        if command in self.directives:
            func = self.directives[command]
            return func.run(*command_args)
        else:
            for listener in self.listeners:
                func = self.listeners[listener]
                return func.run(message)
