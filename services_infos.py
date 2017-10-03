# -*- encoding: utf-8 -*-

import ovh
from tabulate import tabulate
# Python 2 & 3 compatibilty
try:
   input = raw_input
except NameError:
   pass

# Services not available in /service (BETA)
service_types = [ 
    'allDom',
    'cdn/dedicated',
    'cdn/website',
    'cdn/webstorage',
    'cloud/project',
    'cluster/hadoop',
    'dbaas/logs',
    'dbaas/queue',
    'dbaas/timeseries',
    'dedicated/ceph',
    'dedicated/housing',
    'dedicated/nas',
    'dedicated/nasha',
    'dedicated/server',
    'dedicatedCloud',
    'deskaas',
    'freefax',
    'hosting/privateDatabase',
    'hosting/windows',
    'hpcspot',
    'license/cloudLinux',
    'license/cpanel',
    'license/directadmin',
    'license/office',
    'license/plesk',
    'license/sqlserver',
    'license/virtuozzo',
    'license/windows',
    'license/worklight',
    'overTheBox',
    'pack/xdsl',
    'router',
    'saas/csp2',
    'sms',
    'telephony',
    'telephony/spare',
    'veeamCloudConnect',
    'vps',
    'vrack',
    'xdsl',
    'xdsl/spare',
]

# Please double check your ovh.conf (https://github.com/ovh/python-ovh#example-usage)
try:
  client = ovh.Client()
  client.get("/service")
except (ovh.exceptions.InvalidKey,ovh.exceptions.InvalidRegion) as e:
  error = repr(e)
  if "InvalidRegion" in error:
    print("Configuration not found or Invalid Region/Endpoint")
    exit(1)
  elif "Invalid ConsumerKey" in error:
    ck = client.new_consumer_key_request()
    ck.add_rules(ovh.API_READ_ONLY, '/service')
    ck.add_rules(ovh.API_READ_ONLY, '/service/*')
    for t in service_types:
      ck.add_rules(ovh.API_READ_ONLY, '/%s' % t)
      ck.add_rules(ovh.API_READ_ONLY, '/%s/*/serviceInfos' % t)
    validation = ck.request()
    
    print("Please visit %s to authenticate" % validation['validationUrl'])
    input("and press Enter to continue...")
    print("Btw, your 'consumerKey' is '%s'" % validation['consumerKey'])
  elif "InvalidKey" in error:
    print("Check your ovh.conf : %s" % str(e))
    exit(1)
  else:
    print(error)
    exit(1)

services = []
for s in client.get("/service"):
  infos = client.get("/service/%s" % s)
  if infos.get('renew'):
    renew = infos.get('renew').get('mode', '?')
  else:
    renew = infos.get('renew')
  services.append(["/".join(infos['route']['url'].split('/')[1:-1]), infos['resource']['name'], infos['state'], infos['expirationDate'], infos['nextBillingDate'], renew])
for service_type in service_types:
  for service in client.get("/%s" % service_type):
    infos = client.get("/%s/%s/serviceInfos" % (service_type, service))
    services.append([ service_type, service, infos.get('status','?'), infos.get('expiration','N/A'), 'N/A', infos.get('renewalType')])

print(tabulate(services, headers=['Type', 'Id', 'Status', 'Expiration Date', 'Next Billing Date', 'Renew']))
