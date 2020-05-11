from tinydb import TinyDB, Query

SYMBOL_TYPE = 'symbol'
PAGE_TYPE = 'page'
LAST_LINK = 'loglink'
symbolDb = TinyDB('symbols.json')
pageDb = TinyDB('pages.json')
logDb = TinyDB('logging.json')

class SymbolRepo():
    @staticmethod
    def upsertSymbol(key, data):
        existing = SymbolRepo.getSymbol(key)
        if not existing:
            SymbolRepo.insertSymbol(data)
        else:
            SymbolRepo.updateSymbol(key, data)

    @staticmethod
    def insertSymbol(symbolData):
        symbolData['type'] = SYMBOL_TYPE
        symbolDb.insert(symbolData)

    @staticmethod
    def updateSymbol(symbol, data):
        q = Query()
        typeQ = (q.type == SYMBOL_TYPE) & (q.symbol == symbol)
        symbolDb.update(data, typeQ)

    @staticmethod
    def getSymbol(symbol):
        q = Query()
        return symbolDb.search( (q.type == SYMBOL_TYPE) & (q.symbol == symbol) )

    @staticmethod
    def writeToCsv():
        q = Query()
        data = symbolDb.search(q.type == SYMBOL_TYPE)
        with open('symboldata.csv', 'w') as mycsv:

            formatted = "symbol,name,price,peratio,marketcap,annrevenue,netincome,sales12,sales13,sales14,sales15,sales16,"
            formatted = formatted + "spt12,spt13,spt14,spt15,spt16,in12,in13,in14,in15,in16,ipt12,ipt13,ipt14,ipt15,ipt16,"
            formatted = formatted + "eps12,eps13,eps14,eps15,eps16,ept12,ept13,ept14,ept15,ept16\n"
            mycsv.write(formatted)

            for item in data:
                if not item['success']: 
                    continue
                formatted = item['symbol'].replace(",", "")
                formatted = "%s,%s" %(formatted, item['name'].replace(",", ""))
                formatted = "%s,%s" %(formatted, item['price'].replace(",", ""))
                formatted = "%s,%s" %(formatted, item['peratio'].replace(",", ""))
                formatted = "%s,%s" %(formatted, item['marketcap'].replace(",", ""))
                formatted = "%s,%s" %(formatted, item['annrevenue'].replace(",", ""))
                formatted = "%s,%s" %(formatted, item['netincome'].replace(",", ""))
                formatted = "%s,%s" %(formatted, ",".join([i.replace(",", "") for i in item['sales']]))
                formatted = "%s,%s" %(formatted, ",".join([i.replace(",", "") for i in item['salespct']]))
                formatted = "%s,%s" %(formatted, ",".join([i.replace(",", "") for i in item['income']]))
                formatted = "%s,%s" %(formatted, ",".join([i.replace(",", "") for i in item['incomepct']]))
                formatted = "%s,%s" %(formatted, ",".join([i.replace(",", "") for i in item['eps']]))
                formatted = "%s,%s\n" %(formatted, ",".join([i.replace(",", "") for i in item['epspct']]))
                mycsv.write(formatted)

class PageRepo():
    
    @staticmethod
    def getPage(pageNumber):
        q = Query()
        return pageDb.search( (q.type == PAGE_TYPE) & (q.page == pageNumber) )

    @staticmethod
    def upsertPage(key, data):
        existing = PageRepo.getPage(key)
        if not existing:
            PageRepo.insertPage(data)
        else:
            PageRepo.updatePage(key, data)
    
    @staticmethod
    def insertPage(page):
        page['type'] = PAGE_TYPE
        pageDb.insert(page)

    @staticmethod
    def updatePage(key, data):
        data['type'] = PAGE_TYPE
        q = Query()
        typeQ = (q.type == PAGE_TYPE) & (q.page == key)
        pageDb.update(data, typeQ)

class LogRepo():
    @staticmethod
    def upsertLastLink(data):
        existing = LogRepo.getLastLink()
        if not existing:
            LogRepo.insertLastLink(data)
        else:
            LogRepo.updateLastLink(data)

    @staticmethod
    def insertLastLink(data):
        data['type'] = LAST_LINK
        logDb.insert(data)

    @staticmethod
    def updateLastLink(data):
        q = Query()
        typeQ = (q.type == LAST_LINK)
        logDb.update(data, typeQ)

    @staticmethod
    def getLastLink():
        q = Query()
        return logDb.search( (q.type == LAST_LINK))