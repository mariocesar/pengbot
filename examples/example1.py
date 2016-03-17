import logging
import re

import pengbot

logger = logging.getLogger(__name__)


class SensitiveInformation(Exception):
    pass


@pengbot.robot()
def bob(context):
    context.full_name = 'Bob Robot'
    return context


@bob.discussion()
def ask_order(discuss):
    with discuss.ask('What flavor do you want?') as reply:
        discuss.say('%s! great decision!' % reply.message)
        discuss.context.flavor = reply.message

    return ask_size(discuss)


@bob.discussion()
def ask_size(discuss):
    with discuss.ask('What size?') as reply:
        discuss.say('Great ! %s will be.' % reply.message)
        discuss.context.size = reply.message

    with discuss.askYesNo('Do you want something to drink?') as reply:
        discuss.context.beverage = None

        if reply.afirmative:
            discuss = ask_beverage(discuss)

    return ask_deliver(discuss)


@bob.discussion()
def ask_beverage(discuss):
    with discuss.askChoice('What soda do you want?', choices=['coke', 'pepsi']) as reply:
        discuss.say('%s! great decision!' % reply.message)
        discuss.context.beverage = reply.message

    return discuss


@bob.discussion()
def ask_deliver(discuss):
    discuss.context.deliver = False

    with discuss.askYesNo('Do you want to be deliver?') as reply:
        discuss.say('Great ! %s will be.' % reply.text)
        discuss.context.deliver = True


@bob.hears(contains='pizzatime')
def pizza_time(message):
    bob.says('pizza time! yes!')

    with ask_order.start() as discussion:
        if discussion.context.deliver:
            bob.says("Done! A {flavor} pizza {size} is on the way".format(**discussion.context))
        else:
            bob.says("Done! I ordered a {flavor} pizza {size}".format(**discussion.context))


@bob.hears(regexp=r'(?P<issue>[A-Z]{2,}-\d+)')
def reply_jira_issue(message):
    issue = message.match.groups(0)
    bob.says("({0})[http://jira.acme.com/issues/{0}/]".format(issue))


def hear_github_issues(message):
    match = re.match(r'#(?P<issue>\d+)', message.text)
    blacklist_issues = ['12', '13', '14', '10']

    if match:
        issue = match.groupdict()['issue']
        return issue if issue not in blacklist_issues else None


@bob.hears(hear_github_issues)
def reply_github_issues(message):
    issue = message.match
    bob.says("({0})[http://github.com/mariocesar/pengbot/issues/{0}/]".format(issue))


@bob.command()
def hello():
    bob.says('Hello')


@bob.command(alias='good bye')
def bye():
    bob.says('Good bye')


@bob.command(alias=['now', 'what time is it?'])
def say_time():
    """Return the current time"""
    from datetime import datetime

    bob.says('The current date and time is {}'.format(datetime.now()))


@bob.command()
def uptime():
    """Uptime of the host machine"""
    from datetime import timedelta

    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
        uptime_string = str(timedelta(seconds=uptime_seconds))

    bob.says(uptime_string)


@bob.receiver(pengbot.signals.before_shutdown)
def say_goodbye(context):
    bob.says('Good bye')


@bob.receiver(pengbot.signals.before_start)
def update_context(context):
    context.hostname = 'ip-127.0.0.1'


@bob.receiver(pengbot.signals.after_start)
def say_hi(context):
    bob.says("Hello I'm bob and I'm happy to serve!")


@bob.receiver(pengbot.signals.before_reply)
def check_sensitive_information(context, message):
    if 'password' in message.text:
        raise SensitiveInformation()


@bob.receiver(pengbot.signals.after_reply)
def log_message(message):
    logger.log(message.text)


if __name__ == '__main__':
    try:
        bob.start()
    except KeyboardInterrupt:
        bob.shutdown()
