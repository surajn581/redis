'''
file that holds the basic config for redis queue
'''
import os
from enums import QueueConfigEnums, EnvironVarEnums

HOST = os.environ.get(EnvironVarEnums.REDIS_SERVICE_HOST, QueueConfigEnums.DEFAULT_HOST)
PORT = os.environ.get(EnvironVarEnums.REDIS_SERVICE_PORT, QueueConfigEnums.DEFAULT_PORT)
DB = QueueConfigEnums.DB