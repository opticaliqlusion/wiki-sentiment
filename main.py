import os
import sys
import argparse
import re
import urllib
import requests
import json
import datetime
import calendar
import hashlib
import io
import pdb

# local resources
import WikiExtractor
import util

# google's sentiment analysis api
from google.cloud import language

# target wikipedia pages
page_ids = {
    "CNN"             : 62028,
    "Fox News"        : 11121,
    "Bill Cosby"      : 158894,
    "Donald Trump"    : 4848272,
    "Hillary Clinton" : 5043192,
    "George W Bush"   : 3414021,
}

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

        
def analyze(html_data):
    """Run a sentiment analysis request on text within a passed filename."""
    language_client = language.Client()

    # Instantiates a plain text document.
    document = language_client.document_from_text(html_data)
    
    # Detects sentiment in the document.
    annotations = document.annotate_text( include_sentiment = True,
                                          include_syntax    = False,
                                          include_entities  = False )

    score = annotations.sentiment.score
    magnitude = annotations.sentiment.magnitude
                                         
    return score, magnitude

    
def go(name, date, cache=False):

    query_fmt = \
        'http://en.wikipedia.org/w/api.php/w/api.php?' \
        'action=query'    \
        '&format=json'    \
        '&prop=revisions' \
        '&list='          \
        '&pageids={}'     \
        '&rvsection=0'    \
        '&rvprop=timestamp%7Ccontent' \
        '&rvstart={:04d}-{:02d}-{:02d}T00%3A00%3A00.000Z'

    # format the query
    timestamp = "{}-{}-{}".format(date.year, date.month, date.day)
    query = query_fmt.format(page_ids[name], date.year, date.month, date.day)
    sentiment_result = SentimentResult(name, page_ids[name], timestamp)

    # check to see if we actually need to perform the lookup
    if cache and sentiment_result.is_cached:
        print("Found result in cache")
        sentiment_result.sync()
        return sentiment_result
    
    # if we don't have it in the cache, perform the query
    data  = json.loads(requests.get(query).text)

    # parse the result with BeautifulSoup
    wiki_markup  = data['query']['pages'][str(page_ids[name])]['revisions'][0]['*']
    
    def format(text):
        lines = text.split('\n')
        return ' '.join([i for i in lines if i][1:-1])

    # extract readable text from the markup
    extractor = WikiExtractor.Extractor(page_ids[name], 0, name, wiki_markup)
    sio = io.StringIO()
    extractor.extract(sio)
    sio.seek(0)
    text = format(sio.read())
    
    # score the result with Google's sentiment analysis
    score, magnitude = analyze(text)
    sentiment_result.score = score
    sentiment_result.magnitude = magnitude
    sentiment_result.length = len(text)
    
    # cache to a file, if necessary
    if cache: sentiment_result.cache()

    return sentiment_result

def main():

    def delta_gen(start, end, deltafunc):
        cur = start
        while cur < end:
            yield cur
            cur = deltafunc(cur)

    start = datetime.date(year=2005, month=1, day=1)
    end = datetime.date.today()

    # lol timedelta still cant do months - wtf?
    delta_day = lambda cur : cur + datetime.timedelta(days=1)
    
    # <joke>
    # i had a problem once and decided to solve it with java
    #   now i have a problem factory
    # </joke>
    def add_months(months):
        def _add_months(cur):
            # https://stackoverflow.com/questions/4130922
            month = cur.month - 1 + months
            year = int(cur.year + month / 12 )
            month = month % 12 + 1
            day = min(cur.day,calendar.monthrange(year,month)[1])
            return datetime.date(year,month,day)
        return _add_months
    
    for key in page_ids.keys():
        for date in delta_gen(start, end, add_months(1)):
            print("analyzing {}".format(date))
            result = go(key, date, cache=True)
            print(result)

    
if __name__ == "__main__":
    main()
