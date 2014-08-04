#!/usr/bin/python3

import requests
import os

try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser

DEBUG = False
if DEBUG:
    import http.client
    http.client.HTTPConnection.debuglevel = 1

SHARETYPE_USER = 0
SHARETYPE_GROUP = 1
SHARETYPE_PUBLIC = 3

PERMISSION_READ = 1
PERMISSION_UPDATE = 2
PERMISSION_CREATE = 4
PERMISSION_DELETE = 8
PERMISSION_SHARE = 16

API_PATH = '/ocs/v1.php/apps/files_sharing/api/v1'
SHARE_PATH = '/public.php?service=files&t='
from sys import platform as _platform
if _platform == "linux" or _platform == "linux2":
    CONFIG_PATH = os.path.expanduser('~/.local/share/data/ownCloud')
elif _platform == "darwin":
    CONFIG_PATH = os.path.expanduser('~/Library/Application Support/ownCloud')

def check_status(jsonfeed):
    if jsonfeed['ocs']['meta']['statuscode'] != 100:
        raise OCShareException(jsonfeed['ocs']['meta'])


def check_request(request):
    if request.status_code != 200:
        request.raise_for_status()
        raise requests.exceptions.HTTPError(
            '%s Client Error: %s' % (request.status_code, request.reason))


def full_path_to_cloud(fullPath):
    paths = []
    for f in os.listdir(CONFIG_PATH+'/folders'):
        config = ConfigParser.ConfigParser()
        config.read('%s/%s' % (CONFIG_PATH+'/folders', f))
        paths.append(config['ownCloud']['localPath'])

    for path in paths:
        if fullPath[:len(path)] == path:
            return fullPath[len(path)-1:]
    return None


class OCShareException(Exception):
    def __init__(self, meta):
        self.status = meta['status']
        self.status_code = meta['statuscode']
        self.message = meta['message']

    def __str__(self):
        return '%d %s' % (self.status_code, self.message)


class OCShareAPI:
    def __init__(self, url, username, password):
        self.username = username
        self.password = password
        self.url = url

    def get_shares(self, path=None, reshares=None, subfiles=None):
        request = requests.get(
            '%s%s/shares' % (self.url, API_PATH),
            auth=(self.username, self.password),
            params={
                'format': 'json',
                'path': path,
                'reshares': reshares,
                'subfiles': subfiles
            }
        )
        check_request(request)
        jsonfeed = request.json()
        check_status(jsonfeed)
        shares = []
        for share in jsonfeed['ocs']['data']:
            shares.append(OCShare(self, **share))
        return shares

    def get_share(self, share):
        return self.getShareById(share.id)

    def get_share_by_id(self, share_id):
        request = requests.get(
            '%s%s/shares/%d' % (self.url, API_PATH, share_id),
            auth=(self.username, self.password),
            params={'format': 'json'}
        )
        check_request(request)
        jsonfeed = request.json()
        check_status(jsonfeed)
        return OCShare(self, **jsonfeed['ocs']['data']['element'])

    def create_share(self, path, shareType, shareWith=None,
                     publicUpload=False, password=None, permissions=None):
        request = requests.post(
            '%s%s/shares' % (self.url, API_PATH),
            allow_redirects=False,
            auth=(self.username, self.password),
            params={'format': 'json'},
            data={
                'path': path,
                'shareType': shareType,
                'shareWith': shareWith,
                'publicUpload': int(publicUpload),
                'password': password,
                'permissions': permissions
            }
        )
        check_request(request)
        jsonfeed = request.json()
        check_status(jsonfeed)
        return self.get_share_by_id(jsonfeed['ocs']['data']['id'])

    def delete_share(self, share):
        return self.delete_share_by_id(share.id)

    def delete_share_by_id(self, share_id):
        request = requests.delete(
            '%s%s/shares/%d' % (self.url, API_PATH, share_id),
            auth=(self.username, self.password),
            params={'format': 'json'}
        )
        check_request(request)
        jsonfeed = request.json()
        check_status(jsonfeed)

    def update_share(self, share, permissions=None,
                     password=None, publicUpload=None):
        return self.updateShareById(
            share.id,
            permissions,
            password,
            publicUpload
        )

    def update_share_by_id(self, share_id, permissions=None,
                           password=None, publicUpload=None):
        request = requests.put(
            '%s%s/shares/%d' % (self.url, API_PATH, share_id),
            auth=(self.username, self.password),
            params={'format': 'json'},
            data={
                'permissions': permissions,
                'password': password,
                'publicUpload': publicUpload
            }
        )
        check_request(request)
        jsonfeed = request.json()
        check_status(jsonfeed)


class OCShare:
    def __init__(self, ocshareapi, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.ocshareapi = ocshareapi
        if self.token:
            self.url = self.ocshareapi.url+SHARE_PATH+self.token
        else:
            self.url = None

    def delete(self):
        self.ocshareapi.delete_share_by_id(self.id)

    def update(self, permissions=None,
               password=None, publicUpload=None):
        self.permissions = permissions
        self.publicUpload = publicUpload
        return self.ocshareapi.update_share_by_id(
            self.id,
            permissions,
            password,
            publicUpload
        )

    def __str__(self):
        return '<OCShare #%d>' % (self.id)

    def __unicode__(self):
        return '<OCShare #%d>' % (self.id)

    def __repr__(self):
        return '<OCShare #%d>' % (self.id)

if __name__ == '__main__':
    import ocsharetools_cli
    ocsharetools_cli.run()
