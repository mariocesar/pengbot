from .utils import AttributeDict

__all__ = ('env',)


def get_host_username():
    import getpass
    return getpass.getuser()


def get_host_name():
    import socket
    return socket.gethostname()


env = AttributeDict({
    'host_user': get_host_username(),
    'host_name': get_host_name()
})
