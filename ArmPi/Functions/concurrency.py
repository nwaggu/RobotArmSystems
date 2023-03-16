import concurrent.futures
from readerwriterlock import rwlock

class Bus():
    def __init__(self, message):
        self.message = message
        self.lock = rwlock.RWLockWriteD()
    
    def write(self, new_message):
        with self.lock.gen_wlock():
            self.message = new_message
        
    def read(self):
        with self.lock.gen_rlock():
            message = self.message
        return message


