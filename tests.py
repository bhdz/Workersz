'''
Created on Aug 8, 2015

@author: dakkar
'''
import unittest
from workersz.base import WorkerBase


if __name__ == "__main__":
    from workersz.base import check_WorkerBase
    
    checks = [
              check_WorkerBase,
              ]
    
    for check in checks:
        check()
        