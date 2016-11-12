import aiohttp
import aiohttp_jinja2
from aiohttp import web


async def websocket_handler(request):
    response = web.WebSocketResponse(autoclose=False)
    ok, protocol = response.can_prepare(request)

    await response.prepare(request)

    for _room in request.app['rooms'].values():
        print('room: ', _room)
        if _room is not response:
            _room.send_json({'event': 'someone joined'})

    print('Starting rooms', request.app['rooms'])

    async for msg in response:
        if msg.type == aiohttp.WSMsgType.TEXT:
            print('message received: ', msg.type, msg.data)

            message = msg.json()
            room = request.app['rooms'].get(message['room'], None)

            print('available rooms: ', request.app['rooms'])
            print('room: ', room)

            if room is None:
                request.app['rooms'][message['room']] = response
                room = response
                room.send_json({'event': '%s joined to room' % message['sender_id']})

            if room is not response:
                response.send_json(msg.json())

            room.send_json(msg.json())

        elif msg.type == aiohttp.WSMsgType.ERROR:
            print('ws connection closed with exception %s' % response.exception())

    print('websocket connection closed')


@aiohttp_jinja2.template('index.html')
async def index_handler(request):
    room = request.match_info['room']
    return {'room': room}
