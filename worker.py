import gevent
import gevent.monkey
from gevent.queue import Queue
from gevent import Greenlet
from actor import Actor
import googutils as utils 
from repository import SymbolRepo as symbol_repo
import traceback

class Worker(Actor):
    
    def __init__(self, boss, index):
        self.boss = boss
        self.index = index
        gevent.monkey.patch_all()
        Actor.__init__(self)

    def receive(self, message):
        
        print 'worker entry ' + str(self.boss.index) + str(self.index)

        try:
            payload = message['payload']
            symbol = payload['symbol']

            if symbol == "":
                self.boss.inbox.put({ 'type' : "worker.done", 'index': self.index, 'error' : "", 'payload' : message['payload'] })
                gevent.sleep(0)
                return

            link = "http://www.marketwatch.com/investing/stock/%s/financials" %(symbol)

            text = utils.downloadDetailPage(link)
            payload['sales'] = utils.getSalesRevenueData(text)
            payload['salespct'] = utils.getSalesRevenuePercents(text)
            payload['income'] = utils.getIncomeData(text)
            payload['incomepct'] = utils.getIncomePercentages(text)
            payload['eps'] = utils.getEpsData(text)
            payload['epspct'] = utils.getEpsPercentages(text)

            payload['success'] = True
            symbol_repo.updateSymbol(symbol, payload)

            print "w%d %s " %(self.index, payload)
            self.boss.inbox.put({ 'type' : "worker.done", 'index': self.index, 'error' : "", 'payload' : message['payload'] })
        except Exception as ex:
            print ex
            print "w-%d-%d error " %(self.boss.index, self.index)
            traceback.print_exc()
            self.boss.inbox.put({ 'type' : "worker.done", 'index': self.index, 'error' : ex.message, 'payload' : message['payload'] })
        
        gevent.sleep(0)