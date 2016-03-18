import logging

from .utils import colorize


class ColorizingStreamHandler(logging.StreamHandler):
    def __init__(self):
        super().__init__()

        self.level_map = {
            # LEVEL: (background, foreground, bold/normal/underscore)
            logging.DEBUG: (None, 'blue', 'normal'),
            logging.INFO: (None, 'white', 'normal'),
            logging.WARNING: (None, 'yellow', 'normal'),
            logging.ERROR: (None, 'red', 'normal'),
            logging.CRITICAL: ('red', 'white', 'bold'),
        }

    @property
    def is_tty(self):
        "Returns true if the handler's stream is a terminal."
        isatty = getattr(self.stream, 'isatty', None)
        return isatty and isatty()

    def emit(self, record):
        try:
            msg = self.format(record)
            stream = self.stream

            if record.levelno in self.level_map:
                bg, fg, style = self.level_map[record.levelno]
                with colorize(bg, fg, style, stream=self.stream):
                    stream.write(msg)
            else:
                stream.write(msg)
            stream.write(self.terminator)
            self.flush()
        except Exception:
            self.handleError(record)


def getLogger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = ColorizingStreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s [%(name)s] %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
