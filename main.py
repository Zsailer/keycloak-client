from urllib.parse import urljoin
import requests as re
from pprint import pprint
import json

USER = "user1"
PASSWORD = "password"

# API Port
PORT = 8080
BASE_URL = f"http://localhost:{PORT}"
HEADERS = {}


REALM = "master"
TOKEN_URL = f"auth/realms/{REALM}/protocol/openid-connect/token"

class User(object):
    """KeyCloak user.
    """
    def __init__(self, username, password, auth_state):
        self.username = username
        self.auth_state = auth_state
        self.password = password
    
    @property
    def token(self):
        return self.auth_state["access_token"]


    def authorize_user(self):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            "username": self.username,
            "password": self.password,
            "client_id": "admin-cli",
            "grant_type": "password"
        }

        r = re.post(
            urljoin(BASE_URL, TOKEN_URL),
            headers=headers,
            data=data
        )

        # Raise exception if authorization fails. 
        r.raise_for_status()

        self.auth_state = r.json()

    
    def request(self, url="", verb="get", headers={}, data=None):
        """Build a custom request, print reply, 
        """
        operation = getattr(re, verb)

        # Build URL.
        url = urljoin(BASE_URL, f"{url}")

        # Update given headers with authorization token.
        headers.update({"Authorization": f"Bearer {self.token}"})

        # Print URL
        print(f"{verb.upper()} request to:\n{url}\n")

        # Make request
        r = operation(
            url,
            headers=headers,
            data=data
        )

        print(f"Status code: {r.status_code}\n")

        try:
            out = r.json()
            print("JSON Response: ")
            pprint(out)
        except json.JSONDecodeError:
            print("Not valid JSON?\n")
            print(f"Reason: {r.reason}")
        return r



def sign_in(username, password):

    user = User(username, password, {})
    user.authorize_user()

    return user

    # token_url = urljoin(BASE_URL, "auth/realms/master/protocol/openid-connect/token")
    # headers = {
    #     "Content-Type": "application/x-www-form-urlencoded",
    # }
    # data = {
    #     "username": username,
    #     "password": password,
    #     "client_id": "admin-cli",
    #     "grant_type": "password"
    # }

    # r = re.post(
    #     token_url, 
    #     headers=headers,
    #     data=data
    # )

    # return r

# def keycloak_request(url="", verb="get", data=None):
#     """Build a custom request, print reply, 
#     """
#     operation = getattr(re, verb)

#     # Build URL.
#     url = urljoin(BASE_URL, f"auth/{url}")
#     # Print URL
#     print(f"{verb.upper()} request to:\n{url}\n")

#     # Make request
#     r = operation(
#         url, 
#         headers=HEADERS,
#         json=data
#     )

#     print(f"Status code: {r.status_code}\n")

#     try: 
#         out = r.json()
#         print("JSON Response: ")
#         pprint(out)
#     except json.JSONDecodeError:
#         print("Not valid JSON?\n")
#         print(f"Reason: {r.reason}")
#     return r
