import os
import uuid
import time
from datetime import datetime
from conn import RedisConn as conn
from utils import logger


class WorkerMonitor:
    def __init__(self):
        self.name = os.environ.get('HOSTNAME', self.__class__.__name__ + uuid.uuid4().hex)
        self.conn = conn

    def monitor(self):
        while True:
            if not self.conn.hlen('heartbeats'):
                continue
            self._monitor()            
            time.sleep(120)

    def declare_dead_worker(self, worker):
        self.conn.sadd('dead_workers', worker)
    
    def _monitor(self):
        heartbeats = self.conn.hgetall('heartbeats')
        for worker, timestamp in heartbeats.items():
            if self.conn.sismember('dead_workers', worker):
                continue
            if not datetime.now().timestamp() - float(timestamp) > 120:
                logger.info(f'worker: {worker} is live')
                continue
            logger.info(f'declaring worker: {worker} dead')
            self.declare_dead_worker(worker)

def main():
    monitor = WorkerMonitor()
    monitor.monitor()

if __name__ == '__main__':
    main()