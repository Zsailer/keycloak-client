from urllib.parse import urljoin
import requests as re
from pprint import pprint
import json
from functools import wraps


# API Port
PORT = 8080
BASE_URL = f"http://localhost:{PORT}"


def reauthorize(method):
    """Refresh the user's auth_state."""
    @wraps(method)
    def inner(self, *args, **kwargs):
        self.authorize_user()
        return method(self, *args, **kwargs)
    return inner


class User(object):
    """KeyCloak user.
    """
    def __init__(self, 
        username, 
        password, 
        realm="master",
        auth_state={}
        ):
        self.realm = realm
        self.username = username
        self.auth_state = auth_state
        self.password = password
        self.token_url = f"auth/realms/{self.realm}/protocol/openid-connect/token"
    
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
            urljoin(BASE_URL, self.token_url),
            headers=headers,
            data=data
        )

        # Raise exception if authorization fails. 
        r.raise_for_status()

        self.auth_state = r.json()

    @reauthorize
    def request(self, url="", verb="get", headers={}, data=None):
        """Build a custom request, print reply, 
        """
        operation = getattr(re, verb)

        # Build URL.
        url = urljoin(BASE_URL, f"auth/admin/realms/{self.realm}/{url}")

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
    """Sign in to Keycloak server using Admin credentials"""
    user = User(username, password)
    user.authorize_user()
    return user
