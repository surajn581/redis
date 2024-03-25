import time
import logging
formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-4s %(message)s',datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
console = logging.StreamHandler()
console.setFormatter(formatter)
logger.addHandler(console)
logger.warn = logger.warning

class Timer:

    def __init__(self, msg = ''):
        self.msg = msg
        self._elapsed = None

    @property
    def elapsed(self):
        if self._elapsed is not None:
            return self._elapsed
        raise ValueError('elapsed time not found')

    def __enter__(self):
        self.start_time = time.time()

    def __exit__(self, *args, **kwargs):
        end = time.time()
        self._elapsed = end - self.start_time
        logger.info('%s took %s seconds', self.msg, self.elapsed)