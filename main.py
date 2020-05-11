import gevent
from root import Root
import gevent.monkey

gevent.monkey.patch_all()

sectors = [(0, "https://www.google.com/finance?catid=TRBC%3A50&sort=PE_RATIO&ei=wTjZWKvdItXLjAGj-oL4BA&start=0&num=20", "energy"),
(0, "https://www.google.com/finance?catid=TRBC%3A51&sort=PE_RATIO&ei=XjnZWI2VBsTxjAGs77TICA&start=0&num=20", "basic materials"),
(0, "https://www.google.com/finance?catid=TRBC%3A52&sort=PE_RATIO&ei=iDnZWKmkNc2BjAG6koXgDQ&start=0&num=20", "industrials"),
(0, "https://www.google.com/finance?catid=TRBC%3A55&ei=tDnZWJC2CIHj2AblkoG4Ag&start=0&num=20", "financials"),
(0, "https://www.google.com/finance?catid=TRBC%3A56&sort=PE_RATIO&ei=1jnZWNIPxPaMAbqbtcAN&start=0&num=20", "healthcare"),
(0, "", "healthcare"),
] 

root = Root()
root.start()
#root.inbox.put({ 'type': 'work', 'payload': { 'link' : "https://www.google.com/finance?catid=TRBC%3A57&sort=PE_RATIO&ei=s03UWOm2GorNjAHb-I-YBA&start=0&num=20", 'currentPage': 10, 'maxpage': 20 } })
root.inbox.put({ 'type': 'work', 'payload': { 'link' : "https://www.google.com/finance?catid=TRBC%3A58&sort=PE_RATIO&ei=YcHVWLHPCs6S2AbvrKXgDw&start=0&num=20", 'currentPage': 0, 'maxpage': 3 } })
gevent.joinall([root]) 