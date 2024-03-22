import time
import logging

class Timer:

    def __init__(self, msg = ''):
        self.msg = msg
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        self._elapsed = None

    @property
    def elapsed(self):
        if self._elapsed:
            return self._elapsed
        raise ValueError('elapsed time not found')

    def __enter__(self):
        self.start_time = time.time()

    def __exit__(self, *args, **kwargs):
        end = time.time()
        self._elapsed = end - self.start_time
        self.logger.info('%s took %s seconds', self.msg, self.elapsed)