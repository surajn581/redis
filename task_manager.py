import time
from work_publisher import WorkPublisherBase
from utils import logger
from enums import QueueEnums

class TaskManager:

    def __init__(self, publisher: WorkPublisherBase):
        self.publisher = publisher
        self.conn = publisher.conn
        self.task_queue = publisher.name

    def worker_pending_queue(self, worker):
        return f'{worker}:{QueueEnums.PENDING}'

    def _republish_work(self, worker):
        while self.conn.scard(self.worker_pending_queue(worker)):
            work = self.conn.spop(self.worker_pending_queue(worker))
            self.conn.zadd(self.task_queue, {work:0})
            logger.info(f'work: {work} republished')

    def _get_dead_workers(self):
        return self.conn.smembers(QueueEnums.DEAD_WORKERS)

    def _manage(self):
        dead_workers = self._get_dead_workers()
        logger.info(f'dead worker count is: {len(dead_workers)}')
        for worker in dead_workers:
            if not self.conn.scard(self.worker_pending_queue(worker)):
                continue            
            logger.info(f'republishing work items abandoned by worker: {worker} into queue {self.task_queue}')
            self._republish_work(worker)

    def manage(self):
        while True:            
            self._manage()
            time.sleep(15)

def main():
    from work_publisher import WorkPublisher
    manager = TaskManager(publisher=WorkPublisher())
    manager.manage()

if __name__ == '__main__':
    main()