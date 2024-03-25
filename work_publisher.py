'''
file that creates and publishes work to the redis queue
'''
import time
from abc import ABC, abstractmethod
from conn import RedisConn as conn
from work_item import BlockWorkItem, WorkItemBase
from utils import logger

def create_work_item():
    return BlockWorkItem()

class WorkPublisherBase(ABC):
    '''base class for work publisher'''
    def __init__(self, conn, name = None):
        self.conn = conn
        self.name = name or self.__class__.__name__

    @abstractmethod
    def publish_work(self, *args, **kwargs):
        raise NotImplementedError('subclass needs to implement this method')


class WorkPublisher(WorkPublisherBase):
    ''' class that publishes work to redis queue '''
    
    def __init__(self, name=None):
        super().__init__(conn = conn, name = name)

    def enqueue(self, work:str):
        self.conn.zadd(self.name, {work: 0})

    def work_items(self):
        work_items = [create_work_item() for i in range(30)]
        return work_items

    def publish_work(self, work:WorkItemBase):
        logger.info('publishing work: %s to queue: %s', work, self.name)
        self.enqueue(work.json())

    def publish(self):
        while True:
            for work_item in self.work_items():
                self.publish_work(work_item)
            time.sleep(120)

def main():
    publisher = WorkPublisher()
    publisher.publish()

if __name__ == '__main__':
    main()