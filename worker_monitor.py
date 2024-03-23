import os
import uuid
import time
from datetime import datetime
from conn import RedisConn as conn
from utils import logger

LIVENESS_THRESHOLD = 120

class WorkerMonitor:
    def __init__(self, liveness_threshold = LIVENESS_THRESHOLD):
        self.name = os.environ.get('HOSTNAME', self.__class__.__name__ + uuid.uuid4().hex)
        self.conn = conn
        self.liveness_threshold = liveness_threshold

    def monitor(self):
        while True:
            if not self.conn.hlen('heartbeats'):
                continue
            self._monitor()            
            time.sleep(120)

    def declare_dead_worker(self, worker):
        self.conn.sadd('dead_workers', worker)

    def _handle_dead_worker(self, worker, timestamp):
        logger.info(f'declaring worker: {worker} dead, last timestamp: {timestamp}')
        self.declare_dead_worker(worker)
        logger.info(f'removing worker: {worker} hearbeat')
        self.conn.hdel('heartbeats', worker)
    
    def _monitor(self):
        heartbeats = self.conn.hgetall('heartbeats')
        for worker, timestamp in heartbeats.items():
            if self.conn.sismember('dead_workers', worker):
                continue
            if not datetime.now().timestamp() - float(timestamp) > self.liveness_threshold:
                logger.info(f'worker: {worker} is live')
                continue
            self._handle_dead_worker(worker, timestamp)

def main():
    monitor = WorkerMonitor()
    monitor.monitor()

if __name__ == '__main__':
    main()