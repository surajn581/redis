'''
file that creates and publishes work to the redis queue
'''
import time
import random
from abc import ABC, abstractmethod
from conn import RedisConn as conn
from work_item import BlockWorkItem, WorkItemBase, URLWorkItem
from utils import logger
import re
import hashlib
import requests
from bs4 import BeautifulSoup

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
        self.conn.lpush(self.name, work)

    def work_items(self):
        work_items = [create_work_item() for i in range(30)]
        return work_items

    def publish_work(self, work:WorkItemBase):
        logger.info('publishing work: %s to queue: %s', work, self.name)
        self.enqueue(work.json())

    def publish(self):
        for work_item in self.work_items():
            self.publish_work(work_item)

class URLWorkPublisher(WorkPublisher):

    def __init__(self, name=None):
        super().__init__(name)
        self.seed_url_location = '/mnt/data/url.txt'

    @staticmethod
    def hash_url(url):
        return int(hashlib.md5(url.encode('utf-8')).hexdigest(), 16)
    
    @staticmethod
    def find_child(url):
        page = requests.get(url)
        soup = BeautifulSoup(page.content)
        newlinks = []
        for link in  soup.find_all("a",href=re.compile("htt.*://.*")):
            newlinks.extend(re.split(":(?=http)",link["href"]))
        return list( set(newlinks) )
    
    def create_work_item( self, url, name ):
        return URLWorkItem( url = url, name = name )

    def _publish_work_items(self, url):
        stack = [url]
        visited_set_name = f'{self.__class__.__name__}:visited'
        while stack and int( self.conn.scard(visited_set_name) )<1024:
            url = stack.pop()
            name = self.hash_url(url)
            if  self.conn.sismember( visited_set_name, name ):
                continue
            try:
                child_urls = self.find_child(url)
            except Exception as ex:
                child_urls = []
                logger.error(f'could not find children for: {url} due to: {ex}')
                continue
            self.publish_work( self.create_work_item( url, name ) ) 
            self.conn.sadd( visited_set_name, name )
            stack.extend(child_urls)

    def get_seed_url(self):
        with open(self.seed_url_location, 'r') as f:
            lines = [line.rstrip() for line in f.readlines() if line.rstrip()]
            return lines[-1]

    def publish(self):
        url = self.get_seed_url()
        logger.info(f'got seed url: {url} from file: {self.seed_url_location}')
        self._publish_work_items(url)

def main():
    publisher = URLWorkPublisher()
    publisher.publish()

if __name__ == '__main__':
    main()