import netifaces
import os

import docker
import json
import requests
import yaml

# Define the server URL
url = 'http://rpapp.azurewebsites.net/service'
# url = 'http://0.0.0.0:5555/service'
proxies = {
    'http': os.getenv('http_proxy'),
    'https': os.getenv('https_proxy'),
}
headers = {
        'Content-Type': 'application/json',
        'Aparam': 'YourAparamValue'
}


# Send a POST request
def get_mac_address(interface_name: str):
    # print(f'try to get net interface {interface_name} mac address...')
    addr_info = netifaces.ifaddresses(interface_name)
    if netifaces.AF_LINK in addr_info:
        return addr_info[netifaces.AF_LINK][0]['addr']
    else:
        return None


def call_api(mac_addr: str, license_id: str):
    data = {
        'license_id': license_id,  # load from somewhere
        'product_id': 'product-id',
        # 'li_device_id': mac_addr,
        'li_device_id': 'device-3mac',  # for test
    }
    response = requests.post(url, headers=headers, data=json.dumps(data),
                             timeout=(180.0, 180.0),
                             proxies=proxies)
    res = response.json()
    print(f'POST request response:\n{res}\n')

    if res['status'] != 'success':
        print('server status is not success')
        raise ValueError

    return response


def send_post_request():
    with open('license.yaml', 'r', encoding='utf-8') as yml:
        license = yaml.safe_load(yml)

    try:
        mac_addr = get_mac_address('enp0s31f6')
        response = call_api(mac_addr, license['license_id'])
    except ValueError:
        mac_addr = get_mac_address('wlp0s20f3')
        response = call_api(mac_addr, license['license_id'])

    res = response.json()
    print(f'POST request response:\n{res}\n')

    if res['status_code'] == 200:
        token = res['token']
        password = res['password']
        registry = res['registry']

        client = docker.from_env()
        try:
            # Login to the Docker registry
            response = client.login(username=token,
                                    password=password,
                                    registry=registry)
            print(f'Login successful: {response}')
            image_name = 'rp2main.azurecr.io/rp2_main:latest'  # switch tag name

            # Pull the image
            print(f'Pulling image {image_name}...')
            client.images.pull(image_name)
        except docker.errors.APIError as e:
            print('azure container registry login failed:', e)
    else:
        print('token require fail')


if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    # Send a POST request
    send_post_request()
