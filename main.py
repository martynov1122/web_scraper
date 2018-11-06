from Fyndiq import Fyndiq
from PaymentsModel import FyndiqPayments
from Fortnox import Fortnox
from bs4 import BeautifulSoup
from datetime import datetime
import locale


#locale.setlocale(locale.LC_TIME, "Swedish") # swedish for Windows
locale.setlocale(locale.LC_TIME, "sv_SE") # swedish for linux

#Setup stores information in stores variable. Can setup as many stores as you like
stores = {"Mobilextra" : {
            'FyndiqUsername': "username",
            'FyndiqPassword': "password",
            'Access-Token': "token",
            'Client-Secret': "secret",
            'Kundnummer': "1"},}

#We will run the actions for each store.
for store in stores.items():

    #Setup store variables for easier access
    shopname = store[0]
    fyndiqUsername = store[1]["FyndiqUsername"]
    fyndiqPassword = store[1]["FyndiqPassword"]
    fortnoxToken = store[1]["Access-Token"]
    fortnoxSecret = store[1]["Client-Secret"]
    kundnummer = store[1]["Kundnummer"]

    #Get fyndiq coming payments
    result = Fyndiq(fyndiqUsername,fyndiqPassword).getResult()

    #Parse the HTML
    soup = BeautifulSoup(result.text, "lxml")
    payments = soup.find('div', attrs={"class": "grid_5 text"}).findAll("li")
    # Replace unneccesary chars
    payments = [str(payment).replace("<li>", "").replace("</li>", "").replace(" kr", "").replace(",", ".").strip() for
                payment in payments]
    ##Remove today payments as todays total is not final.

    payments.pop(0)

    ##For each payment we create an invoice
    for payment in payments:
        #Format date and amount properly
        date = datetime.strptime(payment.split(":")[0], "%d %B %Y").date()
        start_date = datetime.strptime("29 Oktober 2016", "%d %B %Y").date()
        amount = float(payment.split(":")[1].replace(" ", ""))
        ##Check if this date has already been entered.
        dbPayment = FyndiqPayments.select().where(FyndiqPayments.payment_date == date).where(FyndiqPayments.shopname == shopname).count()
        if (dbPayment == 0) and (date > start_date):
            fortnoxID = Fortnox(fortnoxToken,fortnoxSecret).createInvoice(date.__str__(), amount, shopname, kundnummer)
            dbPayment = FyndiqPayments.create(payment_date=date, amount=amount, final_amount=0,
                                              fortnox_id=fortnoxID,shopname=shopname)
            dbPayment.save()
        else:
            break

    ##Get sent payments and parse
    result = Fyndiq(fyndiqUsername, fyndiqPassword).getResult()
    soup = BeautifulSoup(result.text, "lxml")
    paymentRows = soup.find('table', attrs={"id": "result_list"}).find("tbody").findAll("tr")

    ##Handle each sent payment
    for paymentRow in paymentRows[0:35]:
        ##Only handle payments that are paid
        status = paymentRow.find("td", attrs={"class": "field-state_description"}).getText()
        if not (status == "Betald"):
            continue

        amount = float(paymentRow.find("td", attrs={"class": "field-payment_amount"}).getText().replace(",", "."))
        date = datetime.strptime(paymentRow.find("td", attrs={"class": "field-to_be_paid_at"}).getText(),
                                "%d %B %Y").date()

        dbPayment = FyndiqPayments.select().where(FyndiqPayments.payment_date == date).where(FyndiqPayments.shopname == shopname).where(FyndiqPayments.final_amount == 0)
        if dbPayment.count():
            fortnoxID = Fortnox(fortnoxToken, fortnoxSecret).addInvoicePayment(date.__str__(), amount, dbPayment.get().fortnox_id)
            dbPayment = FyndiqPayments.update(final_amount = amount).where(FyndiqPayments.payment_date == date).where(FyndiqPayments.shopname == shopname).execute()
