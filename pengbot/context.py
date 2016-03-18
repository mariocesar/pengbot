from pengbot.utils import AttributeDict


class Environ:
    """Context provides attribute-style access."""

    def __init__(self, context):
        self.context = context

    def body(self):
        pass

    def handler_callback(self):
        pass

    def handler_resolver(self):
        pass


class Context(AttributeDict):
    pass
