#!/usr/bin/env python
#coding=utf-8

import sys
import requests, json, logging, logging.handlers
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from config import ACCESS_KEY_ID, ACCESS_SECRET, RR, DOMAIN_NAME


def loggerGenerator(logger_name, fileName=None):
    # Set up a specific logger with our desired output level
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(asctime)s] %(message)s')
    handler = logging.handlers.RotatingFileHandler(fileName if fileName else '/tmp/'+logger_name+'.log',
                                                   maxBytes=2097152, backupCount=5)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    # set a format which is simpler for console use
    formatter = logging.Formatter('[%(asctime)s] %(message)s')
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logger.addHandler(console)

    return logger


class DdnsClient(object):
    def __init__(self, rr, domain):
        self.logger = loggerGenerator('ddns_client')
        self.rr = rr
        self.domain = domain
        self.recordId = ''
        self.ip = self._getCurrentIpRecord()

    def _getNewPublicIp(self):
        url = "http://ifconfig.me/all.json"
        try:
            response = requests.request("GET", url, timeout=5)
        except Exception as err:
            self.logger.error('Error - http request error of getLocalPublicIp - {}'.format(err))
            raise RuntimeError(unicode(err))
            # return ''

        if response.status_code != 200:
            self.logger.error('Error - http request error of getLocalPublicIp not 200')
            raise RuntimeError('Error - http request error of getLocalPublicIp not 200')
        publicIp = response.json().get('ip_addr', '')
        self.logger.info('public ip acquired - {}'.format(publicIp))
        return publicIp

    def _getCurrentIpRecord(self):
        client = AcsClient(ACCESS_KEY_ID, ACCESS_SECRET, 'default')
        request = CommonRequest()
        request.set_accept_format('json')
        request.set_domain('alidns.aliyuncs.com')
        request.set_method('POST')
        request.set_protocol_type('https')  # https | http
        request.set_version('2015-01-09')
        request.set_action_name('DescribeDomainRecords')
        request.add_query_param('DomainName', self.domain)
        try:
            response = client.do_action_with_exception(request)
            records = json.loads(response).get('DomainRecords', {}).get('Record', [])
        except Exception as err:
            self.logger.error('Error - aliyun core sdk error of getIpRecord - {}'.format(err))
            raise RuntimeError(unicode(err))
        record = next((r for r in records if r.get('RR', '') == self.rr), None)
        if not record:
            self.logger.error('Error - getIpRecord nothing - rr not there?')
            raise RuntimeError('Error - getIpRecord nothing - rr not there?')
        # print record
        self.recordId = record.get('RecordId', '')
        self.ip = record.get('Value', '')
        self.logger.info('ip record found - {}'.format(self.ip))
        return record.get('Value', '')

    def _setNewIpRecord(self, recordId, rr, newIp):
        client = AcsClient(ACCESS_KEY_ID, ACCESS_SECRET, 'default')
        request = CommonRequest()
        request.set_accept_format('json')
        request.set_domain('alidns.aliyuncs.com')
        request.set_method('POST')
        request.set_protocol_type('https')  # https | http
        request.set_version('2015-01-09')
        request.set_action_name('UpdateDomainRecord')

        request.add_query_param('RecordId', recordId)
        request.add_query_param('RR', rr)
        request.add_query_param('Type', 'A')
        request.add_query_param('Value', newIp)
        try:
            response = client.do_action_with_exception(request)
        except Exception as err:
            self.logger.error('Error - aliyun core sdk error of setIpRecord - {}'.format(err))
            raise RuntimeError(unicode(err))

        self.logger.info('public ip set done - {}'.format(response))
        return response

    def updateRecord(self):
        newIp = self._getNewPublicIp()
        if newIp == self.ip:
            self.logger.info('same ip - done exit')
            return
        else:
            if self.recordId and newIp:
                res = self._setNewIpRecord(self.recordId, self.rr, newIp)
                self.logger.info('done updated - exit')
                return


if __name__ == "__main__":
    nc = DdnsClient(RR, DOMAIN_NAME)
    nc.updateRecord()
