'''
file that defines the worker that polls and excutes the work
'''
import traceback
import time
import uuid
import os
from datetime import datetime
from utils import Timer
from abc import ABC, abstractmethod
from work_item import WorkItemFactory, WorkItemBase
from work_publisher import WorkPublisherBase
from utils import logger
from enums import EnvironVarEnums, QueueEnums


class WorkerBase(ABC):
    def __init__(self, publisher: WorkPublisherBase):
        self.publisher = publisher
        self.name = os.environ.get(EnvironVarEnums.HOST_NAME, self.__class__.__name__ + uuid.uuid4().hex)

    @property
    def conn(self):
        return self.publisher.conn
    
    @property
    def task_queue(self):
        return self.publisher.name
    
    def send_heartbeat(self):
        self.conn.hset(QueueEnums.HEART_BEATS, self.name, datetime.now().timestamp())

    def dequeue(self):
        return self.conn.bzpopmax(self.task_queue)[1]
    
    def get_work(self):
        payload = self.dequeue()
        work = WorkItemFactory.init_from_json(payload)
        logger.info('got work: %s from queue: %s', work, self.task_queue)
        return work
    
    def execute(self, work:WorkItemBase, *args, **kwargs):
        logger.info('executing work: %s with args: %s and kwargs: %s', work, args, kwargs)
        res = work.execute(*args, **kwargs)
        return res

    @abstractmethod
    def handle_result(self, work, result, *args, **kwargs):
        raise NotImplementedError('subclass needs to implement this method')
    
    def handle_failure(self, work):
        logger.error(f'resubmitting to queue: {self.task_queue}')
        self.publisher.publish_work(work)
    
    def _run(self):
        self.send_heartbeat()
        work = self.get_work()
        try:
            res = self.execute(work)
            self.handle_result(work, res)
        except Exception as ex:
            logger.error(f'failed to execute work: {work} due to: {ex}')
            logger.error(f'traceback: {traceback.format_exc()}')
            self.handle_failure(work)

    def run(self):
        while True:
            self._run()
        
class Worker(WorkerBase):

    def __init__(self, publisher:WorkPublisherBase):
        super().__init__(publisher)        

    def get_work(self):
        work = super().get_work()
        if work:
            self.conn.sadd(self.pending_queue_name, work.json())
            return work
        time.sleep(1)

    def execute(self, work: WorkItemBase, *args, **kwargs):
        with Timer(f'executing work: {work}') as timer:
            return super().execute(work, *args, **kwargs)
        
    @property
    def pending_queue_name(self):
        return f'{self.name}:{QueueEnums.PENDING}'
        
    @property
    def result_queue_name(self):
        return f'{self.name}:{QueueEnums.PROCESSED}'
    
    @property
    def failure_counts_map_name(self):
        return f'{self.name}:{QueueEnums.FAILURE_COUNTS_MAP}'

    def handle_result(self, work, result, *args, **kwargs):
        logger.info('handling result: %s', result)
        self.conn.sadd(self.result_queue_name, work.json())
        self.conn.srem(self.pending_queue_name, work.json())

    def handle_failure(self, work):
        try_count = self.conn.hget(self.failure_counts_map_name, work.name)
        if try_count and int( try_count ) >= 5:
            logger.warn(f'work: {work} has been tried: {int(try_count)} times, it will not be processed again')
            return
        self.conn.hincrby(self.failure_counts_map_name, work.name, 1)
        return super().handle_failure(work)

def main():
    from work_publisher import WorkPublisher
    worker = Worker(publisher=WorkPublisher())
    worker.run()

if __name__ == '__main__':
    main()
