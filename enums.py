
class EnvironVarEnums:
    HOST_NAME = 'HOSTNAME'
    REDIS_SERVICE_HOST = 'REDIS_SERVICE_HOST'
    REDIS_SERVICE_PORT = 'REDIS_SERVICE_PORT'

class WorkPublisherEnvironVarEnums(EnvironVarEnums):
    SLEEP_INTERVAL = 'WORKER_PUBLISHER_SLEEP_INTERVAL'
    NUM_WORK_ITEMS = 'WORKER_PUBLISHER_NUM_WORK_ITEMS'

class WorkItemEnums:
    CLASS_NAME = 'CLASS_NAME'

class QueueConfigEnums:
    DEFAULT_HOST = 'localhost'
    DEFAULT_PORT = 6379
    DB = 0

class WorkerMonitorEnvironVarsEnums(EnvironVarEnums):
    LIVENESS_THRESHOLD = 'WORKER_MONITOR_LIVENESS_THRESHOLD'
    NUM_RETRY_STUCK_WORKER = 'WORKER_MONITOR_NUM_RETRY_STUCK_WORKER'

class WorkerEnvironVarsEnums(EnvironVarEnums):
    FAILURE_NUM_RETRY = 'WORKER_NUM_RETRY'

class TaskManagerEnvironVarsEnums(EnvironVarEnums):
    SLEEP_INTERVAL = 'TASK_MANAGER_SLEEP_INTERVAL'

class QueueEnums:
    HEARTBEATS = 'heartbeats'
    PROCESSED = 'processed'
    FAILURE_COUNTS_MAP = 'failure_counts_map'
    PENDING = 'pending'
    DEAD_WORKERS = 'deadworkers'