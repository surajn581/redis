
class EnvironVarEnums:
    HOST_NAME = 'HOSTNAME'
    REDIS_SERVICE_HOST = 'REDIS_SERVICE_HOST'
    REDIS_SERVICE_PORT = 'REDIS_SERVICE_PORT'

class WorkItemEnums:
    CLASS_NAME = 'CLASS_NAME'

class QueueConfigEnums:
    DEFAULT_HOST = 'localhost'
    DEFAULT_PORT = 6379
    DB = 0

class WorkerMonitorEnums:
    LIVENESS_THRESHOLD = 'LIVENESS_THRESHOLD'

class QueueEnums:
    HEARTBEATS = 'heartbeats'
    PROCESSED = 'processed'
    FAILURE_COUNTS_MAP = 'failure_counts_map'
    PENDING = 'pending'
    DEAD_WORKERS = 'deadworkers'