# -*- coding: utf-8 -*-
# Original author of bcloud is LiuLang <gsushzhsosgsu@gmail.com>
# bcloud-cl is a command line bcloud created by Caasiu
# Use of this source code is governed by GPLv3 license that can be found
# in http://www.gnu.org/licenses/gpl-3.0.html


try:
    import requests
    from Crypto.PublicKey import RSA
    from Crypto.Cipher import PKCS1_v1_5
except ImportError:
    print('fail to import Requests and Crypto modules')
import time
import json
import base64
import re
import random
import urlparse
import os

#需要的基本信息，例如：网址、时间等
timestamp = str(int(time.time()*1000))
ppui_logintime = str(random.randint(52000, 58535))
PASSPORT_BASE = 'https://passport.baidu.com/'
PASSPORT_URL = PASSPORT_BASE + 'v2/api/'
ACCEPT_HTML = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
REFERER = PASSPORT_BASE + 'v2/?login'
PASSPORT_LOGIN = PASSPORT_BASE + 'v2/api/?login'
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0'
PAN_REFERER = 'http://pan.baidu.com/disk/home'
ACCEPT_JSON = 'application/json, text/javascript, */*; q=0.8'


#相同的headers，不需重复加入
default_headers = {
    'User-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0',
    'Referer': 'http://pan.baidu.com/disk/home',
    'Accept': 'application/json, text/javascript, */*; q=0.8',
    'Accept-language': 'zh-cn, zh;q=0.5',
    'Accept-encoding': 'gzip, deflate',
    'Pragma': 'no-cache',
    'Cache-control': 'no-cache',
}


#将String格式转为Json格式
def json_loads_single(s):
    return json.loads(s.replace("'",'"').replace('\t',''))


#将密码用服务器返回的公匙加密
def RSA_encrypt(public_key, message):
    if not globals().get('RSA'):
        return ''
    rsakey = RSA.importKey(public_key)
    rsakey = PKCS1_v1_5.new(rsakey)
    encrypted = rsakey.encrypt(message.encode('utf-8'))
    return base64.encodestring(encrypted).decode('utf-8').replace('\n', '')


'''
从string中提取关键词keys的值加入到cookie内
cookie是一个dict
'''
def add_cookie(cookie,string,keys):
    str_list = re.split('[,;]\s*', string)
    for key in keys:
        for item in str_list:
            if re.match(key,item):
                s = re.search('=(.+)', item)
                cookie[key] = s.group(1)
    return cookie


#获取 BAIDUID cookie
def get_BAIDUID():
    url = ''.join([
                    PASSPORT_URL,
                    '?getapi&tpl=mn&apiver=v3',
                    '&tt=', timestamp,
                    '&class=login&logintype=basicLogin',
                    ])
    req = requests.get(url, headers={'Referer': ''}, timeout=50)
    if req:
        #获取返回cookie中'Set-Cookie'的值，得到的是一个dict
        cookie = req.cookies.get_dict()
        #手动加入必要的cookie值
        cookie['cflag'] = '65535%3A1'
        cookie['PANWEB'] = '1'
        return cookie
    else:
        return None


#获得 token （此token是还没有经过授权的）
def get_token(cookie):
    url = ''.join([
                    PASSPORT_URL,
                    '?getapi&tpl=mn&apiver=v3',
                    '&tt=', timestamp,
                    '&class=login&logintype=basicLogin',
                    ])

    headers={
            'Accept': ACCEPT_HTML,
            'Cache-control': 'max-age=0',
            }

    headers_merged = default_headers.copy()
    #merge the headers
    for key in headers.keys():
        headers_merged[key] = headers[key]

    req = requests.get(url, headers=headers_merged, cookies=cookie, timeout=50)
    if req:
        hosupport = req.headers['Set-Cookie']
        content_obj = json_loads_single(req.text)
        if content_obj:
            token = content_obj['data']['token']
            return token
    return None


#获取 UBI
def get_UBI(cookie, tokens):
    url = ''.join([

                    PASSPORT_URL,
                    '?loginhistory',
                    '&token=', tokens['token'],
                    '&tpl=pp&apiver=v3',
                    '&tt=', timestamp,
                    ])
    headers={'Referer': REFERER,}

    headers_merged = default_headers.copy()
    #merge the headers
    for key in headers.keys():
        headers_merged[key] = headers[key]

    req=requests.get(url, headers=headers_merged, cookies=cookie, timeout=50)
    if req:
        ubi=req.headers['Set-Cookie']
        return ubi
    return None


#向服务器获取密匙，用于加密用户密码
def get_public_key(cookie, tokens):
    url = ''.join([
                    PASSPORT_BASE,
                    'v2/getpublickey',
                    '?token=', tokens['token'],
                    '&tpl=pp&apiver=v3&tt=', timestamp,

                    ])

    headers={'Referer': REFERER,}

    headers_merged = default_headers.copy()
    #merge the headers
    for key in headers.keys():
        headers_merged[key] = headers[key]

    req = requests.get(url, headers=headers_merged, cookies=cookie, timeout=50)
    if req:
        data = json_loads_single(req.text)
        return data
    return None


#向服务器发送登录请求
'''
    登录验证.
    password   - 使用RSA加密后的base64字符串
    rsakey     - 与public_key相匹配的rsakey
    verifycode - 验证码, 默认为空
    @return (status, info). 其中, status表示返回的状态:
      0 - 正常, 这里, info里面存放的是auth_cookie
     -1 - 未知异常
      4 - 密码错误
    257 - 需要输入验证码, 此时info里面存放着(vcodetype, codeString))
'''
def post_login(cookie, tokens, username, password_enc, rsakey, verifycode='', codeString=''):
    url=PASSPORT_LOGIN
    headers={
            'Accept': ACCEPT_HTML,
            'Referer': REFERER,
            'Connection': 'Keep-Alive',
    }

    headers_merged = default_headers.copy()
    #merge the headers
    for key in headers.keys():
        headers_merged[key] = headers[key]

    data={
        'staticpage':'https%3A%2F%2Fpassport.baidu.com%2Fstatic%2Fpasspc-account%2Fhtml%2Fv3Jump.html',
        'charset':'UTF-8',
        'token':tokens['token'],
        'tpl':'pp',
        'subpro':'',
        'apiver':'v3',
        'tt': timestamp,
        'codestring':codeString,
        'safeflg':'0',
        'u':'http%3A%2F%2Fpassport.baidu.com%2F',
        'isPhone':'',
        'quick_user':'0',
        'logintype':'basicLogin',
        'logLoginType':'pc_loginBasic&idc=',
        'loginmerge':'true',
        'username':username,
        'password':password_enc,
        'verifycode':verifycode,
        'mem_pass':'on',
        'rsakey':rsakey,
        'crypttype':'12',
        'ppui_logintime':ppui_logintime,
        'callback':'parent.bd__pcbs__28g1kg',

        }
    req = requests.post(url, headers=headers_merged, cookies=cookie, data=data, timeout=50)
    content = req.text
    if content:
        match = re.search('"(err_no[^"]+)"', content)
        if not match:
            return (-1, None)
        query = dict(urlparse.parse_qsl(match.group(1)))
        query['err_no'] = int(query['err_no'])
        err_no = query['err_no']
        if err_no == 0 or err_no == 18:
            auth_cookie = req.headers['Set-Cookie']
            keys = ['STOKEN','HOSUPPORT','BDUSS','BAIDUID','USERNAMETYPE','PTOKEN','PASSID','UBI','PANWEB','HISTORY','cflag','SAVEUSERID']
            auth_cookie = add_cookie(cookie,auth_cookie,keys)
            return (0, auth_cookie)
        elif err_no == 257:
            return (err_no, query)
        elif err_no == 400031:
            return (err_no, query)
        else:
            return (err_no, query)
    else:
        return (-1, None)


'''
获取登录时的验证码图片.
codeString - 调用check_login()时返回的codeString.
'''
def get_signin_vcode(cookie, codeString):
        url=''.join([
                        PASSPORT_BASE,
                        'cgi-bin/genimage?',
                        codeString,
                    ])
        headers={'Referer':REFERER,}

        headers_merged = default_headers.copy()
        #merge the headers
        for key in headers.keys():
            headers_merged[key] = headers[key]
        req=requests.get(url, headers=headers_merged, cookies=cookie, timeout=50)
        #vcode_data is bytes
        vcode_data=req.content
        if vcode_data:
            vcode_path = os.path.join(os.path.abspath('.'),'vcode.jpg')
            with open(vcode_path, 'wb') as fh:
                fh.write(vcode_data)
            print('Verifycode is in:'+ vcode_path)
        else:
            print('cannot get verifycode image')
        return None


def get_refresh_codeString(cookie, tokens, vcodetype):
    url=''.join([
        PASSPORT_BASE,
        'v2/?reggetcodestr',
        '&token=', tokens['token'],
        '&tpl=pp&apiver=v3',
        '&tt=', timestamp,
        '&fr=ligin',
        '&vcodetype=', vcodetype,
        ])
    headers={'Referer': REFERER}
    headers_merged = default_headers.copy()
    #merge the headers
    for key in headers.keys():
        headers_merged[key] = headers[key]

    req=requests.get(url, headers=headers_merged, cookies=cookie, timeout=50)
    if req:
        req.encoding = 'gbk'
        return json.loads(req.text)
    return None


def refresh_vcode(cookie, tokens, vcodetype):
    info = get_refresh_codeString(cookie, tokens, vcodetype)
    codeString = info['data']['verifyStr']
    get_signin_vcode(cookie, codeString)
    return codeString


def parse_bdstoken(content):
    '''从页面中解析出bdstoken等信息.

    这些信息都位于页面底部的<script>, 只有在授权后的页面中才出现.
    这里, 为了保证兼容性, 就不再使用cssselect模块解析了.
    @return 返回bdstoken
    '''
    bdstoken = ''
    bds_re = re.compile('"bdstoken"\s*:\s*"([^"]+)"', re.IGNORECASE)
    bds_match = bds_re.search(content)
    if bds_match:
        bdstoken = bds_match.group(1)
        return bdstoken
    else:
        return None


#get baidu accout token
def get_bdstoken(temp_cookie):
    '''从/disk/home页面获取bdstoken等token信息
    这些token对于之后的请求非常重要.
    '''
    url = PAN_REFERER
    headers_merged = default_headers.copy()

    req = requests.get(url, headers=headers_merged, cookies=temp_cookie, timeout=50)
    #将返回的网页用 utf-8 解压
    req.encoding = 'utf-8'
    if req:
        _cookie = req.headers['Set-Cookie']
        key = ['STOKEN','SCRC','PANPSC']
        auth_cookie = add_cookie(temp_cookie, _cookie, key)
        return (auth_cookie, parse_bdstoken(req.text))
    else:
        return None
