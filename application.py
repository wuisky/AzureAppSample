#!/usr/bin/env/ python
import os

from azure.identity import AzureDeveloperCliCredential
from azure.identity import DefaultAzureCredential
from azure.mgmt.containerregistry import ContainerRegistryManagementClient
from azure.mgmt.containerregistry.models import GenerateCredentialsParameters
from azure.mgmt.containerregistry.models import Token
from azure.mgmt.containerregistry.models import TokenCredentialsProperties
from datetime import datetime
from datetime import timedelta
from flask import Flask
from flask import jsonify
from flask import request
from flask_cors import CORS
import json
import requests

API_KEY = '614a3e89-aaaa-7778-5ec5-19fe7eca3052'
SERVICE_ID = 'roboticspf'
BASE_URL = 'https://api.demo-remote-license.com/license/v1'

TENANT_ID = 'd40d2357-b9d8-4768-989e-32f22fd23fbd'
SUBSCRIPTION_ID = '70d53066-b459-4c14-b59e-fdee58af1e83'
SCOPE_MAP_ID = ('/subscriptions/70d53066-b459-4c14-b59e-fdee58af1e83/'
                'resourceGroups/rg-az065/providers/'
                'Microsoft.ContainerRegistry/registries/'
                'rp2main/scopeMaps/ReadOnlyScopeMap')
RESOURCE_GROUP_NAME = 'rg-az065'
REGISTRY_NAME = 'rp2main'
REGISTRY = 'rp2main.azurecr.io'

proxies = {
    'http': os.getenv('http_proxy'),
    'https': os.getenv('https_proxy'),
}

app = Flask(__name__, static_folder='.', static_url_path='')
cors = CORS(app, supports_credentials=True, allow_headers='Content-Type')


def payout_token(uuid):

    # credential = AzureDeveloperCliCredential(tenant_id=TENANT_ID)
    credential = DefaultAzureCredential()
    client = ContainerRegistryManagementClient(credential=credential,
                                               subscription_id=SUBSCRIPTION_ID)
    arg_token = Token(
        scope_map_id=SCOPE_MAP_ID,
        status='enabled',
        credentials=TokenCredentialsProperties(),
    )

    token = client.tokens.begin_create(
        RESOURCE_GROUP_NAME,
        REGISTRY_NAME,
        uuid + 'Token',
        token_create_parameters=arg_token
    )

    token.wait(30)
    # Output the token details
    if token.done():
        res = token.result(10)
        token_id = res.id
    else:
        return

    now = datetime.now()
    three_hour_later = now + timedelta(hours=3)

    parameters = GenerateCredentialsParameters(
        token_id=token_id,
        expiry=three_hour_later  # Credential valid for 1 hour
    )
    credential_poller = client.registries.begin_generate_credentials(
        resource_group_name=RESOURCE_GROUP_NAME,
        registry_name=REGISTRY_NAME,
        generate_credentials_parameters=parameters
    )

    credential_result = credential_poller.result()
    return credential_result.passwords[0].value


@app.route('/service', methods=['OPTIONS'])
def option_callback():
    print(f'header\n{request.headers}')
    print(f'arg\n{request.args}')
    return 'Done'


@app.route('/service', methods=['POST'])
def service_callback():
    # print(f'Aparam is {request.headers["Aparam"]}')
    data = json.loads(request.data.decode('utf-8'))
    print(f'data\n{data}')
    r = requests.post(
        BASE_URL + '/validate_license/' + SERVICE_ID,
        # data=json.dumps(license_info),
        data=json.dumps(data),
        headers={
            'Content-Type': 'application/json',
            'Authentication': API_KEY,
        },
        timeout=(10.0, 10.0),
        proxies=proxies,
    )

    response_data = {
        'status': 'fail',
        'message': 'Invalid license'
    }

    if r.status_code == 200:
        uuid = data['li_device_id']
        password = payout_token(uuid)
        if password:
            response_data = {
                'status': 'success',
                'message': 'Data processed successfully',
                'token': uuid + 'Token',
                'password': password,
                'registry': REGISTRY,
                'status_code': r.status_code,
            }

    return jsonify(response_data)


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization,Aparam')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,PUT,POST,DELETE,OPTIONS')
    return response


if __name__ == "__main__":
    app.run(debug=True)
        #, port=443,
        #host='0.0.0.0',
        #use_reloader=False
