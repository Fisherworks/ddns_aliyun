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
request.set_action_name('UpdateDomainRecord')

request.add_query_param('RecordId', '17091566203664384')
request.add_query_param('RR', 'nest')
request.add_query_param('Type', 'A')
request.add_query_param('Value', '222.129.28.148')

response = client.do_action(request)
print(response) 
# print(str(response, encoding = 'utf-8'))

