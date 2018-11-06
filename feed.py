# encoding: utf-8
from bs4 import BeautifulSoup
from datetime import datetime
import requests
from lxml import html
import parsedatetime
import locale
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

#locale.setlocale(locale.LC_TIME, "Swedish") # swedish for Windows
locale.setlocale(locale.LC_TIME, "sv_SE") # swedish for linux



stores = {"Mobilextra" : {
            'FyndiqUsername': "papenam",
            'FyndiqPassword': "Gamer55!",
            'Access-Token': "dc135a3f-1e9d-4fb1-8800-40af55b21dc3",
            'Client-Secret': "Gs7SD7Znm6",
            'Kundnummer': "1"},



LOGIN_URL = "https://fyndiq.se/merchant/login/"



def getResult(username, password):
    session = requests.Session()
    result = session.get(LOGIN_URL)

    # GET CSRF TOKEN
    tree = html.fromstring(result.text)
    authenticity_token = list(set(tree.xpath("//input[@name='csrfmiddlewaretoken']/@value")))[0]

    result = session.post(LOGIN_URL, login_data(username, password, authenticity_token),
                          headers=dict(referer="https://fyndiq.se/merchant/login/?next=/merchant/settings/api/"))

    return result

def login_data(username, password, token):
    """Craft the login data."""
    return {'csrfmiddlewaretoken': token,
            'username': username,
            'this_is_the_login_form': "1",
            'password': password,
            'next': "/merchant/settings/api/"}

for store in stores.items():

    #Setup store variables for easier access
    shopname = store[0]
    fyndiqUsername = store[1]["FyndiqUsername"]
    fyndiqPassword = store[1]["FyndiqPassword"]

    result = getResult(fyndiqUsername, fyndiqPassword)
    soup = BeautifulSoup(result.text, "lxml")
    contents = soup.findAll('div', attrs={"class": "content"})
    lastRead = str(contents[4]).split("senast: ")[1].split("\n")[0]
    lastReadDate = datetime.strptime(lastRead, "%d %B %Y %H:%M")
    currentTime = datetime.now()
    difference = currentTime - lastReadDate
    differenceHours = (difference.seconds + difference.days * 86400) / 60/60
    if differenceHours > 24:
        server = smtplib.SMTP('hostweb1.avesoro.se', 25)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login("fyndiqalert@swedishasongroup.se", "mTTX7#vRPA]^")
        fromaddr = 'fyndiqalert@swedishasongroup.se'
        toaddr = "info@swedishasongroup.se"Fy
        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Subject'] = "ALERT - FYNDIQ FEED ERROR"
        body = "Fyndiq feed has not been read for more than 24HRS!! Store: " + shopname
        msg.attach(MIMEText(body, 'plain'))
        text = msg.as_string()
        server.sendmail(fromaddr, toaddr, text)
