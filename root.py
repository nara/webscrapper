import gevent
import gevent.monkey
from actor import Actor
from manager import Manager
from googutils import getLinkSet, downloadPage, getNavigationLinks
from repository import PageRepo as page_repo, LogRepo as log_repo
from operator import itemgetter
import re
import traceback

class Root(Actor):
    
    def __init__(self):
        self.managers = [Manager(self, i) for i in xrange(5)]
        self.page_tasks = []
        self.max_page_processed = 0
        self.success_page_count = 0
        self.no_more_pages = False
        self.base_link = ''
        self.max_page_number = 0

        gevent.monkey.patch_all()

        for manager in self.managers:
            manager.start()

        Actor.__init__(self)

    def receive(self, message):
        if message['type'] == "manager.done":
            self.manager_done(message)
        else:
            self.parse_page(message)
        gevent.sleep(0)

    def parse_page(self, message):
        payload = message['payload']
        self.base_link = payload['link']
        currentPage = payload['currentPage']
        self.max_page_number = payload['maxpage']
        
        self.fetch_tasks(currentPage)
        
        for idx, manager in enumerate(self.managers):
            self.allocate_task(idx)
        return

    def manager_done(self, message):
        
        if message['error'] != "":
            print "error, re-adding"
            payload = message['payload']

            link = page_repo.getPage(payload['currentPage'])[0]
            if link['failcount'] <= 3:
                self.increment_fail_count(link, payload)
                self.page_tasks.append(message['payload'])
            else:
                print "too many failures %s" %(payload['currentPage'])

        idx = message['index']
        self.allocate_task(idx)
    
    def increment_fail_count(self, link, payload):
        link['failcount'] = link['failcount'] + 1
        payload['failcount'] = link['failcount']
        page_repo.upsertPage(payload['currentPage'], link)

    def allocate_task(self, managerIndex):
        manager = self.managers[managerIndex]
        if(len(self.page_tasks) > 0):
            manager.inbox.put({ 'payload': self.page_tasks.pop(), 'type': "work" })
        else:
            if not self.no_more_pages:
                self.fetch_tasks(self.max_page_processed+1)
                if not self.no_more_pages and len(self.page_tasks) > 0:
                    manager.inbox.put({ 'payload': self.page_tasks.pop(), 'type': "work" })
    
    def fetch_tasks(self, page_number):
        
        try:
            links = getLinkSet(self.base_link, page_number, 10, self.max_page_number)
            self.max_page_processed = max(link['currentPage'] for link in links) if len(links) > 0 else self.max_page_number 
            self.no_more_pages = len(links) == 0
            self.page_tasks.extend(links)
            
            if len(links) > 0:
                log_repo.upsertLastLink({ 'link' : links[-1]['link'], 'pageNumber' : links[-1]['currentPage'] })
                
        except Exception as ex:
            print ex
            traceback.print_exc()
            self.no_more_pages = True

