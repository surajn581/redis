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

    def _get_dead_workers(self):
        return self.conn.smembers('dead_workers')

    def _manage(self):
        dead_workers = self._get_dead_workers()
        logger.info(f'dead worker count is: {len(dead_workers)}')
        for worker in dead_workers:
            if not self.conn.scard(worker):
                continue
            self._republish_work(worker)

    def manage(self):
        while True:            
            self._manage()
            time.sleep(15)

def main():
    from work_publisher import URLWorkPublisher
    manager = TaskManager(publisher=URLWorkPublisher())
    manager.manage()

if __name__ == '__main__':
    main()