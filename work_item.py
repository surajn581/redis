'''
definition of work item class
'''

from abc import ABC, abstractmethod
import logging
import random
import time
import json
import sys

logger = logging.getLogger('WorkItem')
logger.setLevel(logging.DEBUG)
console = logging.StreamHandler()
logger.addHandler(console)

class WorkItemBase(ABC):
    '''base class to define a work item'''
    def __init__(self, name=None):
        self.name = name or self.__class__.__name__    

    def __repr__(self) -> str:
        return f'{self.name}'

    @abstractmethod
    def payload(self, *args, **kwargs):
        '''method that give the payload that must to dumped as a json so that it can be put into redis queue'''
        raise NotImplementedError('subclass needs to implement this method')
    
    def json(self):
        return WorkItemFactory.covert_to_json(self)
    
    @staticmethod
    def from_json(payload):
        return WorkItemFactory.init_from_json(payload)
    
    @abstractmethod
    def execute(self, *args, **kwargs):
        raise NotImplementedError('subclass must implement this method')

class BlockWorkItem(WorkItemBase):
    ''' work item that blocks the worker for a set amount of time '''

    def __init__(self, name = None, time = None):
        super().__init__(name)
        self.time = time or random.randint(0, 5)

    def __repr__(self) -> str:
        return f'{super().__repr__()} with block time: {self.time}'
    
    def payload(self):
        return dict(name = self.name, time = self.time)

    def execute(self, *args, **kwargs):
        if random.randint(1, 10) == 1:
            raise Exception('raising exception to mimic failures')
        logger.info('sleeping for %s seconds', self.time)
        time.sleep(self.time)
        return True

class WorkItemFactory:

    @staticmethod
    def _get_implementation(cls_name):
        module = sys.modules[__name__]
        return getattr(module, cls_name)
    
    @staticmethod
    def init_from_json(payload:str):
        payload = json.loads(payload)
        cls_name = payload.pop('cls_name')
        return WorkItemFactory._get_implementation(cls_name)(payload)
    
    def covert_to_json(work_item:WorkItemBase):
        payload = work_item.payload()
        cls = work_item.__class__.__name__
        payload.update( dict(cls_name = cls) )
        return json.dumps(payload)