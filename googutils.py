import urllib2
import re
import HTMLParser

def downloadDetailPage(link):
    response = urllib2.urlopen(link)
    html = response.read()

    '''with open("markwatch.txt", 'w') as myfile:
        myfile.write(html)'''

    #text = html.decode()
    '''with open("marketwatch.txt", 'r') as myfile:
        text = myfile.read()'''
    return html

def downloadPage(link):
    print "in downloadpage --"
    print link
    response = urllib2.urlopen(link)
    html = response.read()
    text = html.decode()

    with open("goog.txt", 'w') as myfile:
        myfile.write(text)

    '''with open("testfile.txt", 'r') as myfile:
        text = myfile.read()'''
    return text

def getNavigationLinks(text, currentPage):
    m = re.search("<div id=navbar>[\s\S]*?<\/table>", text)
    navbarHtml = m.group(0)

    '''with open("navlinks.txt", 'w') as myfile:
        myfile.write(navbarHtml)'''

    links = re.findall("<a href=\"([\s\S]*?)\">[\s\S]*?<\/div>(\d*)<\/a>", navbarHtml)
    #nextLinks = [( int(id), link) for link, id in links if int(id) > currentPage]
    nextLinks = [(int(id), HTMLParser.HTMLParser().unescape(link)) for link, id in links]
    return nextLinks

def getLinkSet(link, from_page, page_count, max):
    return [{ 'link': re.sub("start=(\\d*)", "start=" + str(i*20), link ), 'currentPage': i, 'failcount' : 0 } 
        for i in xrange(from_page, from_page+page_count+1) if i <= max]
    
def getSymbolData(text):
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
        symbol = safeGetRegEx("href=\"\/finance\?q=\w*:(\w*)&", row, 1)
        name = safeGetRegEx("href=\"\/finance\?q=[\s\S]*?>(.*)<\/a>", row, 1)
        tds = re.findall("<td align=right class=\"[\s\S]*?(.*)[\s]*(?=(<td|$))", row)
        data.append({ 'symbol' : symbol, 'name': name, 'price' : tds[0][0], 'marketcap' : tds[1][0], 
            'peratio' : tds[2][0], 'annrevenue' : tds[3][0], 'netincome' : tds[4][0], 'success': False })

    return data

def safeGetRegEx(pattern, txt, groupNo):
    m = re.search(pattern, txt)
    if m:
        return m.group(groupNo)
    else:
        return ""

def getSalesRevenueData(text):
    m = re.search("<a href=\"#\" data-ref=\"ratio_SalesNet1YrGrowth\">[\s\S]*?<\/tr>", text)
    if m:
        subtext = m.group(0)
        all = re.findall("<td class=\"valueCell\">(?:<span[\s\S]*?>)?(.*?)(?:<\/span>)?<\/td>", subtext)
        return all
    else:
        return []

def getIncomeData(text):
    m = re.search("<a href=\"#\" data-ref=\"ratio_NetIncGrowth,ratio_NetMargin1YrGrowthRate\">[\s\S]*?<\/tr>", text)
    if m:
        subtext = m.group(0)
        all = re.findall("<td class=\"valueCell\">(?:<span[\s\S]*?>)?(.*?)(?:<\/span>)?<\/td>", subtext)
        return all
    else:
        return []

def getEpsData(text):
    m = re.search("<a href=\"#\" data-ref=\"ratio_Eps1YrAnnualGrowth\">[\s\S]*?<\/tr>", text)
    if m:
        subtext = m.group(0)
        all = re.findall("<td class=\"valueCell\">(?:<span[\s\S]*?>)?(.*?)(?:<\/span>)?<\/td>", subtext)
        return all
    else:
        return []

def getSalesRevenuePercents(text):
    m = re.search("<tr class=\"childRow hidden\" id=\"ratio_SalesNet1YrGrowth\">[\s\S]*?<\/tr>", text)
    if m:
        subtext = m.group(0)
        all = re.findall("<td class=\"valueCell \S*\">(.*?)%?<\/td>", subtext)
        return all
    else:
        return []

def getIncomePercentages(text):
    m = re.search("<tr class=\"childRow hidden\" id=\"ratio_NetIncGrowth\">[\s\S]*?<\/tr>", text)

    if m:
        subtext = m.group(0)
        all = re.findall("<td class=\"valueCell \S*\">(.*?)%?<\/td>", subtext)
        return all
    else:
        return []

def getEpsPercentages(text):
    m = re.search("<tr class=\"childRow hidden\" id=\"ratio_Eps1YrAnnualGrowth\">[\s\S]*?<\/tr>", text)

    if m:
        subtext = m.group(0)
        all = re.findall("<td class=\"valueCell \S*\">(.*?)%?<\/td>", subtext)
        return all
    else:
        return []