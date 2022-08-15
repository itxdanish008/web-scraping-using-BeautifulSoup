from bs4 import BeautifulSoup
import requests
import smtplib
import time
import datetime
import csv
import pandas as pd
from urllib.request import urlopen
from urllib.error import URLError
from urllib.error import HTTPError


file = pd.read_csv("bookinput.csv")
df = file["ASIN"].iloc[0:5]
HEADER = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0", "Accept-Encoding":"gzip, deflate", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1"}
def getAsins(frame):
    asins = []
    for i in df:
        asins.append(i)
    return asins

def getTitles(asins):
    TITLES = []
    for a in asins:
        titles = file.loc[file["ASIN"] == a, ["Title"]].values
        TITLES.append(titles)
    titles = []
    for t in TITLES:
        for ti in t:
            for tit in ti:
                titles.append(tit)
    return titles

def makingUrlsForAmazon(asins):
    URLS = []
    for i in asins:
        url = f"https://www.amazon.com/dp/{i}/"
        URLS.append(url)
    return URLS

def amazon(URLS,asins):
    usedPricesAmazon = []
    isbns = []
    temp = 0
    for myurl in URLS:
        try:

            pg = requests.get(myurl, headers=HEADER)
            if pg.status_code == 200:
                page = pg.content
                soup = BeautifulSoup(page, "html.parser")

                try:
                    isbn_10 = soup.select_one('span.a-text-bold:contains("ISBN-10"), b :-soup-contains("ISBN-10")').find_parent().text
                    pureIsbn = str(isbn_10.split(':')[-1].strip())
                    isbns.append(pureIsbn.replace("\u200e\n", ""))
                    print(pureIsbn.replace("\u200e\n", ""))

                    try:
                        usedPrice = soup.find(id="usedPrice").get_text()
                        usedpriceprime = usedPrice.replace('$','')
                        usedPricesAmazon.append(usedpriceprime)
                    except:
                        usedPricesAmazon.append('0')

                except:
                    isbns.append(asins[temp])
                    print("page not found")
                    usedPricesAmazon.append('0')

            else:
                print("not working")
                isbns.append(asins[temp])
                usedPricesAmazon.append('0')

            temp = temp +1;

        except HTTPError as e:
            print("error")

        except ConnectionRefusedError:
            print("error")
    newISBN = []
    for i in isbns:
        newisbn = i.strip()
        newISBN.append(newisbn)
    return newISBN, usedPricesAmazon

def makingUrlForBookFinder(isbns):

    bfUrl = []
    for isbn in isbns:
        bf_url = f"https://www.bookfinder.com/search/?author=&title=&lang=en&isbn={isbn}&new_used=&destination=us&currency=USD&mode=basic&st=sr&ac=qr"
        bfUrl.append(bf_url)
    return bfUrl

def getPriceFromBookFinder(bfUrl):
    usedPricesBookFinder = []
    for link in bfUrl:
        try:
            bfPg = requests.get(link, headers=HEADER)
            if bfPg.status_code == 200:
                bfPage = requests.get(link, headers=HEADER).text
                try:
                    soup = BeautifulSoup(bfPage, "html.parser")
                    usedPrice = soup.find(itemprop="lowPrice").get("content")
                    usedPricesBookFinder.append(usedPrice)
                    print(usedPrice)
                except:
                    usedPricesBookFinder.append('0')
                    print("price not found")
            else:
                print("not working")
                usedPricesBookFinder.append('0')
        except HTTPError as e:
            print("error")
        except ConnectionRefusedError:
            print("error")
    return usedPricesBookFinder

def byDefault(asins):
    ppack = []
    shipping = []
    packing = []
    for i in asins:
        ppack.append(9.52)
        shipping.append(1.00)
        packing.append(1.00)

    return ppack,shipping,packing

def referral(amazonUsedPrices):
    ref_15 = []
    for price in amazonUsedPrices:
        fprice = float(price)
        percent_15 = (fprice*15)/100
        ref_15.append(round(percent_15,2))

    return ref_15

def outOfPocket(shipping,packing,bookfinderusedprice,salesTax):
    outpocket = []
    for i in range(0,len(packing)):
        shp = shipping[i]
        pck = packing[i]
        sltx = salesTax[i]
        bfup = bookfinderusedprice[i]

        sumofall = float(shp) + float(pck) + float(bfup) + float(sltx)
        outpocket.append(sumofall)
    return outpocket

def net(usedPricesBookFinder,pickpack,shipping,packaging,usedPricesAmazon,salesTax,refereal):
    mynet = []
    for i in range(0,len(pickpack)):
        upbf = usedPricesBookFinder[i]
        ppack = pickpack[i]
        ship = shipping[i]
        pckg = packaging[i]
        sltx = salesTax[i]
        ref = refereal[i]
        prime = usedPricesAmazon[i]

        all = float(upbf) + float(ppack) + float(pckg) + float(ship) + float(sltx) + float(ref)
        netprice = float(prime) - all
        mynet.append(round(netprice,2))
    return mynet
def ROI(netPrice,outofpocket):
    roi = []
    for i in range(0, len(netPrice)):
        np = netPrice[i]
        ofp = outofpocket[i]
        fnp = float(np)
        fofp = float(ofp)
        op = fnp/fofp
        roundop = round(op,2)
        strop = str(roundop)
        result = strop + "%"
        roi.append(result)
    return roi
def salesTax(usedPricesBookFinder):
    salestax = []
    for i in range (len(usedPricesBookFinder)):
        bfprice = usedPricesBookFinder[i]
        f_bfprice = float(bfprice)
        tax = (8.25 * f_bfprice)/100
        roundtax = round(tax,2)
        strTax = str(roundtax)
        salestax.append(strTax)
    return salestax


asins = getAsins(df)
titles = getTitles(asins)
URLS = makingUrlsForAmazon(asins)
newISBN, usedPricesAmazon = amazon(URLS,asins)

bfUrls = makingUrlForBookFinder(newISBN)


usedPricesBookFinder = getPriceFromBookFinder(bfUrls)

pickpack,shipping,packaging = byDefault(asins)
referal_15 = referral(usedPricesAmazon)
saletax = salesTax(usedPricesBookFinder)
outofpocket = outOfPocket(shipping,packaging,usedPricesBookFinder,saletax)
netPrice = net(usedPricesBookFinder,pickpack,shipping,packaging,usedPricesAmazon,saletax,referal_15)

roi = ROI(netPrice,outofpocket)

newDf = pd.DataFrame({'ISBN' : newISBN,
                      'ASIN' : asins,
                      'Title' : titles,
                      'Used Prices Amazon' : usedPricesAmazon,
                      'Used Prices Bookfinder': usedPricesBookFinder,
                      'Pick pack' : pickpack,
                      'Shipping' : shipping,
                      'Packaging' : packaging,
                      'Referral 15%' : referal_15,
                      'Sales tax 8.25%' : saletax,
                      'Out of Pocket' : outofpocket,
                      'Net' : netPrice,
                      'ROI' : roi},

                     columns=["ISBN","ASIN","Title","Used Prices Amazon","Used Prices Bookfinder",
                              "Pick pack","Shipping","Packaging","Referral 15%","Sales tax 8.25%","Out of Pocket","Net","ROI"])

openfile = open("D:\\programming\\python\\UDP\\web Scraping\\BookInformation.csv","r+",newline="")
openfile.truncate(0)
newDf.to_csv("D:\\programming\\python\\UDP\\web Scraping\\BookInformation.csv", mode="a")
#
print("dataset exported")