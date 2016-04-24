# bcloud-cl
![py version](https://img.shields.io/badge/Python-2.7-brightgreen.svg)
![platform](https://img.shields.io/badge/Platform-Linux/UNIX-orange.svg)
![bc version](https://img.shields.io/badge/Version-1.0-yellow.svg)
![license](https://img.shields.io/badge/License-GPLv3-blue.svg)

## About
* bcloud-cl 是基于[LiuLang/bcloud](https://github.com/LiuLang/bcloud)的Python 2版本百度网盘授权和PCS接口
* bcloud-cl 使用[Requests](https://github.com/kennethreitz/requests)库简化网页爬取操作
* bcloud-cl 应该可以在Windows上运行，但需要下载并安装[Python](https://www.python.org/ftp/python/2.7.11/python-2.7.11.msi)
* 需要Python 3版本百度网盘授权和PCS接口的可以参照[bcloud](https://github.com/LiuLang/bcloud/blob/master/README.md)
* 通过命令行来使用百度云盘[houtianze/bypy](https://github.com/houtianze/bypy) (支持Python 2.7+, 3.3+)
* 目的:能在Python 2环境下使用__bcloud__百度网盘接口

## Usage
* Linxu/UNIX:
> :warning: 确保已经安装 Python 2.7

  安装必要的依赖: (Requests,pycrypto)
  ```shell
  $ git clone https://github.com/caasiu/bcloud-cl
  $ pip install requests pycrypto
  ```
  运行 bcloud-cl 获得授权：（只需运行一次）
  ```
  $ cd bcloud-cl
  $ python2.7 run.py
  ```
  调用 PCS接口：
  ```
  $ python2.7 run_pcs.py
  ```

## Document
* [__Requests__](http://docs.python-requests.org/en/master/)
* [__Auth-api__]()
* [__PCS-api__]()
  - :warning: PCS接口只移植了下载，查询，列出全部文件的功能

## License
* Copyright (C) [LiuLang](mailto:gsushzhsosgsu@gmail.com)
* Modified by Caasiu    :envelope: [Email](mailto:Rogers619952467@gmail.com)
* 基于GNU通用许可协议第三版发布, 详细的许可信息请参考 [LICENSE](LICENSE)
