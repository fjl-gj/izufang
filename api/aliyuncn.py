'''
aliyun-python-sdk-core # 安装阿里云SDK核心库
aliyun-python-sdk-ecs # 安装管理ECS的库
'''


from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest


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
    request.add_query_param('TemplateParam', "{'code':"+f'{message}'+"}")
    response = client.do_action_with_exception(request)
    print(str(response, encoding='utf-8'))