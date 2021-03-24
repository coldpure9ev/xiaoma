import os
import json
import base64
from binascii import hexlify
from Crypto.Cipher import AES
import requests
import traceback


class Encrypyed:
    """传入歌曲的ID，加密生成'params'、'encSecKey 返回"""

    def __init__(self):
        self.pub_key = '010001'
        self.modulus = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
        self.nonce = '0CoJUm6Qyw8W8jud'

    @staticmethod
    def create_secret_key(size):
        return hexlify(os.urandom(size))[:16].decode('utf-8')

    @staticmethod
    def aes_encrypt(text, key):
        iv = b'0102030405060708'
        pad = 16 - len(text) % 16
        text = text + pad * chr(pad)
        encryptor = AES.new(bytes(key.encode('utf-8')), AES.MODE_CBC, iv)
        result = encryptor.encrypt(bytes(text.encode('utf-8')))
        result_str = base64.b64encode(result).decode('utf-8')
        return result_str

    @staticmethod
    def rsa_encrpt(text, pubKey, modulus):
        text = text[::-1]
        rs = pow(int(hexlify(text.encode('utf-8')), 16), int(pubKey, 16), int(modulus, 16))
        return format(rs, 'x').zfill(256)

    def work(self, ids, br=128000):
        text = {'ids': [ids], 'br': br, 'csrf_token': ''}
        text = json.dumps(text)
        i = self.create_secret_key(16)
        encText = self.aes_encrypt(text, self.nonce)
        encText = self.aes_encrypt(encText, i)
        encSecKey = self.rsa_encrpt(i, self.pub_key, self.modulus)
        data = {'params': encText, 'encSecKey': encSecKey}
        return data

    def search(self, text):
        text = json.dumps(text)
        i = self.create_secret_key(16)
        encText = self.aes_encrypt(text, self.nonce)
        encText = self.aes_encrypt(encText, i)
        encSecKey = self.rsa_encrpt(i, self.pub_key, self.modulus)
        data = {'params': encText, 'encSecKey': encSecKey}
        return data

class Search:
    """
    跟歌单直接下载的不同之处
    1.就是headers的referer
    2.加密的text内容不一样！
    3.搜索的URL也是不一样的
    输入搜索内容，可以根据歌曲ID进行下载，大家可以看我根据跟单下载那章，自行组合
    """

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
            'Host': 'music.163.com',
            'Referer': 'http://music.163.com/search/'
        }  # !!注意，搜索跟歌单的不同之处！！
        self.main_url = 'http://music.163.com/'
        self.session = requests.Session()
        self.session.headers = self.headers
        self.ep = Encrypyed()

    def search_song(self, search_content, search_type=1, limit=20):
        """
        根据音乐名搜索
        :params search_content: 音乐名
        :params search_type: 不知
        :params limit: 返回结果数量
        return: 可以得到id 再进去歌曲具体的url
        """
        url = 'http://music.163.com/weapi/cloudsearch/get/web?csrf_token='
        text = {'s': search_content, 'type': search_type, 'offset': 0, 'sub': 'false', 'limit': limit}
        data = self.ep.search(text)
        r = self.session.post(url, data=data, timeout=10)
        ret_data = r.json()
        if ret_data['result']['songCount'] <= 0:
            print('搜不到！！')
            return []
        else:
            songs = ret_data['result']['songs']
            search_list = []
            for song in songs:
                search_list.append({
                    'song_id': song['id'],
                    'title': song['name'],
                    'singer': song['ar'][0]['name'],
                })
            return search_list

def download_music(music_info):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
    }
    song_id = music_info['song_id']
    title = music_info['title']
    singer = music_info['singer']
    file = f'{title}-{singer}.mp3'
    if not os.path.exists(f'./musics/{file}'):
        api = f'https://music.163.com/song/media/outer/url?id={song_id}.mp3'
        print(api)
        try:
            r = requests.get(api, headers=headers, timeout=10)
            print(r.url)
            if '404' in r.url:
                return {'code': -1, 'msg': f'[{title}]为Vip歌曲'}
            with open(f'./musics/{file}', 'wb') as f:
                f.write(r.content)
            return {'code': 1, 'msg': f'[{title}]下载完成'}
        except:
            traceback.print_exc()
            return {'code': -2, 'msg': '网络错误'}
    else:
        return {'code': 2, 'msg': f'[{title}]已存在'}


if __name__ == '__main__':
    # print(Search().search_song('许嵩'))
    print(download_music({'song_id': 1816179968, 'title': '清空（男女合唱完整版）（翻自 王忻辰/苏星婕）', 'singer': '青沨'}))