import gevent
from gevent.queue import Queue
import sys
from googutils import downloadPage, downloadDetailPage, getNavigationLinks, getSymbolData, getLinkSet
import re
import repository as repo
import urllib2
import HTMLParser

repo.SymbolRepo.writeToCsv()
sys.exit()

link = "http://www.google.com/finance?catid=TRBC%3A57&sort=PE_RATIO&ei=s03UWOm2GorNjAHb-I-YBA&start=40&num=20"
print re.sub("start=(\d*)", "start=" + str(1*20), link)
links = getLinkSet(link, 0, 10, 2)
#print links

sys.exit()
text = downloadPage("http://www.google.com/finance?catid=TRBC%3A57&sort=PE_RATIO&ei=s03UWOm2GorNjAHb-I-YBA&start=40&num=20")
m = re.search("<table id=main[\s\S]*?class=results>([\s\S]*?<\/table>)", text)
mainTableHtml = m.group(1)

m1 = re.search("(<tr>[\s]*?<td align=[\s\S]*?<\/table>)", mainTableHtml)
mainTableRowData = m1.group(1)
rows = re.findall("(<tr>[\s]*?<td align=[\s\S]*?)(?=(<tr>|<\/table>))", mainTableRowData)

data = []
for tuplerow in rows:
    row = tuplerow[0]
    if (row == "</table>"):
        continue
    print row
    print "----------" 
    symbol = re.search("href=\"\/finance\?q=\w*:(\w*)&", row).group(1)
    name = re.search("href=\"\/finance\?q=[\s\S]*?>(.*)<\/a>", row).group(1)
    tds = re.findall("<td align=right class=\"[\s\S]*?(.*)[\s]*(?=(<td|$))", row)
    data.append({ 'symbol' : symbol, 'name': name, 'price' : tds[0][0], 'marketcap' : tds[1][0], 
        'peratio' : tds[2][0], 'annrevenue' : tds[3][0], 'netincome' : tds[4][0], 'success': False })

print data

sys.exit()


sys.exit()

class Actor(gevent.Greenlet):

    def __init__(self):
        self.inbox = Queue()
        Greenlet.__init__(self)

    def receive(self, message):
        """
        Define in your subclass.
        """
        raise NotImplementedError()

    def _run(self):
        self.running = True

        while self.running:
            message = self.inbox.get()
            self.receive(message)

import gevent
from gevent.queue import Queue
from gevent import Greenlet

class Worker(Actor):
    
    def __init__(self, boss, index):
        self.boss = boss
        self.index = index
        Actor.__init__(self)

    def receive(self, message):
        print "w%d %s " %(self.index, message)
        self.boss.inbox.put('done')
        gevent.sleep(0)

class Manager(Actor):
    
    def __init__(self):
        self.workers = [Worker(self, i) for i in xrange(4)]
        for worker in self.workers:
            worker.start()
        Actor.__init__(self)

    def receive(self, message):
        print(message)
        
        for idx, worker in enumerate(self.workers):
            worker.inbox.put('manager telling worker')
        gevent.sleep(0)
 
man = Manager()
man.start()

man.inbox.put('start')
gevent.joinall([man])

