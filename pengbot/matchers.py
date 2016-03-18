import re
from difflib import SequenceMatcher

__all__ = ('listener',)


class Everything:
    def __call__(self, context, message):
        return True


class FuzzyMatch:
    """
    Fuzzy String Matching.

        >>> match = FuzzyMatch('Good morning')
        >>> match({'text': 'Good morning all!'})
        ... True
        >>> match({'text': 'Good morning!'})
        ... True
        >>> match({'text': 'Good mornin'})
        ... True
    """

    def __init__(self, compare_to):
        self.compare_to = compare_to

    def __call__(self, context, message):
        match = SequenceMatcher(None, message['text'], self.compare_to)
        if match.ratio() > 0.99:
            return True


class PatternMatch:
    """
    Simple Pattern String Matching.

    #TODO: Extract matching groups if any

        >>> match = PatternMatch('#(?P<number>\d+)')
        >>> match('Issue ticket #3001')
        True
    """

    def __init__(self, pattern):
        self.pattern = re.compile(pattern)

    def __call__(self, context, message):
        raise NotImplementedError()


class Command:
    """
    Command definition matching.

        >>> Command('kudos', '[<username> ...]')
        >>> Command('count', '<variable:str> <value:int> | <variable:str>')
    """

    def __init__(self, command):
        self.regexp = re.compile(r'^/%s' % command, flags=re.IGNORECASE)

    def __call__(self, context, message):
        text = message['text'].strip()

        if self.regexp.match(text):
            # TODO: Extract arguments
            return True
