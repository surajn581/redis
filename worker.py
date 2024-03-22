'''
file that defines the worker that polls and excutes the work
'''

import logging
import time
import uuid
import os
from utils import Timer
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
        return self.conn.brpop(self.queue)[1]
    
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
        return res

    @abstractmethod
    def handle_result(self, result, *args, **kwargs):
        raise NotImplementedError('subclass needs to implement this method')
    
    def handle_failure(self, work):
        logger.error(f'resubmitting to queue: {self.queue}')
        self.publisher.publish_work(work)
    
    def _run(self):
        work = self.get_work()
        if not work:
            return
        try:
            res = self.execute(work)
            self.handle_result(res)
        except Exception as ex:
            logger.error(f'failed to execute work: {work} due to: {ex}')
            self.handle_failure(work)

    def run(self):
        while True:
            self._run()
        
class Worker(WorkerBase):

    def __init__(self, publisher:WorkPublisherBase):
        super().__init__(publisher)
        self.name = os.environ.get('HOSTNAME', self.__class__.__name__ + uuid.uuid4().hex)

    def get_work(self):
        work = super().get_work()        
        if work:
            self.conn.lpush(self.name, work.json())
            return work
        time.sleep(1)

    def execute(self, work: WorkItemBase, *args, **kwargs):
        with Timer(f'executing work: {work}') as timer:
            res = super().execute(work, *args, **kwargs)
        return res

    def handle_result(self, result, *args, **kwargs):
        logger.info('handling result: %s', result)
        self.conn.lpush(f'{self.name}:processed', result)

    def handle_failure(self, work):
        self.conn.lpush(f'{self.name}:failure', work.json())
        return super().handle_failure(work)

def main():
    from work_publisher import WorkPublisher
    worker = Worker(publisher=WorkPublisher())
    worker.run()

if __name__ == '__main__':
    main()
