import os

import asyncio

import aiohttp_jinja2
import jinja2
from aiohttp import web
from .views import index_handler, websocket_handler

loop = asyncio.get_event_loop()

location = lambda path: os.path.join(os.path.dirname(os.path.abspath(__file__)), path)


def main(argv):
    app = web.Application(loop=loop)
    app['rooms'] = {}
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(location('templates')))

    app.router.add_static('/static/', path=location('static'), name='static')
    app.router.add_get(r'/', index_handler)
    app.router.add_get(r'/socket', websocket_handler)
    app.router.add_get(r'/rooms/{room:\w+}', index_handler)

    return app
