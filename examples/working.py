import asyncio
import inspect
from contextlib import contextmanager
from functools import wraps

indent_level = -1


def do_puts(content, *args, **kwargs):
    print('%s%s' % (indent_level * '    ', content), *args, **kwargs)


@contextmanager
def indent():
    global indent_level
    indent_level += 1

    yield do_puts

    indent_level -= 1


def debug_func(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with indent() as puts:
            puts('%s()\t%s' % (func.__name__, func))
            puts('  spec=', inspect.getfullargspec(func))
            puts('  args=%s kwargs=%s' % (args, kwargs))
        return func(*args, **kwargs)

    return wrapper


@debug_func
async def done(func):
    return


@debug_func
async def func_1():
    await asyncio.sleep(1)
    await done(func_1)


@debug_func
async def func_2():
    await asyncio.sleep(1)
    await done(func_2)


loop = asyncio.get_event_loop()
loop.set_debug(True)

asyncio.ensure_future(func_1())
asyncio.ensure_future(func_2())
asyncio.ensure_future(func_1())
asyncio.ensure_future(func_2())
asyncio.ensure_future(func_1())
asyncio.ensure_future(func_2())

loop.run_forever()
