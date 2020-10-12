'''
aliyun-python-sdk-core # 安装阿里云SDK核心库
aliyun-python-sdk-ecs # 安装管理ECS的库
'''

# 阿里云主账号AccessKey拥有所有API的访问权限，风险很高。
# 强烈建议您创建并使用RAM账号进行API访问或日常运维，请登录 https://ram.console.aliyun.com 创建RAM账号。


from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest

import oss2
from itertools import islice
from izufang import app


# 设置存储空间为私有读写权限。
# bucket.create_bucket(oss2.models.BUCKET_ACL_PRIVATE)


class OssFLies:
    __instance = None
    _init = True

    def __new__(cls, *args, **kwargs):
        if cls.__instance == None:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self, bucket=None):
        if OssFLies._init:
            # 创建存储空间
            auth = oss2.Auth('AccessKey ID', 'AccessKey Secret')
            # Endpoint以ESC服务器，。
            self.bucket = oss2.Bucket(auth, 'http://oss-cn-shenzhen.aliyuncs.com', 'fjl-g-mysql')
            OssFLies._init = False

    def upload(self, key, data, *args):
        '''上传图片'''
        # # 创建存储空间
        # auth = oss2.Auth('LTAI4G4dWXk2TQMFiN2UsSo9', 'wlru6tunbXQqvuCd8zZoGoSVjzrM3j')
        # # Endpoint以ESC服务器，。
        # bucket = oss2.Bucket(auth, 'http://oss-cn-shenzhen.aliyuncs.com', 'fjl-g-mysql')
        # 上传文件
        # key上传文件到OSS时需要指定包含文件后缀在内的完整路径，例如abc/efg/123.jpg。
        # filename由本地文件路径加文件名包括后缀组成，例如/users/local/myfile.txt。
        # print(f'izufang/izufang/static/izufang_image/{key}')
        self.bucket.put_object(f'izufang/izufang/static/izufang_image/{key}', data)


def read_file(cata):
    file_img = b''
    for i in cata:
        file_img += bytes(i)
    return file_img


# print(read_file('logo1'))


# def ergodic():
#     '''遍历文件'''
#     # 创建存储空间
#     auth = oss2.Auth('LTAI4G4dWXk2TQMFiN2UsSo9', 'wlru6tunbXQqvuCd8zZoGoSVjzrM3j')
#     # Endpoint以ESC服务器，。
#     bucket = oss2.Bucket(auth, 'http://oss-cn-shenzhen.aliyuncs.com', 'fjl-g-mysql')
#     # oss2.ObjectIteratorr用于遍历文件。
#     for b in islice(oss2.ObjectIterator(bucket), 10):
#         print(b.key)
#
#
# def upload(key, filename):
#     '''上传图片'''
#     # 创建存储空间
#     auth = oss2.Auth('LTAI4G4dWXk2TQMFiN2UsSo9', 'wlru6tunbXQqvuCd8zZoGoSVjzrM3j')
#     # Endpoint以ESC服务器，。
#     bucket = oss2.Bucket(auth, 'http://oss-cn-shenzhen.aliyuncs.com', 'fjl-g-mysql')
#     # 上传文件
#     # key上传文件到OSS时需要指定包含文件后缀在内的完整路径，例如abc/efg/123.jpg。
#     # filename由本地文件路径加文件名包括后缀组成，例如/users/local/myfile.txt。
#     bucket.put_object_from_file(f'izufang/izufang/static/izufang_image/{key}', filename)
#
#
# def download(key, filename):
#     '''下载图片'''
#     # 创建存储空间
#     auth = oss2.Auth('LTAI4G4dWXk2TQMFiN2UsSo9', 'wlru6tunbXQqvuCd8zZoGoSVjzrM3j')
#     # Endpoint以ESC服务器，。
#     bucket = oss2.Bucket(auth, 'http://oss-cn-shenzhen.aliyuncs.com', 'fjl-g-mysql')
#     # <yourObjectName>从OSS下载文件时需要指定包含文件后缀在内的完整路径，例如abc/efg/123.jpg。
#     # <yourLocalFile>由本地文件路径加文件名包括后缀组成，例如/users/local/myfile.txt。
#     bucket.get_object_to_file(f'izufang/izufang/static/izufang_image/{key}',
#                               f'C:/Users\Fjl/Pictures/Camera Roll/oss/{filename}')


@app.task
def send_sms_by_aliyun(tel, message):
    '''发送验证码'''
    client = AcsClient('LTAI4G4dWXk2TQMFiN2UsSo9', 'wlru6tunbXQqvuCd8zZoGoSVjzrM3j', 'cn-shenzhen')

    request = CommonRequest()
    request.set_accept_format('json')
    request.set_domain('dysmsapi.aliyuncs.com')
    request.set_method('POST')
    request.set_protocol_type('https')  # https | http
    request.set_version('2017-05-25')
    request.set_action_name('SendSms')

    request.add_query_param('RegionId', "cn-shenzhen")
    request.add_query_param('PhoneNumbers', f"{tel}")
    request.add_query_param('SignName', "租房网")
    request.add_query_param('TemplateCode', "SMS_204126343")
    request.add_query_param('TemplateParam', "{'code':" + f'{message}' + "}")
    response = client.do_action_with_exception(request)
    return str(response, encoding='utf-8')

# from common.models import HousePhoto
#
#
# path = 'https://fjl-g-mysql.oss-cn-shenzhen.aliyuncs.com/izufang/izufang/static/izufang_image'
#
# photo = HousePhoto()
# photo.path = path
# photo.save()
