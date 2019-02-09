#!/usr/bin/env python
#coding=utf-8

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from config import ACCESS_KEY_ID, ACCESS_SECRET

client = AcsClient(ACCESS_KEY_ID, ACCESS_SECRET, 'default')

request = CommonRequest()
request.set_accept_format('json')
request.set_domain('alidns.aliyuncs.com')
request.set_method('POST')
request.set_protocol_type('https') # https | http
request.set_version('2015-01-09')
request.set_action_name('DescribeDomainRecords')

request.add_query_param('DomainName', 'fisherworks.cn')

response = client.do_action(request)
# python2:  print(response) 
print(str(response))

