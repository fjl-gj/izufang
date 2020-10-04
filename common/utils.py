"""
项目常用工具函数
"""
import datetime
import hashlib
import io
from concurrent.futures.thread import ThreadPoolExecutor

import ujson
import os
import random
import uuid
from functools import wraps, partial

import qrcode
import requests
from PIL.Image import Image


def get_ip_address(request):
    """获得请求的IP地址"""
    ip = request.META.get('HTTP_X_FORWARDED_FOR', None)
    return ip or request.META['REMOTE_ADDR']


def to_md5_hex(data):
    """生成MD5摘要"""
    if type(data) != bytes:
        if type(data) == str:
            data = data.encode()
        elif type(data) == io.BytesIO:
            data = data.getvalue()
        else:
            data = bytes(data)
    return hashlib.md5(data).hexdigest()


def gen_mobile_code(length=6):
    """生成指定长度的手机验证码"""
    return ''.join(random.choices('0123456789', k=length))


def gen_captcha_text(length=4):
    """生成指定长度的图片验证码文字"""
    return ''.join(random.choices(
        '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
        k=length)
    )


def make_thumbnail(image_file, path, size, keep=True):
    """生成缩略图"""
    image = Image.open(image_file)
    origin_width, origin_height = image.size
    if keep:
        target_width, target_height = size
        w_rate, h_rate = target_width / origin_width, target_height / origin_height
        rate = w_rate if w_rate < h_rate else h_rate
        width, height = int(origin_width * rate), int(origin_height * rate)
    else:
        width, height = size
    image.thumbnail((width, height))
    image.save(path)


def gen_qrcode(data):
    """生成二维码"""
    image = qrcode.make(data)
    buffer = io.BytesIO()
    image.save(buffer)
    return buffer.getvalue()


def send_sms_by_luosimao(tel, message):
    """发送短信（调用螺丝帽短信网关）"""
    resp = requests.post(
        url='http://sms-api.luosimao.com/v1/send.json',
        auth=('api', 'key-d752503b8db92317a2642771cec1d9b0'),
        data={
            'mobile': tel,
            'message': message
        },
        timeout=10,
        verify=False)
    return ujson.loads(resp.content)


EXECUTOR = ThreadPoolExecutor(max_workers=64)


def run_in_thread_pool(*, callbacks=(), callbacks_kwargs=()):
    """将函数放入线程池执行的装饰器"""

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            future = EXECUTOR.submit(func, *args, **kwargs)
            for index, callback in enumerate(callbacks):
                try:
                    kwargs = callbacks_kwargs[index]
                except IndexError:
                    kwargs = None
                fn = partial(callback, **kwargs) if kwargs else callback
                future.add_done_callback(fn)
            return future

        return wrapper

    return decorator
