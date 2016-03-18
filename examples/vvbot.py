import asyncio
import re

import pengbot


class Everything:
    def __call__(self, context, data):
        return True


class Message:
    def __call__(self, context, data):
        if data.get('type', None) == 'message':
            if 'reply_to' not in data:
                # Dimiss messages from lost connections
                return True
        return False


class DirectMessage(Message):
    def __call__(self, context, data):
        if super().__call__(context, data):
            return data['channel'] in context['ims']
        return False


class Mention(Message):
    def __call__(self, context, data):
        if super().__call__(context, data):
            if 'text' in data:
                return '<@%s>' % context['self']['id'] in data['text']
        return False


@pengbot.robot(name='vvbot', api_token='xoxb-27602091572-A0ZsTeWGR5d0pIYHnV7tpf0B')
def vvbot(bot):
    bot.logger.info('Hi')


@vvbot.hears(Everything)
@asyncio.coroutine
def hears_everything(bot, message):
    bot.logger.info('Everything callback %s', message)


@vvbot.hears(Mention, DirectMessage)
@asyncio.coroutine
def count_to_10(bot, message):
    bot.logger.info(message)
    match = re.match(r'.*cuenta hasta (?P<limit>\-?\d+).*', message['text'], re.IGNORECASE)
    channel = message['channel']

    if match:
        limit = int(match.groupdict().get('limit'))
        bot.logger.info('Contare hasta %s' % limit)

        if limit > 20:
            yield from bot.says('... solo se contar hasta 20 :\'(', channel)
        elif limit <= 0:
            yield from bot.says('... lo siento, no se contar hasta %s :(' % limit, channel)
        else:
            yield from bot.says('Seguro! contare hasta %s!' % limit, channel)
            yield from asyncio.sleep(0.5)

            for n in range(1, limit + 1):
                yield from bot.says('%s .. ' % n, channel)
                yield from asyncio.sleep(0.5)


@vvbot.hears(DirectMessage)
@asyncio.coroutine
def talking_parrot(bot, message):
    bot.logger.debug(message)

    yield from bot.says(':bird: %s' % message['text'], message['channel'])


if __name__ == '__main__':
    vvbot()
