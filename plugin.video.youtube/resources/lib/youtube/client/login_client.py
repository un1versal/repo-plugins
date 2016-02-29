__author__ = 'bromix'

import time
import urlparse
import xbmc

from resources.lib.kodion import simple_requests as requests
from resources.lib.youtube.youtube_exceptions import LoginException

# Kodi 17 support and API keys by Uukrul
def log_error(text):
    xbmc.log('YouTube login_client.py - %s' % (text),xbmc.LOGERROR)

class LoginClient(object):
    CONFIGS = {
        'youtube-tv': {
            'system': 'All',
            'key': 'AIzaSyAd-YEOqZz9nXVzGtn3KWzYLbLaajhqIDA',
            'id': '861556708454-d6dlm3lh05idd8npek18k6be8ba3oc68.apps.googleusercontent.com',
            'secret': 'SboVhoG9s0rNafixCSGGKXAT'
        },
        # API KEY for search and channel infos. These should work most of the time without login to safe some quota
        'youtube-for-kodi-quota': {
            'token-allowed': False,
            'system': 'All',
            'key': 'AIzaSyBhQvk9fuc6y_0_vdOJn3g5HiGugplyUwg',
            'id': '1027139679087-8odn2pq90u92qnna7h7j16lp80pabjfq.apps.googleusercontent.com',
            'secret': 'Z750d1Cs4OtBgwlPOBraz-8u'
        },
        'youtube-for-kodi-fallback': {
            'token-allowed': False,
            'system': 'Fallback!',
            'key': 'AIzaSyDXacvXHzPce8UJPK_SJXkvGVS2sjw5ngc',
            'id': '932124282136-1h2fg2a2bfahpkvbg8nk05injmcm60ao.apps.googleusercontent.com',
            'secret': 'Z9ctN0RAzB2w0sWuDFnGiLH2'
        },
        'youtube-for-kodi-12': {
            'system': 'Frodo',
            'key': 'AIzaSyAtSGFXt7PierQaetyz_zawg6SiMQbEoLU',
            'id': '132924520075-4bfjom7ig91dgaum22gnnqs54o0pm3cr.apps.googleusercontent.com',
            'secret': 'UGiB-A2ti-QbrWWeW1ijZaBy'
        },
        'youtube-for-kodi-13': {
            'system': 'Gotham',
            'key': 'AIzaSyCmGt3h1JNxoToALdQTECpK5V5dUQXZh8I',
            'id': '566042245832-qo8a0d9gag422gb2qqneb9k38t1qmi0k.apps.googleusercontent.com',
            'secret': '5PbZ5SXOQmn95V-oRONbVXxO'
        },
        'youtube-for-kodi-14': {
            'system': 'Helix',
            'key': 'AIzaSyDoGc3e7QRlWAn6ukQFoezx3uU2GAynYEI',
            'id': '679912363153-72r33u32en0k2htqqvrdtt1mt4km013d.apps.googleusercontent.com',
            'secret': 'GVWjcVQ4q-wKqcqdCrAvdZhM'
        },
        'youtube-for-kodi-15': {
            'system': 'Isengard',
            'key': 'AIzaSyA5DyO2a9ThpAgQxwVH64Q6MFjgyn5OCdI',
            'id': '939835029889-8ipk31auh8snah3ned7t1eqsqeqags4a.apps.googleusercontent.com',
            'secret': '_9TDAhqdbg-6Fl5_1z1S0ghh'
        },
        'youtube-for-kodi-16': {
            'system': 'Jarvis',
            'key': 'AIzaSyB4Wy7VEoCvtcgReJCzKKAZCP1aZyvjuWo',
            'id': '826708200151-iqi7ovuv4bg3guinsladtd9tq7h08rcb.apps.googleusercontent.com',
            'secret': '78EjmWrQOWfK5GaCxqe4Tx4w'
        },
        'youtube-for-kodi-17': {
            'system': 'Krypton',
            'key': 'AIzaSyCf60r8v8K8isYOt4pfcLfAOgyaiOl2gQM',
            'id': '876361093606-df4dudti2a3j7pksvuvqibr1kmtb7607.apps.googleusercontent.com',
            'secret': 'mJlpCXQUjKwxQ5KLihh7uJBo'
        }
    }

    def __init__(self, config={}, language='en-US', access_token='', access_token_tv=''):
        if not config:
            config = self.CONFIGS['youtube-for-kodi-fallback']
            pass

        self._config = config
        self._config_tv = self.CONFIGS['youtube-tv']

        # the default language is always en_US (like YouTube on the WEB)
        if not language:
            language = 'en_US'
            pass

        language = language.replace('-', '_')
        language_components = language.split('_')
        if len(language_components) != 2:
            language = 'en_US'
            pass

        self._language = language
        self._country = language.split('_')[1]
        self._access_token = access_token
        self._access_token_tv = access_token_tv
        self._log_error_callback = None
        pass

    def set_log_error(self, callback):
        self._log_error_callback = callback
        pass

    def log_error(self, text):
        if self._log_error_callback:
            self._log_error_callback(text)
            pass
        else:
            print text
            pass
        pass

    def revoke(self, refresh_token):
        headers = {'Host': 'www.youtube.com',
                   'Connection': 'keep-alive',
                   'Origin': 'https://www.youtube.com',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.28 Safari/537.36',
                   'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
                   'Accept': '*/*',
                   'DNT': '1',
                   'Referer': 'https://www.youtube.com/tv',
                   'Accept-Encoding': 'gzip, deflate',
                   'Accept-Language': 'en-US,en;q=0.8,de;q=0.6'}

        post_data = {'token': refresh_token}

        # url
        url = 'https://www.youtube.com/o/oauth2/revoke'

        result = requests.post(url, data=post_data, headers=headers, verify=False)
        if result.status_code != requests.codes.ok:
            log_error('revoke')
            raise LoginException('Logout Failed')

        pass

    def refresh_token_tv(self, refresh_token, grant_type=''):
        client_id = self.CONFIGS['youtube-tv']['id']
        client_secret = self.CONFIGS['youtube-tv']['secret']
        return self.refresh_token(refresh_token, client_id=client_id, client_secret=client_secret,
                                  grant_type=grant_type)

    def refresh_token(self, refresh_token, client_id='', client_secret='', grant_type=''):
        headers = {'Host': 'www.youtube.com',
                   'Connection': 'keep-alive',
                   'Origin': 'https://www.youtube.com',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.28 Safari/537.36',
                   'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
                   'Accept': '*/*',
                   'DNT': '1',
                   'Referer': 'https://www.youtube.com/tv',
                   'Accept-Encoding': 'gzip, deflate',
                   'Accept-Language': 'en-US,en;q=0.8,de;q=0.6'}

        _client_id = client_id
        if not client_id:
            _client_id = self._config['id']
            pass
        _client_secret = client_secret
        if not _client_secret:
            _client_secret = self._config['secret']
            pass
        post_data = {'client_id': _client_id,
                     'client_secret': _client_secret,
                     'refresh_token': refresh_token,
                     'grant_type': 'refresh_token'}

        # url
        url = 'https://www.youtube.com/o/oauth2/token'

        result = requests.post(url, data=post_data, headers=headers, verify=False)
        if result.status_code != requests.codes.ok:
            log_error('refresh_token')
            raise LoginException('Login Failed')

        if result.headers.get('content-type', '').startswith('application/json'):
            json_data = result.json()
            access_token = json_data['access_token']
            expires_in = time.time() + int(json_data.get('expires_in', 3600))
            return access_token, expires_in

        return '', ''

    def get_device_token_tv(self, code, client_id='', client_secret='', grant_type=''):
        client_id = self.CONFIGS['youtube-tv']['id']
        client_secret = self.CONFIGS['youtube-tv']['secret']
        return self.get_device_token(code, client_id=client_id, client_secret=client_secret, grant_type=grant_type)

    def get_device_token(self, code, client_id='', client_secret='', grant_type=''):
        headers = {'Host': 'www.youtube.com',
                   'Connection': 'keep-alive',
                   'Origin': 'https://www.youtube.com',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.28 Safari/537.36',
                   'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
                   'Accept': '*/*',
                   'DNT': '1',
                   'Referer': 'https://www.youtube.com/tv',
                   'Accept-Encoding': 'gzip, deflate',
                   'Accept-Language': 'en-US,en;q=0.8,de;q=0.6'}

        _client_id = client_id
        if not client_id:
            _client_id = self._config['id']
            pass
        _client_secret = client_secret
        if not _client_secret:
            _client_secret = self._config['secret']
            pass
        post_data = {'client_id': _client_id,
                     'client_secret': _client_secret,
                     'code': code,
                     'grant_type': 'http://oauth.net/grant_type/device/1.0'}

        # url
        url = 'https://www.youtube.com/o/oauth2/token'

        result = requests.post(url, data=post_data, headers=headers, verify=False)
        if result.status_code != requests.codes.ok:
            log_error('get_device_token')
            raise LoginException('Login Failed')

        if result.headers.get('content-type', '').startswith('application/json'):
            return result.json()

        return None

    def generate_user_code_tv(self):
        client_id = self.CONFIGS['youtube-tv']['id']
        return self.generate_user_code(client_id=client_id)

    def generate_user_code(self, client_id=''):
        headers = {'Host': 'www.youtube.com',
                   'Connection': 'keep-alive',
                   'Origin': 'https://www.youtube.com',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.28 Safari/537.36',
                   'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
                   'Accept': '*/*',
                   'DNT': '1',
                   'Referer': 'https://www.youtube.com/tv',
                   'Accept-Encoding': 'gzip, deflate',
                   'Accept-Language': 'en-US,en;q=0.8,de;q=0.6'}

        _client_id = client_id
        if not client_id:
            _client_id = self._config['id']
        post_data = {'client_id': _client_id,
                     'scope': 'https://www.googleapis.com/auth/youtube'}
        # 'scope': 'http://gdata.youtube.com https://www.googleapis.com/auth/youtube-paid-content'}

        # url
        url = 'https://www.youtube.com/o/oauth2/device/code'

        result = requests.post(url, data=post_data, headers=headers, verify=False)
        if result.status_code != requests.codes.ok:
            log_error(result.text)
            raise LoginException('Login Failed')

        if result.headers.get('content-type', '').startswith('application/json'):
            return result.json()

        return None

    def get_access_token(self):
        return self._access_token

    def authenticate(self, username, password):
        headers = {'device': '38c6ee9a82b8b10a',
                   'app': 'com.google.android.youtube',
                   'User-Agent': 'GoogleAuth/1.4 (GT-I9100 KTU84Q)',
                   'content-type': 'application/x-www-form-urlencoded',
                   'Host': 'android.clients.google.com',
                   'Connection': 'Keep-Alive',
                   'Accept-Encoding': 'gzip'}

        post_data = {'device_country': self._country.lower(),
                     'operatorCountry': self._country.lower(),
                     'lang': self._language.replace('-', '_'),
                     'sdk_version': '19',
                     # 'google_play_services_version': '6188034',
                     'accountType': 'HOSTED_OR_GOOGLE',
                     'Email': username.encode('utf-8'),
                     'service': 'oauth2:https://www.googleapis.com/auth/youtube https://www.googleapis.com/auth/youtube.force-ssl https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/emeraldsea.mobileapps.doritos.cookie https://www.googleapis.com/auth/plus.stream.read https://www.googleapis.com/auth/plus.stream.write https://www.googleapis.com/auth/plus.pages.manage https://www.googleapis.com/auth/identity.plus.page.impersonation',
                     'source': 'android',
                     'androidId': '38c6ee9a82b8b10a',
                     'app': 'com.google.android.youtube',
                     # 'client_sig': '24bb24c05e47e0aefa68a58a766179d9b613a600',
                     'callerPkg': 'com.google.android.youtube',
                     # 'callerSig': '24bb24c05e47e0aefa68a58a766179d9b613a600',
                     'Passwd': password.encode('utf-8')}

        # url
        url = 'https://android.clients.google.com/auth'

        result = requests.post(url, data=post_data, headers=headers, verify=False)
        if result.status_code != requests.codes.ok:
            log_error('authenticate')
            raise LoginException('Login Failed')

        lines = result.text.replace('\n', '&')
        params = dict(urlparse.parse_qsl(lines))
        token = params.get('Auth', '')
        expires = int(params.get('Expiry', -1))
        if not token or expires == -1:
            raise LoginException('Failed to get token')

        return token, expires

    pass
