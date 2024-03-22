'''
file that holds the basic config for redis queue
'''
import os

HOST = os.environ.get('REDIS_SERVICE_HOST', 'localhost' )
PORT = os.environ.get('REDIS_SERVICE_PORT', 6379 )
DB = 0