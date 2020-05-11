import gevent
from gevent.queue import Queue
from gevent import Greenlet
from actor import Actor
from worker import Worker
from googutils import downloadPage, getSymbolData
from repository import SymbolRepo as symbol_repo, PageRepo as page_repo
import traceback

class Manager(Actor):
    
    def __init__(self, boss, index):
        self.index = index
        self.boss = boss
        self.workers = [Worker(self, i) for i in xrange(4)]
        self.symbolTasks = []
        self.symbol_fails = {}
        for worker in self.workers:
            worker.start()
        Actor.__init__(self)

    def receive(self, message):
        if message['type'] == "worker.done":
            self.worker_done(message)
        else:
            self.parse_page(message)
            
        gevent.sleep(0)

    def parse_page(self, message):
        
        payload = message['payload']
        link = payload['link']
        currentPage = payload['currentPage']
        fail_count = payload['failcount']
        page = { 'link' : link, 'page': currentPage, 'success' : False, 'failcount' : fail_count }
        page_repo.upsertPage(currentPage, page)

        try:
            text = downloadPage(link)
            self.symbolTasks = getSymbolData(text)
            
            for sym in self.symbolTasks:
                symbol_repo.upsertSymbol(sym['symbol'], sym)
                
            for idx, worker in enumerate(self.workers):
                self.allocate_task(idx)

            page['success'] = True
            page_repo.upsertPage(currentPage, page)

        except Exception as ex:
            print ex
            print "m%d error " %(self.index)
            traceback.print_exc()
            self.boss.inbox.put({ 'type' : "manager.done", 'index': self.index, 'error' : ex.message, 'payload' : message['payload'] })

        return

    def worker_done(self, message):
        if message['error'] != "":
            print "error, re-adding"
            payload = message['payload']
            symbol = payload['symbol']
            self.symbol_fails[symbol] = self.symbol_fails.get(symbol, 1) + 1
            if self.symbol_fails[symbol] <= 3:
                self.symbolTasks.append(message['payload'])

        idx = message['index']
        assigned = self.allocate_task(idx)
        if not assigned:
            self.boss.inbox.put({ 'type' : "manager.done", 'index': self.index, 'error' : "", 'payload' : message['payload'] })
        
    def allocate_task(self, workerIndex):
        worker = self.workers[workerIndex]
        if(len(self.symbolTasks) > 0):
            worker.inbox.put({ 'payload': self.symbolTasks.pop(), 'type': "work" })
            return True
        return False
    