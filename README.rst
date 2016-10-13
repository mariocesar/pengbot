Pengbot: For building robots with human manners
===============================================

**warning:** Pengbo is currently in DESIGN

.. code-block:: python

    import pengbot
    from pengbot.adapters.slack import SlackRobot, Mention


    @pengbot.robot(adapter=SlackRobot)
    def mybot(bot):
        bot.context = bot.context(
            api_token=os.environ.get('SLACK_API_TOKEN', None)
        )


    @mybot.hears(Mention)
    def talking_parrot(bot, message):
        yield from bot.says(':bird: %s' % message['text'] , channel=message['channel'])


    if __name__ == '__main__':
        mybot()

Installation
------------

.. code-block:: bash

    $ pip install pengbot

Documentation
-------------

.. TODO


TODO
----

    - Fuzzy string match for commands
    - Commands receive message context.
    - Listen all messages to trigger commands.
    - Adapters for Slack, XMPP, Twitter.
    - Message stream filters.
    - Message stream middlewares.
    - Stream response messages.
    - Natural Language Processing?. http://spacy.io

Example ideas
-------------

    - Auto linking for Jira Issues.
    - Attach user mentions to issues as comments in Jira.
    - Bots talking to bots.
    - Voting and Polls.
