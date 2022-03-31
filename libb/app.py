import json
import logging
import os
from pymongo import MongoClient
import sys
import platform
import requests
from pathlib import Path

path = os.path.dirname(sys.modules['__main__'].__file__).replace('/libb', '')


class App:
    def __init__(self):
        self.status = 0
        abs_path_config = next(Path(path).rglob('config.json'))
        self.config = self.read_json(abs_path_config)
        self.log_error = logger(name='error', mode='w')
        self.log_debug = logger(name='debug', mode='w')
        my_node = platform.uname().node
        if my_node == 'Z1' or my_node == 'alexei':
            self.bot_name = self.config.get('bot_name')
        else:
            self.bot_name = self.config.get('bot_name')
        if self.config.get('telegram_client'):
            self.app_id = self.config['telegram_client'].get('app_id')
            self.app_hash = self.config['telegram_client'].get('api_hash')
        else:
            self.app_id = None
            self.app_hash = None
        if self.app_id is None or self.app_hash is None:
            self.status = 1
        if 'mongo' in self.config['using_db']:
            mongo_base, enable_ssl, self.status = _detect_base(self)
            self.cluster = MongoClient(mongo_base, tls=enable_ssl, tlsAllowInvalidCertificates=True)
            my_node = platform.uname().node
            if my_node == 'Z1':
                self.db = self.cluster.Funds
            else:
                self.db = self.cluster.CoinsData
            self.collection = self.db.coins
        if 'clickhouse' in self.config['using_db']:
            self.host, self.auth, self.status = _detect_clickhouse_base(self)

    def sms(self, text, lang='en'):
        try:
            token = self.config['telegram']['token']
            url = "https://api.telegram.org/bot"
            channel_id = self.config['telegram']['channel_id']
            url += token
            method = url + "/sendMessage"
            if token == '' and channel_id == '':
                return
            else:
                if lang == 'en':
                    requests.post(method, data={"chat_id": channel_id, "text": text})
                else:
                    text = text.encode("cp1251").decode("utf-8-sig", 'ignore')
                    # text = text.encode('UTF-8').decode('cp1251', 'ignore')
                    requests.post(method, data={"chat_id": channel_id, "text": text})
        except Exception as e:
            print(e, 'error sending a message in telegram')

    def read_json(self, path):
        try:
            with open(path, 'r', encoding='utf-8-sig') as f:
                items = json.load(f)
            return items
        except Exception as e:
            print(e)
            return None

    def write_json_all(self, path, items):
        try:
            with open(path, 'w', encoding='utf-8') as file:
                json.dump(items, file, indent=4, ensure_ascii=False)
        except Exception as e:
            print(e)


def _detect_clickhouse_base(self):
    my_node = platform.uname().node
    auth = None
    if my_node == 'Z1':
        try:
            data = self.read_json(self.config['clickhouse']['click_house_data'])
            host = data['url']
            auth = {'user': data['user'], 'password': data['password']}
            if auth['user'] is None:
                auth = None
            if 'url' not in data or "198." not in data['url']:
                raise Exception
            else:
                print('global base adress has been detected')
        except:
            host = self.config['clickhouse']['local']
            print('my local base will be used')
    else:
        if self.config['clickhouse']['is_local'] is True:
            host = self.config['clickhouse']['local']
        else:
            data = self.read_json(self.config['clickhouse']['click_house_data'])
            host = data['url']
            auth = {'user': data['user'], 'password': data['password']}
            if auth['user'] is None:
                auth = None
            if 'url' not in data or "198." not in data['url']:
                print('base adress incorrect')
                self.status = 1
    return host, auth, self.status


def _detect_base(self):
    enable_ssl = False
    my_node = platform.uname().node
    if my_node == 'Z1':
        try:
            with open(self.config['mongodb']['mongo_base_data'], 'r', encoding='utf-8-sig') as g:
                mongo_base = g.read().strip()
            if "mongodb" not in mongo_base:
                raise Exception
            else:
                print('global base adress has been detected')
        except:
            mongo_base = self.config['mongodb']['mongo_base_my_local']
            print('my local base will be used')
    else:
        if self.config['mongodb']['local_mongodb'] is True:
            mongo_base = self.config['mongodb']['mongo_base_my_local']
            print('my local base will be used')
        else:
            with open(self.config['mongodb']['mongo_base_data'], 'r', encoding='utf-8-sig') as g:
                mongo_base = g.read().strip()
            if "mongodb" not in mongo_base:
                print('base adress incorrect')
                self.status = 1
    if '27017' not in mongo_base:
        enable_ssl = True
    return mongo_base, enable_ssl, self.status


def logger(name, mode='a'):
    log = logging.getLogger(name=name)
    handler = logging.FileHandler(f"{path}/log/{name}.log", mode=mode)
    formatter = logging.Formatter(fmt='[X] %(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    if name == 'error':
        log.setLevel(logging.ERROR)
    else:
        log.setLevel(logging.DEBUG)
    log.addHandler(handler)
    return log
