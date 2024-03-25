import os
import uuid
import time
from datetime import datetime
from conn import RedisConn as conn
from utils import logger
from enums import EnvironVarEnums, QueueEnums, WorkerMonitorEnums

LIVENESS_THRESHOLD = os.environ.get(WorkerMonitorEnums.LIVENESS_THRESHOLD, 60)

class WorkerMonitor:
    def __init__(self, liveness_threshold = LIVENESS_THRESHOLD):
        self.name = os.environ.get(EnvironVarEnums.HOST_NAME, self.__class__.__name__ + uuid.uuid4().hex)
        self.conn = conn
        self.liveness_threshold = liveness_threshold

    def monitor(self):
        while True:
            if not self.conn.hlen(QueueEnums.HEART_BEATS):
                continue
            self._monitor()
            time.sleep(int(self.liveness_threshold/2))

    def declare_dead_worker(self, worker):
        self.conn.sadd(QueueEnums.DEAD_WORKERS, worker)

    def _handle_dead_worker(self, worker):
        self.declare_dead_worker(worker)
        logger.info(f'removing worker: {worker} hearbeat')
        self.conn.hdel(QueueEnums.HEART_BEATS, worker)

    def is_worker_live(self, worker, timestamp):
        delta = datetime.now().timestamp() - float(timestamp)
        if delta < self.liveness_threshold:
            return True
        logger.info(f'worker: {worker} has timestamp older than {self.liveness_threshold} seconds')
        logger.info(f'pending_queue name: {worker}:{QueueEnums.PENDING}')
        if not self.conn.scard(f'{worker}:{QueueEnums.PENDING}'):
            logger.info(f'worker: {worker} does not have any pending work items, it may not be dead')
            return True if delta <= self.liveness_threshold*10 else False
        logger.info(f'worker: {worker} is dead with last timestamp: {timestamp}')
        return False
    
    def _monitor(self):
        heartbeats = self.conn.hgetall(QueueEnums.HEART_BEATS)
        for worker, timestamp in heartbeats.items():
            if self.conn.sismember(QueueEnums.DEAD_WORKERS, worker):
                continue
            if self.is_worker_live(worker, timestamp):
                logger.info(f'worker: {worker} is live')
                continue            
            self._handle_dead_worker(worker)

def main():
    monitor = WorkerMonitor()
    monitor.monitor()

if __name__ == '__main__':
    main()