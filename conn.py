'''
file that has the redis client connection object
'''

import redis
from queue_config import HOST, PORT, DB
RedisConn = redis.Redis(host=HOST, port=PORT, db=DB)

#ping the redis server, fail if fails
RedisConn.ping()