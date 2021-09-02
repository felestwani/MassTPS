import requests
import time
import webbrowser
import csv
import pandas
import keyboard
import time
import random

from bs4 import BeautifulSoup

lineEntry = []
tableEntry = []
delay = 0

#Setup for Captcha
browserLocation = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
webbrowser.register('Chrome', None, webbrowser.BackgroundBrowser(browserLocation))

#Check if Captcha
def recaptchaProtection(page):
    checker = BeautifulSoup(page.content, 'html.parser')
    checker.prettify()
    if "Captcha" in checker.text:
        webbrowser.get('Chrome').open_new(builtURL)
        waitForKey()
        page = requests.get(builtURL)

        #Try to prevent rate-limit
        delay = random.randrange(5,10)
        print("Delaying for ", delay)
        time.sleep(delay)

        soup = BeautifulSoup(page.content, 'html.parser')
        soup.prettify()
    elif "Cloudflare" in checker.text:
        print("Rate-limit triggered")
        writeAndClose()
    return

#Write to csv and exit
def writeAndClose():
        df = pandas.DataFrame(tableEntry)
        df.to_csv("Results.csv")
        exit()


#Pause for input, until recaptcha is solved
def waitForKey():
    print("Press 1 after captcha is solved")
    print("Press 2 to kill script")
    a = keyboard.read_key()

    if a == '1':
        print("1 was pressed, continuing")
    elif a == '2':
        print("2 was pressed, exiting")


inputDF = pandas.read_csv("Input.csv")

for index, row in inputDF.iterrows():
    firstName = row['Fname']
    lastName = row['Lname']
    cityName = row['City']
    ageBot = str(row['AgeBot'])
    ageTop = str(row['AgeTop'])

    builtURL = 'https://www.truepeoplesearch.com/results?name='+firstName+'%20'+lastName+'&citystatezip='+cityName+',%20TX&agerange='+ageBot+'-'+ageTop

    page = requests.get(builtURL)
    
    #Try to prevent rate-limit
    delay = random.randrange(5,10)
    print("Delaying for ", delay)
    time.sleep(delay)

    recaptchaProtection(page)
    soup = BeautifulSoup(page.content, 'html.parser')
    soup.prettify()

    searchResults = soup.find_all(class_='card card-body shadow-form card-summary pt-3')

    for searchResult in searchResults:
        detailLink_elem = searchResult.find('a', class_='btn btn-success btn-lg detail-link shadow-form')['href']
        
        #Pull the city name, second value in content-value array
        livesIn_elem = searchResult.find_all(class_="content-value")[1].text.strip()
        
        #If wrong city, don't even pull the page
        if cityName not in livesIn_elem:
            continue

        fullDetailLink_elem = 'https://www.truepeoplesearch.com' + detailLink_elem
        
        #get Page
        detailPage = requests.get(fullDetailLink_elem)
       
        #Try to prevent rate-limit
        delay = random.randrange(5,10)
        print("Delaying for ", delay)
        time.sleep(delay)

        recaptchaProtection(detailPage)
        detailSoup = BeautifulSoup(detailPage.content, 'html.parser')
        detailSoup.prettify()

        detailName = detailSoup.find(class_="h2")

        detailSearchResults = detailSoup.find_all(class_="row pl-sm-2")
        
        #Skip if None, error catching
        if detailSoup.find(class_="h2") is None:
            continue
        if detailSoup.find(class_="content-value", string=lambda text: 'Age') is None:
            continue     
        if detailSoup.find(class_="card card-body shadow-form")['data-fn'] is None:
            continue
        if detailSoup.find(class_="card card-body shadow-form")['data-ln'] is None:
            continue
        if detailSoup.find(class_="card card-body shadow-form")['data-city'] is None:
            continue
        if detailSoup.find(class_="card card-body shadow-form")['data-state'] is None:
            continue
        if detailSoup.find(class_="card card-body shadow-form")['data-age'] is None:
            continue


        detailAgeString = detailSoup.find(class_="content-value", string=lambda text: 'Age')
        
        detailFName = detailSoup.find(class_="card card-body shadow-form")['data-fn']
        detailLName = detailSoup.find(class_="card card-body shadow-form")['data-ln']
        detailCity = detailSoup.find(class_="card card-body shadow-form")['data-city']
        detailState = detailSoup.find(class_="card card-body shadow-form")['data-state']
        detailAge = detailSoup.find(class_="card card-body shadow-form")['data-age']
        
        #Skip if None
        if None in (detailName, detailFName, detailLName, detailCity, detailState, detailAge, detailAgeString):
            continue

        #Eliminate Wrong City/First Name/Last Name
        if (cityName not in detailCity) or (firstName not in detailFName) or (lastName not in detailLName):
            continue

        lineEntry = [detailName.text.strip(), firstName, lastName, detailAge, detailAgeString.text.strip()]

        print(fullDetailLink_elem)
        print(detailName.text.strip())
        #print(detailAgeString.text.strip())
        #print("Phone Numbers:")

        for detailSearchResult in detailSearchResults:
            detailPhoneNumber_elem = detailSearchResult.find('a', class_="link-to-more olnk")
            detailPhoneNumberType_elem = detailSearchResult.find(class_="content-label smaller")
            if None in (detailPhoneNumber_elem, detailPhoneNumberType_elem):
                continue
            if ")" in detailPhoneNumber_elem.text.strip(): 
                temp = detailPhoneNumber_elem.text.strip() + "-" + detailPhoneNumberType_elem.text.strip()
                #print(detailPhoneNumber_elem.text.strip(), "-", detailPhoneNumberType_elem.text.strip())
                lineEntry.append(temp)
        tableEntry.append(lineEntry)
        print()

writeAndClose()

print("Done")