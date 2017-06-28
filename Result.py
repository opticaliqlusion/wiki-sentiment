import util
import hashlib


class Result(object):
    pass
    
# cacheable result class so we can easily pause, cancel, and resume processing
class SentimentResult(Result, util.CachableMixin):

    def __init__(self, name, pageid, timestamp, length=0, score=None, magnitude=None):
        self.name = name
        self.score = score
        self.pageid = pageid
        self.timestamp = timestamp
        self.magnitude = magnitude
        self.length = length
        return

    def __str__(self):
        return '<SentimentResult [{}:{}] Score:{} Magnitude:{} Length:{}>'.format(self.name, 
            self.pageid, self.score, self.magnitude, self.length)
        
    def __copy__(self, other):
        self.__dict__ = other.__dict__.copy()
        
    def __hash__(self):
        
        # dont use python's built-in hash() function;
        # the hashes are different per-process, which
        # totally defeats the purpose of the cache
        
        md5 = hashlib.md5()
        md5.update(self.name.encode())
        md5.update(str(self.pageid).encode())
        md5.update(self.timestamp.encode())

        return int(md5.hexdigest(), 16)