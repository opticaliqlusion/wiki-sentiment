import os
import pdb
import pickle
import unittest


class CachableMixin():

    #
    #   Overrides - implement these
    #

    def __hash__(self):
        'Mandatory key derivation method for looking up results in the cache'
        raise NotImplementedError('This method must be overidden')

    def __copy__(self, other):
        'Optional instance method to perform an internal copy from the cache'
        raise NotImplementedError('This method must be overidden')

    #
    #   Public attributes
    #
    
    @property
    def is_cached(self):
        self.__init_cache_file()
        return self.__key in self.__cache
        
    def __init_cache_file(self):
        if not os.path.exists(self.__cache_file):
            with open(self.__cache_file, "wb") as f:
                pickle.dump({}, f)
        return
        
    def load_from_cache(self):
        return self.__cache[self.__key]    
        
    def sync_with_cache(self):
        self.__copy__(self.__cache[self.__key])
    
    def cache(self):
        self.__init_cache_file()
        
        # load the cache
        cache = self.__cache
        cache[self.__key] = self
        
        # save the cache
        with open(self.__cache_file, "wb") as f:
            pickle.dump(cache, f)
            
    # aliases - for the lazy
    load = lambda self : self.load_from_cache()
    sync = lambda self : self.sync_with_cache()

    #
    #   Private attributes
    #

    @property
    def __key(self):
        return hash(self)
        
    @property
    def __cache_file(self):
        return "cache-{}.dat".format(self.__class__.__name__)
    
    @property
    def __cache(self):
        with open(self.__cache_file, "rb") as f:
            cache = pickle.load(f)
        return cache
              
        
class FooBase():
    pass

    
class Foo(CachableMixin, FooBase):
    def __init__(self, name, value=None):
        
        self.name = name
        self.value = value

    def __hash__(self):
        return hash(self.name)
        
    def __copy__(self, other):
        'the suggested implementation for basic objects'
        self.__dict__ = other.__dict__.copy()
        

class TestBasicFunctionality(unittest.TestCase):        
    def test_basic(self):

        foo_1 = Foo("foo_1", 1)
        foo_2 = Foo("foo_2", 2)
        
        foo_1.cache()
        foo_2.cache()

        assert foo_1.is_cached
        assert foo_2.is_cached

        foo_proxy1 = Foo("foo_1")
        foo_proxy1 = foo_proxy1.load()
        
        foo_proxy2 = Foo("foo_2")
        foo_proxy2.sync()
        
        assert foo_proxy1.value == foo_1.value
        assert foo_proxy2.value == foo_2.value
             
        return
        
    def tearDown(self):
        if os.path.exists('cache-Foo.dat'):
            os.remove('cache-Foo.dat')
     
# if we're running in main, we're testing the module
if __name__ == "__main__":
    print("Running tests...")
    unittest.main()
    