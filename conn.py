'''
file that has the redis client connection object
'''
import redis
import logging
import time
from queue_config import HOST, PORT, DB

logger = logging.getLogger('Worker')
logger.setLevel(logging.DEBUG)
console = logging.StreamHandler()
logger.addHandler(console)

def retry(ntry=6):
    def _retry(f):
        def call(*args, **kwargs):
            for tri in range(ntry):
                logger.info(f'Attempt {tri+1}/{ntry} on function: {f.__name__}...')
                try:
                    f(*args)
                    break
                except Exception as ex:
                    wait_time = 2**tri
                    logger.error(f'could not succeed: {f.__name__} due to: {ex}')
                    logger.info(f'will retry after {wait_time} seconds')
                    time.sleep(wait_time)
        return call
    return _retry

RedisConn = redis.Redis(host=HOST, port=PORT, db=DB)

@retry(ntry=7)
def main():
    RedisConn.ping()

main()