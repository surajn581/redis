from work_publisher import WorkPublisherBase
from utils import logger
import time

class TaskManager:

    def __init__(self, publisher: WorkPublisherBase):
        self.publisher = publisher
        self.conn = publisher.conn
        self.queue = publisher.name

    def _republish_work(self, worker):
        logger.info(f'republishing work items abandoned by worker: {worker} into queue {self.queue}')
        while self.conn.scard(worker):
            work = self.conn.spop(worker)
            self.conn.lpush(self.queue, work)
            logger.info(f'work: {work} republished')

    def republish_work(self):
        dead_workers = self.conn.smembers('dead_workers')
        logger.info(f'found {len(dead_workers)} dead workers: {dead_workers}')
        for worker in dead_workers:
            self._republish_work(worker)

    def manage(self):
        while True:            
            self.republish_work()
            time.sleep(120)

def main():
    from work_publisher import WorkPublisher
    manager = TaskManager(publisher=WorkPublisher())
    manager.manage()

if __name__ == '__main__':
    main()