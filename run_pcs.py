# -*- coding: utf-8 -*-
# Original author of bcloud is LiuLang <gsushzhsosgsu@gmail.com>
# bcloud-cl is a command line bcloud created by Caasiu
# Use of this source code is governed by GPLv3 license that can be found
# in http://www.gnu.org/licenses/gpl-3.0.html

import os
import json
import pcs

def yesno(question, default='n'):
    prompt = '%s (y/[n])' % question
    ans = raw_input(prompt).strip().lower()

    if not ans:
        ans = default

    elif ans == 'y':
        return True

    return False


username = raw_input('please input username:')
auth_data_path = os.path.join(os.path.abspath('.'),username,'auth_data.txt')

if os.path.isfile(auth_data_path):
    with open(auth_data_path, 'r') as f:
        data = json.load(f)
    cookie = data[0]
    tokens = data[1]
    qut='显示用户的信息?'
    if yesno(qut):
        #uk=pcs.get_user_uk(cookie,tokens)
        #info= pcs.get_user_info(tokens,uk)
        #print(info)
        pcs.get_quota(cookie,tokens)

    else:
        qut='显示网盘目录的文件信息吗?'
        if yesno(qut):
            path=raw_input('请输入绝对目录[例如:/我的资源/]:')
            path,pcs_files=pcs.list_dir_all(cookie,tokens,path)
            print(pcs_files)

        else:
            qut='下载文件吗?'
            if yesno(qut):
                path=raw_input('请输入文件绝对路径[例如:/我的资源/1.mp4]:')
                downlink=pcs.stream_download(cookie,tokens,path)
                print(downlink)
            else:
                qut='查找文件吗？'
                if yesno(qut):
                    key = raw_input('请输入需要查找文件的名称[例如:1.mp4]:')
                    s = pcs.search(cookie,tokens,key)
                    if s['list']:
                        print(s['list'])
                    else:
                        print('找不到文件')
                else:
                    qut='获取M3U8文件吗？'
                    if yesno(qut):
                        path = raw_input('请输入文件的绝对路径：')
                        res = pcs.get_streaming_playlist(cookie, path)
                        if res:
                            with open('file.m3u8', 'w') as f:
                                f.write(res)
                            print('m3u8文件创建成功')
                    else:
                        print('Nothing to do.')
else:
    print('Please run the run.py first')
