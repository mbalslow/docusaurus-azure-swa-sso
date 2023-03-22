import json
import logging
from os import environ
from typing import Dict, List
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import azure.functions as func


def get_access_token() -> str:
    url = f"https://login.microsoftonline.com/{environ['AZURE_CLIENT_TENANT']}/oauth2/v2.0/token"
    payload = urlencode({
        'grant_type': 'client_credentials',
        'client_id': environ['AZURE_CLIENT_ID'],
        'client_secret': environ['AZURE_CLIENT_SECRET'],
        'scope': 'https://graph.microsoft.com/.default',
    }).encode()

    httprequest = Request(
        url,
        data=payload,
        method='POST',
        headers={
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    )

    with urlopen(httprequest) as response:
        responseJson = json.loads(response.read().decode())

    return responseJson['access_token']


def get_user_groups(access_token: str, user_id: str) -> List[Dict]:
    url = f"https://graph.microsoft.com/v1.0/users/{user_id}/memberOf/microsoft.graph.group?$select=id,displayName"

    httprequest = Request(
        url,
        method='GET',
        headers={
            'Accept': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )

    with urlopen(httprequest) as response:
        responseJson = json.loads(response.read().decode())

    return responseJson['value']


def main(req: func.HttpRequest) -> func.HttpResponse:
    req_body = req.get_json()
    logging.info(req_body)

    user_id = req_body['userId']
    logging.info(f'user_id: {user_id}')

    user_details = req_body['userDetails']
    logging.info(f'user_details: {user_details}')

    # Get the access token for the Graph API
    access_token = get_access_token()

    # Get the groups the user is a member of
    groups: List[Dict] = get_user_groups(access_token, req_body['userId'])
    logging.info(roles)

    roles: List[str] = []

    # Add any logic here to determine the roles for the user
    roles += groups
    logging.info(roles)

    response = {
        'roles': roles
    }

    return func.HttpResponse(json.dumps(response))
