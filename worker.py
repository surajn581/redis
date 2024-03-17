'''
file that defines the worker that polls and excutes the work
'''

import logging
import time
from abc import ABC, abstractmethod
from work_item import WorkItemFactory, WorkItemBase
from work_publisher import WorkPublisherBase
logger = logging.getLogger('Worker')
logger.setLevel(logging.DEBUG)
console = logging.StreamHandler()
logger.addHandler(console)

class WorkerBase(ABC):
    def __init__(self, publisher: WorkPublisherBase):
        self.publisher = publisher

    @property
    def conn(self):
        return self.publisher.conn
    
    @property
    def queue(self):
        return self.publisher.name

    def dequeue(self):
        return self.conn.rpop(self.queue)
    
    def get_work(self):
        payload = self.dequeue()
        if not payload:
            logger.info('queue: %s is empty', self.queue)
            return
        work = WorkItemFactory.init_from_json(payload)
        logger.info('got work: %s from queue: %s', work, self.queue)
        return work
    
    def execute(self, work:WorkItemBase, *args, **kwargs):
        logger.info('executing work: %s with args: %s and kwargs: %s', work, args, kwargs)
        res = work.execute(*args, **kwargs)

    @abstractmethod
    def handle_result(self, result, *args, **kwargs):
        raise NotImplementedError('subclass needs to implement this method')
    
    def _run(self):
        work = self.get_work()
        if not work:
            return
        try:
            res = self.execute(work)
            self.handle_result(res)
        except Exception as ex:
            logger.error('failed to execute work: %s due to: %s, resubmitting to queue', work, ex, self.queue)
            self.publisher.publish_work(work)

    def run(self):
        while True:
            self._run()
        
class Worker(WorkerBase):

    def __init__(self, publisher:WorkPublisherBase):
        super().__init__(publisher)

    def get_work(self):
        work = super().get_work()
        if not work:
            time.sleep(1)
        return work

    def handle_result(self, result, *args, **kwargs):
        logger.info('handling result: %s', result)

def main():
    from work_publisher import WorkPublisher
    worker = Worker(publisher=WorkPublisher())
    worker.run()

if __name__ == '__main__':
    main()
