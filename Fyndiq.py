import requests
from lxml import html


class Fyndiq():


    def __init__(self, username, password):

        self.LOGIN_URL = "https://fyndiq.se/merchant/login/"

        self.username = str(username)
        self.password = str(password)


    def getResult(self):
        session = requests.Session()
        result = session.get(self.LOGIN_URL)

        # GET CSRF TOKEN
        tree = html.fromstring(result.text)
        authenticity_token = list(set(tree.xpath("//input[@name='csrfmiddlewaretoken']/@value")))[0]

        result = session.post(self.LOGIN_URL, self.login_data(authenticity_token),
                              headers=dict(referer="https://fyndiq.se/merchant/login/?next=/merchant/payments/"))

        return result

    def login_data(self, token):
        """Craft the login data."""
        return {'csrfmiddlewaretoken': token,
                'username': self.username,
                'this_is_the_login_form': "1",
                'password': self.password,
                'next': "/merchant/payments/"}
