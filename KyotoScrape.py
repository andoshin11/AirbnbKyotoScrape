# -*- coding: utf-8 -*-
"""
Created on Mon Dec 14 2015

@author: Shin Ando
Scraping Airbnb
"""

from __future__ import unicode_literals

import mechanize
import cookielib
from lxml import html
import csv
import cStringIO
import codecs
from random import randint
from time import sleep
from lxml.etree import tostring
import bs4
import json
import urllib2
import requests



# Browser
br = mechanize.Browser()

# Allow cookies
cj = cookielib.LWPCookieJar()
br.set_cookiejar(cj)

# Browser options
br.set_handle_equiv(True)
br.set_handle_gzip(True)
br.set_handle_redirect(True)
br.set_handle_referer(True)
br.set_handle_robots(False)

# Follows refresh 0 but not hangs on refresh > 0
br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
#specify browser to emulate
br.addheaders = [('User-agent',
'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

#######################################
#  Wrapper Functions    ###############
#######################################

def IterateMainPage(location_string, loop_limit):
    MainResults = []

    base_url = 'https://www.airbnb.com/s/'
    page_url = '?page='

    try:
        for n in range(1, loop_limit+1):
            print 'Processing Main Page %s out of %s' % (str(n), str(loop_limit))
            #Implement random time delay for scraping
            sleep(randint(0,2))
            current_url = ''.join([base_url, location_string, page_url, str(n)]) # Generate location-based Main Page URL
            MainResults += ParseMainXML(current_url, n)


    except:
        print 'This URL did not return results: %s ' % current_url

    print 'Done Processing Main Page'
    return MainResults




#######################################
#  Main Page    #######################
#######################################


def ParseMainXML(url, pg):

    n = 1
    ListingDB = []

    try:

        tree = html.fromstring(br.open(url).get_data())
        listings = tree.xpath('//div[@class="listing"]')

        for listing in listings: # generate hash for each listings
            dat = {}
            dat['baseurl'] = url
            dat['Lat'] = listing.attrib.get('data-lat', 'Unknown')
            dat['Long'] = listing.attrib.get('data-lng', 'Unknown')
            dat['Title'] = listing.attrib.get('data-name', 'Unknown')
            dat['ListingID'] = listing.attrib.get('data-id', 'Unknown')
            dat['UserID'] = listing.attrib.get('data-user', 'Unknown')
            dat['Price'] = ''.join(listing.xpath('div//span[@class="h3 text-contrast price-amount"]/text()'))
            dat['PageCounter'] = n
            dat['OverallCounter'] = n * pg
            dat['PageNumber'] = pg

            ShortDesc = listing.xpath('div//div[@class="media"]/div/a') # 物件情報

            if len(ShortDesc) > 0:
                dat['ShortDesc'] = ShortDesc[0].text

            ListingDB.append(dat) # 新しい行として追加
            n += 1

        return ListingDB

    except:
        print 'Error Parsing Page - Skipping: %s' % url
        #if there is an error, just return an empty list
        return ListingDB



#######################################
#  Detail Pages #######################
#######################################

def iterateDetail(mainResults):

    finalResults = []
    counter = 0
    baseURL = 'https://www.airbnb.com/rooms/'

    for listing in mainResults:
        counter += 1
        print 'Processing Listing %s out of %s' % (str(counter), str(len(mainResults)))

        #Construct URL
        currentURL = ''.join([baseURL, str(listing['ListingID'])])

        #Get the tree
        tree = getTree(currentURL)

        #Parse the data out of the tree
        DetailResults = collectDetail(tree, listing['ListingID']) 

        #Collect Data
        newListing = dict(listing.items() + DetailResults.items()) 

        #Append To Final Results
        finalResults.append(newListing) 

    return finalResults


def fixDetail(mainResults, indexList):

    finalResults = mainResults[:]
    baseURL = 'https://www.airbnb.com/rooms/'


    for i in indexList:
        print 'fixing index %s' % str(i)
        listingID = str(finalResults[i]['ListingID'])
        currentURL = ''.join([baseURL, listingID])

        #Get the tree
        tree = getTree(currentURL) # 指定したページから作成したtreeオブジェクトを返す

        #Parse the data out of the tree
        DetailResults = collectDetail(tree, listingID) # データを整形しResultsを返してくれる

        #Collect Data
        newListing = dict(finalResults[i].items() + DetailResults.items())

        #Append To Final Results
        finalResults[i] = newListing

    return finalResults


def getTree(url):

    try:
        tree = html.fromstring(br.open(url).get_data())
        return tree

    except:
        print 'Was not able to fetch data from %s' % url
        return ''


def collectDetail(treeObject, ListingID): # データを整形しResultsとして返す
    Results = {'HostName': 'Not Found',
                     'R_acc' : 'Not Found',
                     'R_comm' : 'Not Found',
                     'R_clean' : 'Not Found',
                     'R_loc': 'Not Found',
                     'R_CI' : 'Not Found',
                     'R_val' : 'Not Found',
                     'R_total' : 'Not Found',
                     'P_Cleaning' : 'Not Found',
                     'P_Deposit' : 'Not Found',
                     'P_Weekly' : 'Not Found',
                     'P_Monthly' : 'Not Found',
                     'Cancellation' : 'Not Found',
                     'S_PropType' : 'Not Found',
                     'S_Accomodates' : 'Not Found',
                     'S_Bedrooms' : 'Not Found',
                     'S_Bathrooms' : 'Not Found',
                     'S_NumBeds' : 'Not Found',
                     'S_RoomType' : 'Not Found',
                     'S_CheckIn' : 'Not Found',
                     'S_Checkout' : 'Not Found',
                     'num_reservation' : 'Not Found',
                     'Earning' : 'Not Found'
                     }

    try:
        #Hamel's Functions
        ###################
        Results['S_PropType'] = ''.join(treeObject.xpath("//a[./span/text()='Property type:']/strong/text()"))
        Results['S_Accomodates'] = ''.join(treeObject.xpath("//div[./span/text()='Accommodates:']/strong/text()"))
        Results['S_Bedrooms'] = ''.join(treeObject.xpath("//div[./span/text()='Bedrooms:']/strong/text()"))
        Results['S_Bathrooms'] = ''.join(treeObject.xpath("//div[./span/text()='Bathrooms:']/strong/text()"))
        Results['S_NumBeds'] = ''.join(treeObject.xpath("//div[./span/text()='Beds:']/strong/text()"))
        Results['S_RoomType'] = ''.join(treeObject.xpath("//div[./span/text()='Room type:']/strong/text()"))
        Results['S_CheckIn'] = ''.join(treeObject.xpath("//div[./span/text()='Check In:']/strong/text()"))
        Results['S_Checkout'] = ''.join(treeObject.xpath("//div[./span/text()='Check Out:']/strong/text()"))

        OR = getStatus(ListingID)
        Results['num_reservation'] = OR['num_reservation']
        Results['Earning'] = OR['Earning']


        ####################
        Results['HostName'] = getHostName(TreeToSoup(treeObject), ListingID)

        #accuracy, communication, cleanliness, location, checkin, value
        Results['R_acc'], Results['R_comm'], Results['R_clean'], Results['R_loc'], \
        Results['R_CI'], Results['R_val'], Results['R_total'] = getStars(TreeToSoup(treeObject), ListingID)

        #price
        Results['P_Cleaning'] = ''.join(treeObject.xpath("//div[./span/text()='Cleaning Fee:']/strong/text()")).lstrip("¥ ")
        Results['P_Deposit'] = ''.join(treeObject.xpath("//div[./span/text()='Security Deposit:']/strong/text()")).lstrip("¥ ")
        Results['P_Weekly'] = ''.join(treeObject.xpath("//div[./span/text()='Weekly discount:']/strong/text()"))
        Results['P_Monthly'] = ''.join(treeObject.xpath("//div[./span/text()='Monthly discount:']/strong/text()"))
        Results['Cancellation'] = ''.join(treeObject.xpath("//div[./span/text()='Cancellation:']/a/strong/text()"))


        return Results

    except:
        #Just Return Initialized Dictionary
        return Results



def TreeToSoup(treeObject):
    source = tostring(treeObject)
    soup = bs4.BeautifulSoup(source)
    return soup

def getHostName(soup, ListingID):
    host_name = 'Not Found'

    try:
        host_name = soup.find("h4", class_="row-space-4").string
        host_name = host_name.split(", ")[1]
        return host_name

    except:
        print 'Unable to parse host name for listing id: %s' % str(ListingID)
        return host_name


def singlestar(index, soup):
    stars = soup.find_all("div", {"class" : "foreground"})[index]
    full_star = stars.find_all("i", {"class" : "icon-star icon icon-beach icon-star-small"})
    half_star=  stars.find_all("i", {"class" : "icon-star-half icon icon-beach icon-star-small"})
    total_star = len(full_star)+len(half_star)*0.5
    return total_star

def largestar(index, soup):
    stars = soup.find_all("div", {"class" : "foreground"})[index]
    full_star = stars.find_all("i", {"class" : "icon-star icon icon-beach icon-star-big"})
    half_star=  stars.find_all("i", {"class" : "icon-star-half icon icon-beach icon-star-big"})
    total_star = len(full_star)+len(half_star)*0.5
    return total_star


def getStars(soup, ListingID):
    accuracy, communication, cleanliness, location, checkin, value, total = ['Not Found'] * 7

    try:
        accuracy = singlestar(2, soup)
        communication = singlestar(3, soup)
        cleanliness = singlestar(4, soup)
        location = singlestar(5,soup)
        checkin = singlestar(6,soup)
        value = singlestar(7,soup)
        total = largestar(1, soup)
        return accuracy, communication, cleanliness, location, checkin, value, total

    except:
        print 'Unable to parse stars listing id: %s' % str(ListingID)
        return accuracy, communication, cleanliness, location, checkin, value


#########################################
#  getStatus ########################
#########################################
def getStatus(ListingID):
    dat = {'num_reservation': 'Not at all', 'Earning': 0}

    listingID = str(ListingID)
    base1 = 'https://www.airbnb.jp/api/v2/calendar_months?key=d306zoyjsyarp7ifhu67rjxn52tv0t20&currency=JPY&locale=ja&listing_id='
    base2 = '%22&month=11'
    base3 = '%22&year=2015'
    base4 = '%22&count=1&_format=with_conditions'
    data_url = ''.join([base1, listingID, base2, base3, base4])
    OR = 0
    num_dates = 0
    num_reservation = 0

    try:
        r = requests.get(url=data_url)
        root = json.loads(r.text)
        months = root['calendar_months']

        for month in months:
            for date in month["days"]:
                if '2015-11-' in date["date"]:
                    num_dates+=1
                    if not date["available"]:
                        num_reservation+=1
                        dat['num_reservation'] = num_reservation
                        dat['Earning'] += date["price"]["local_price"]
        return dat

    except:
        print 'Error in getting OR Data from json for listing iD: %s' % str(ListingID)
        return dat


######################################
#### Save Results ####################

class DictUnicodeWriter(object):

    def __init__(self, f, fieldnames, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.DictWriter(self.queue, fieldnames, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, D):
        self.writer.writerow({k:v.encode("utf-8") if isinstance(v, unicode) else v for k,v in D.items()})
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for D in rows:
            self.writerow(D)

    def writeheader(self):
        self.writer.writeheader()

def writeToCSV(resultDict, outfile):

    colnames = [ 'ListingID', 'Title','UserID','baseurl',  'Price', \
        'HostName','Lat','Long','Cancellation',  \
        'OverallCounter','PageCounter','PageNumber', \
         'P_Cleaning','P_Deposit','P_Monthly','P_Weekly', \
         'R_CI','R_acc','R_clean','R_comm', \
         'R_loc','R_val','R_total', \
         'RespRate','RespTime','num_reservation', \
         'S_Accomodates','S_Bathrooms','S_RoomType','S_Bedrooms', \
         'S_CheckIn','S_Checkout','S_NumBeds','S_PropType','ShortDesc','Earning']

    with open(outfile, 'wb') as f:
        w = DictUnicodeWriter(f, fieldnames=colnames)
        w.writeheader()
        w.writerows(resultDict)

#######################################
#  Testing ############################
#######################################


if __name__ == '__main__':

    #Iterate Through Main Page To Get Results
    MainResults = IterateMainPage('Kyoto--Kyoto-Prefecture', 1)

    #Take The Main Results From Previous Step and Iterate Through Each Listing
    #To add more detail
    DetailResults = iterateDetail(MainResults)

    #Write Out Results To CSV File, using function I defined
    writeToCSV(DetailResults, 'OutputFile.csv')
