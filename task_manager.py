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
        logger.info(f'found {len(dead_workers)} dead workers: {dead_workers}')
        for worker in dead_workers:
            self._republish_work(worker)

        # writing a 2nd for loop instead of doing the cleanup in the above for loop so that
        # the work is resubmitted as soon as possible and only then the clean up begins
        for worker in dead_workers:
            self._cleanup_dead_worker_artifacts(worker)

    def _cleanup_dead_worker_artifacts(self, worker):
        self.conn.srem('dead_workers', worker)

    def manage(self):
        while True:            
            self._manage()
            time.sleep(120)

def main():
    from work_publisher import URLWorkPublisher
    manager = TaskManager(publisher=URLWorkPublisher())
    manager.manage()

if __name__ == '__main__':
    main()