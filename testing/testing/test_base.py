'''
Created on Aug 11, 2015

@author: dakkar
'''
from workersz.base import Worker

def check_Base():
    pass

if __name__ == "__main__":
    from workersz.base import check_WorkerBase
    
    checks = [
              check_WorkerBase,
              ]
    
    for check in checks:
        check()