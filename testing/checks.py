'''
Created on Aug 11, 2015

@author: dakkar
'''
# WARNING This is not proper testing but eyechecks. Run all checks from the
#  source tree
if __name__ == '__main__':
    from testing.check_base import check_base
    
    checks = [
              check_base
              ]
    for check in checks:
        check()