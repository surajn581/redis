'''
definition of work item class
'''
import random
import time
import json
import sys
import uuid
from abc import ABC, abstractmethod
from utils import logger
from enums import WorkItemEnums

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
        name = name or ( '{}-{}'.format( self.__class__.__name__, uuid.uuid4().hex ) )
        super().__init__(name)
        self.time = time or random.randint(0, 5)

    def __repr__(self) -> str:
        return f'{super().__repr__()} with block time: {self.time}'
    
    def payload(self):
        return dict(name = self.name, time = self.time)
    
    def execute(self, *args, **kwargs):
        if random.randint(1, 10) <= 3:
            raise Exception('raising exception to mimic failures')
        logger.info('sleeping for %s seconds', self.time)
        time.sleep(self.time)
        return self.name

class WorkItemFactory:

    @staticmethod
    def _get_implementation(cls_name):
        module = sys.modules[__name__]
        return getattr(module, cls_name)
    
    @staticmethod
    def init_from_json(payload:str):
        payload = json.loads(payload)
        cls_name = payload.pop(WorkItemEnums.CLASS_NAME)
        impl = WorkItemFactory._get_implementation(cls_name)
        return impl(**payload)
    
    def covert_to_json(work_item:WorkItemBase):
        payload = work_item.payload()
        cls = work_item.__class__.__name__
        payload.update( {WorkItemEnums.CLASS_NAME:cls} )
        return json.dumps(payload)