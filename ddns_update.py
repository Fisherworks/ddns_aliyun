#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "fisherworks.cn"

import sys
import os, requests, json, logging, logging.handlers
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest


def loggerGenerator(loggerName, fileName=None):
    # Set up a specific logger with our desired output level
    logger = logging.getLogger(loggerName)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(asctime)s] %(message)s')
    handler = logging.handlers.RotatingFileHandler(fileName if fileName else '/tmp/'+loggerName+'.log',
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
    """
    ddns client of Aliyun domain service
    """
    def __init__(self, rr, domain, accKey, accSec, logger=None):
        self.logger = logger if logger else loggerGenerator('ddns_client')
        self.rr = rr
        self.domain = domain
        self.accKey = accKey
        self.accSec = accSec
        self.recordId = ''
        self.ipRecord = self._getCurrentIpRecord()

    def _getNewPublicIp(self):
        """
        WARNING: pls make sure YOU DO HAVE A PUBLIC IP, if you don't know how, visit http://fisherworks.cn/?p=2337

        this method requests your home router public ip (provided by your ISP)
        through some public ip lookup service, such as ifconfig.me (currently slow in China) or httpbin.org
        :return: your public ip, in string
        """
        # url = "http://ifconfig.me/all.json"
        url = "http://httpbin.org/ip"
        try:
            response = requests.request("GET", url, timeout=5)
        except Exception as err:
            self.logger.error('Error - http request error of getLocalPublicIp - {}'.format(err))
            raise RuntimeError(unicode(err))
            # return ''

        if response.status_code != 200:
            self.logger.error('Error - http request error of getLocalPublicIp not 200')
            raise RuntimeError('Error - http request error of getLocalPublicIp not 200')
        # publicIp = response.json().get('ip_addr', '')
        publicIp = response.json().get('origin', '')
        publicIp = publicIp.split(',')
        if not publicIp:
            self.logger.error('Error - new public ip acquiring failed')
            raise RuntimeError('Error - new public ip acquiring failed')
        publicIp = publicIp[0]
        self.logger.info('My public ip acquired - {}'.format(publicIp))
        return publicIp

    def _getCurrentIpRecord(self):
        """
        if you ever set domain record of the RR in this config
        then this method finds and returns the record id and corresponding ip from Aliyun API
        OR if not
        then this method returns blank string
        :return: ip record of this RR.DOMAIN, or blank string
        """
        client = AcsClient(self.accKey, self.accSec, 'default')
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
            self.logger.info('Aliyun ip record NOT FOUND, need to set the new one')
            self.ipRecord = ''
            return self.ipRecord
            # raise RuntimeError('Error - getIpRecord nothing - rr not there?')
        # print record
        self.recordId = record.get('RecordId', '')
        self.ipRecord = record.get('Value', '')
        self.logger.info('Aliyun ip record of {}.{} found - {}'.format(self.rr, self.domain, self.ipRecord))
        return self.ipRecord

    def _addIpRecord(self, rr, newIp):
        """
        if this rr was never been set, now we set it (for the 1st time) with the ip
        :param rr: the rr
        :param newIp: the ip
        :return: response from Aliyun API
        """
        client = AcsClient(self.accKey, self.accSec, 'default')
        request = CommonRequest()
        request.set_accept_format('json')
        request.set_domain('alidns.aliyuncs.com')
        request.set_method('POST')
        request.set_protocol_type('https')  # https | http
        request.set_version('2015-01-09')
        request.set_action_name('AddDomainRecord')

        request.add_query_param('DomainName', self.domain)
        request.add_query_param('RR', rr)
        request.add_query_param('Type', 'A')
        request.add_query_param('Value', newIp)
        try:
            response = client.do_action_with_exception(request)
        except Exception as err:
            self.logger.error('Error - aliyun core sdk error of addIpRecord - {}'.format(err))
            raise RuntimeError(unicode(err))

        self.logger.info('Aliyun ip record set done - {}'.format(response))
        return response

    def _setNewIpRecord(self, recordId, rr, newIp):
        """
        if this rr is already in the Aliyun domain record, now we set that with the new IP
        :param recordId: the record id returned from aliyun
        :param rr: the rr
        :param newIp: the ip
        :return: response from Aliyun API
        """
        client = AcsClient(self.accKey, self.accSec, 'default')
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
            self.logger.error('Error - aliyun core sdk error of setNewIpRecord - {}'.format(err))
            raise RuntimeError(unicode(err))

        self.logger.info('Aliyun ip record set done - {}'.format(response))
        return response

    def updateRecord(self):
        """
        let's do it.
        :return: nothing
        """
        newIp = self._getNewPublicIp()
        if not self.recordId:
            res = self._addIpRecord(self.rr, newIp)
        elif newIp == self.ipRecord:
            self.logger.info('same ip - done exit')
        else:
            res = self._setNewIpRecord(self.recordId, self.rr, newIp)
            self.logger.info('done updated - exit')
        return


if __name__ == "__main__":
    logger = loggerGenerator('ddns_client')
    dirPath = os.path.dirname(os.path.realpath(__file__))
    try:
        with open(os.path.join(dirPath, 'config.json'), 'r') as fp:
            config = json.load(fp)
    except Exception as err:
        logger.error('config file error - {}'.format(err))
        raise IOError('config file error - {}'.format(err))
    # validate the config file
    rr = config.get('RR', '')
    domain = config.get('DOMAIN_NAME', '')
    key = config.get('ACCESS_KEY', '')
    secret = config.get('ACCESS_SECRET', '')
    if not (rr and domain and key and secret):
        logger.error('config file error - RR, DOMAIN_NAME, ACCESS_KEY and ACCESS_SECRET are all required')
        raise KeyError('config file error - RR, DOMAIN_NAME, ACCESS_KEY and ACCESS_SECRET are all required')
    # validate done, do the update
    nc = DdnsClient(rr=rr, domain=domain, accKey=key, accSec=secret, logger=logger)
    nc.updateRecord()
