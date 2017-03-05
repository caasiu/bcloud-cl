# -*- coding: utf-8 -*-
# Original author of bcloud is LiuLang <gsushzhsosgsu@gmail.com>
# bcloud-cl is a command line bcloud created by Caasiu
# Use of this source code is governed by GPLv3 license that can be found
# in http://www.gnu.org/licenses/gpl-3.0.html


import os
import json
import auth

#初始化参数
cookie={}
tokens={}
username=''
password=''
verifycode=''
codeString=''
pubkey=''
rsakey=''


cookie = auth.get_BAIDUID()
token = auth.get_token(cookie)
tokens['token'] = token
ubi = auth.get_UBI(cookie,tokens)
cookie = auth.add_cookie(cookie,ubi,['UBI','PASSID'])
key_data = auth.get_public_key(cookie,tokens)
pubkey = key_data['pubkey']
rsakey = key_data['key']

username = raw_input('username:')
password = raw_input('password:')
password_enc = auth.RSA_encrypt(pubkey, password)
err_no,query = auth.post_login(cookie,tokens,username,password_enc,rsakey)
if err_no == 0:
    auth_cookie = query
    bdstoken = auth.get_bdstoken(auth_cookie)
    tokens['bdstoken'] = bdstoken
    user_dir = os.path.join(os.path.abspath('.'), username)
    if not os.path.isdir(user_dir):
        os.mkdir(user_dir)
    auth_data_path = os.path.join(user_dir, 'auth_data.txt')
    auth_data = [auth_cookie,tokens]
    with open(auth_data_path, 'w') as f:
        json.dump(auth_data, f)
    print(auth_cookie)
    print(tokens)
elif err_no == 4:
    print('your password is incorrect')
elif err_no == 257:
    vcodetype = query['vcodetype']
    codeString = query['codeString']
    auth.get_signin_vcode(cookie, codeString)
    while True:
        ans = raw_input('refresh vcode? [y/N]: ')
        if ans == 'N' or ans == 'n':
            break
        codeString = auth.refresh_vcode(cookie,tokens,vcodetype)
    verifycode = raw_input('input verifycode here:')
    if verifycode:
        err_no,query = auth.post_login(cookie,tokens,username,password_enc,rsakey,verifycode,codeString)
        if err_no == 0:
            temp_cookie = query
            auth_cookie,bdstoken = auth.get_bdstoken(temp_cookie)
            tokens['bdstoken'] = bdstoken
            user_dir = os.path.join(os.path.abspath('.'), username)
            if not os.path.isdir(user_dir):
                os.mkdir(user_dir)
            auth_data_path = os.path.join(user_dir, 'auth_data.txt')
            auth_data = [auth_cookie,tokens]
            with open(auth_data_path, 'w') as f:
                json.dump(auth_data, f)
            print(auth_cookie)
            print(tokens)
        else:
            print('try again')
    else:
        print('vcode characters must be 4, try again')
elif err_no == -1:
    print('Fail to login unknow error')
else:
    print(err_no)
    print('open the error file to solve the issue')
