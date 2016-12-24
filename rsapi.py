import os
import sys
import requests, json
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from time import sleep
def check_rs_boot():
    """
    Function to check if rancher server is UP or not
    Try 10 times with 5 sec increasing interval
    if cant connect after 10 attempts, then exit out
    :return: Nothing
    """
    success_flag = False
    rsurl = 'http://' + rsip + ':8080/v2-beta/'
    print "INFO : Connecting to Rancher Server"
    s = requests.Session()
    retries = Retry(total=5,
                    backoff_factor=5,
                    status_forcelist=[500, 502, 503, 504])
    s.mount('http://', HTTPAdapter(max_retries=retries))
    resp = s.get(rsurl)
    if resp.status_code == 200:
        print "INFO : Successfully connected to Rancher server. Moving on"
    else:
        raise Exception("ERROR : Step 1 : Failed to connect to Rancher server on URL {}".format(rsurl))




def get_k8s_proj_id():
    """
    Rancher server can randomly change template ID for k8s
    so getting the k8s template ID for this server instance
    :return: template ID of k8s project template
    """
    print "INFO : Sleeping 20 seconds for server to come up"
    sleep(20)
    rsurl = 'http://' + rsip + ':8080/v2-beta/projectTemplates?name=kubernetes'
    resp = requests.get(rsurl)
    if resp.status_code != 200:
        raise Exception("ERROR : Step 2 : Failed to get Rancher k8s template ID on URL {}".format(rsurl))
    return resp.json()['data'][0]['id']


def create_k8s_env():
    """
    call rancher server to create k8s environment
    :return: Env ID of the env created
    """
    rsurl = 'http://' + rsip + ':8080/v2-beta/projects/'
    req_body=''.join(['{"description": "rancher project for kubernetes", "name": "rancherk8s", "projectTemplateId": "',
                      k8spid,
                      '", "allowSystemRole": false,"members": [ ],"virtualMachine": false,"servicesPortRange": null}'])
    resp = requests.post(rsurl,
                         data=req_body,
                         headers={'Accept':'text/plain','Content-Type':'application/json'})
    if not (resp.status_code == 200 or resp.status_code == 201):
        raise Exception("Failed to create k8s project on Rancher server URL {}".format(rsurl))
    return resp.json()['id']

def set_active_host():
    """
    set rancher server as active host to manage VMs and generate token
    :return: Nothing
    """
    rsurl = 'http://' + rsip + ':8080/v2-beta/activesettings/1as!api.host'
    req_body = ''.join(['{"activeValue":null, "id":"1as!api.host", "name":"api.host", "source":null, "value":"http://',
                      rsip,
                     ':8080"}'])
    resp = requests.put(rsurl,
                         data=req_body,
                         headers={'Accept': 'text/plain', 'Content-Type': 'application/json'})
    if not (resp.status_code == 200 or resp.status_code == 201):
        raise Exception("Failed to set active host on Rancher server URL {}".format(rsurl))

def generate_token():
    """
    Request rancher server to generate authorization token
    :return: Nothing
    """
    print "INFO : Sleeping 10 seconds for host to get activated"
    sleep(10)
    rsurl = 'http://' + rsip + ':8080/v2-beta/projects/'+ k8s_envid +'/registrationtokens'
    req_body = '{"description":"new token for rancherk8s", "name":"token_rancherk8s"}'
    resp = requests.post(rsurl,
                        data=req_body,
                        headers={'Accept': 'text/plain', 'Content-Type': 'application/json'})
    if not (resp.status_code == 200 or resp.status_code == 201):
        raise Exception("Failed to generate token on Rancher server URL {}".format(rsurl))


def get_agent_cmd():
    """
    Get docker command for rancher agent from rancher server
    :return: string containing docker command
    """
    sleep(10)
    rsurl = 'http://' + rsip + ':8080/v2-beta/registrationtokens?name=token_rancherk8s'
    resp = requests.get(rsurl)
    if resp.status_code != 200:
        raise Exception("ERROR : Step 2 : Failed to get Agent command from Rancher Server {}".format(rsurl))
    return resp.json()['data'][0]['command']

#
# Checking for Rancher Server IP
# and exiting if IP is not set
#
rsip = '104.197.179.220'
step = 'all'
"""
try:
    rsip = os.environ['RANCHER_SERVER_IP']
    step = os.environ['STEP']
except KeyError:
    print "ERROR : Please set environment variable RANCHER_SERVER_IP"
    sys.exit(1)
"""
print "INFO : Value of RANCHER_SERVER_IP is {} and value of step is {} ".format(rsip, step)
if step == '1' or step == 'all':
    check_rs_boot()
if step == '2' or step == 'all':
    k8spid = get_k8s_proj_id()
    print "INFO : Value of k8s project id is {}".format(k8spid)
if step == '3' or step == 'all':
    k8s_envid = create_k8s_env()
    print "INFO : Value of Env for k8s project is {}".format(k8s_envid)
if step == '4' or step == 'all':
    set_active_host()
if step == '5' or step == 'all':
    generate_token()
if step == '6' or step == 'all':
    agent_cmd = get_agent_cmd()
    print "INFO : Value of agent_cmd is {} ".format(agent_cmd)