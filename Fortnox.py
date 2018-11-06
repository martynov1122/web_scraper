import requests
import json
from datetime import datetime, timedelta


class Fortnox():

    def __init__(self, token, secret):
        self.token = token
        self.secret = secret

    def createInvoice(self, date, amount, shopname, customerNumber):
        # Invoices (POST https://api.fortnox.se/3/invoices)

        headers = {
            "Access-Token": self.token,
            "Client-Secret": self.secret,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        try:
            r = requests.post(
                url="https://api.fortnox.se/3/invoices",
                headers=headers,
                data=json.dumps({
                    "Invoice": {
                        "InvoiceRows": [
                            {
                                "DeliveredQuantity": "1",
                                "Description": "Fyndiq Utbetalning " + str(date) + " " + str(shopname),
                                "Price": amount
                            }
                        ],
                        "CustomerNumber": str(customerNumber),
                        "VATIncluded": "true",
                        "YourReference": "Fyndiq Utbet " + str(date) + " " + str(shopname) + " " + str(amount),
                        "InvoiceDate": (
                        datetime.strptime(str(date), "%Y-%m-%d") + timedelta(days=-30)).date().__str__(),
                        "DueDate": str(date),
                    }
                })
            )
            print('Response HTTP Status Code : {status_code}'.format(status_code=r.status_code))
            # print('Response HTTP Response Body : {content}'.format(content=r.content))
            # Load the created invoice number so we can bookeep it.

            if r.status_code != 201:
                return False

            result = json.loads(r.text)
            invoiceID = str(result['Invoice']['DocumentNumber'])

        except requests.exceptions.RequestException as e:
            return False
            print('HTTP Request failed')

        try:
            r = requests.put(
                url="https://api.fortnox.se/3/invoices/" + invoiceID + "/bookkeep",
                headers=headers
            )
            print('Response HTTP Status Code : {status_code}'.format(status_code=r.status_code))
            print('Response HTTP Response Body : {content}'.format(content=r.content))

            if r.status_code == 200:
                return invoiceID

        except requests.exceptions.RequestException as e:
            return False
            ##print('HTTP Request failed')

        return false



    def addInvoicePayment(self, date, amount, invoiceNumber):
        # Invoices (POST https://api.fortnox.se/3/invoicepayments/)

        headers = {
            "Access-Token": self.token,
            "Client-Secret": self.secret,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        try:
            r = requests.post(
                url="https://api.fortnox.se/3/invoicepayments",
                headers=headers,
                data=json.dumps({
                        "InvoicePayment": {
                        "Amount": amount,
                        "PaymentDate": str(date),
                        "InvoiceNumber": invoiceNumber
                        }
                })
            )
            print('Response HTTP Status Code : {status_code}'.format(status_code=r.status_code))
            print('Response HTTP Response Body : {content}'.format(content=r.content))
            # Load the created invoice number so we can bookeep it.

            if r.status_code != 201:
                return False

            result = json.loads(r.text)
            paymentID = str(result['InvoicePayment']['Number'])

        except requests.exceptions.RequestException as e:
            return False
            print('HTTP Request failed')

        try:
            r = requests.put(
                url="https://api.fortnox.se/3/invoicepayments/" + paymentID + "/bookkeep",
                headers=headers
            )
            print('Response HTTP Status Code : {status_code}'.format(status_code=r.status_code))
            print('Response HTTP Response Body : {content}'.format(content=r.content))

            if r.status_code == 200:
                return invoiceNumber

        except requests.exceptions.RequestException as e:
            return False
            ##print('HTTP Request failed')

        return false
