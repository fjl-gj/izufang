import os
import uuid
from datetime import datetime, timedelta

import jwt
import ujson
# Create your views here.
from django.core.cache import caches
from django.db.models import Prefetch, Q
from django.db.transaction import atomic
from django.http import HttpRequest, HttpResponse

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from django_redis import get_redis_connection
from django.utils import timezone

from rest_framework.decorators import api_view, action
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.aliyuncn import send_sms_by_aliyun, OssFLies, read_file
from api.consts import USER_LOGIN_SUCCESS, USER_LOGIN_FAILED, INVALID_LOGIN_INFO, NULL_LOGIN_INFO, CODE_TOO_FREQUENCY, \
    MOBILE_CODE_SUCCESS, INVALID_TEL_NUM, FILE_UPLOAD_SUCCESS

from api.helpers import EstateFilterSet, HouseInfoFilterSet, DefaultResponse
from api.serializers import DistrictSimpleSerializer, DistrictDetailSerializer, AgentCreateSerializer, \
    AgentDetailSerializer, AgentSimpleSerializer, HouseTypeSerializer, TagListSerializer, EstateCreateSerializer, \
    EstateDetailSerializer, EstateSimpleSerializer, HouseInfoDetailSerializer, HousePhotoSerializer, \
    HouseInfoCreateSerializer, HouseInfoSimpleSerializer, UserCreateSerializer, UserUpdateSerializer, \
    UserSimpleSerializer

from common.captcha import Captcha
from common.models import District, Agent, Estate, HouseType, Tag, HouseInfo, HousePhoto, User, LoginLog
from common.utils import to_md5_hex, gen_captcha_text, get_ip_address, check_tel, gen_mobile_code

from izufang.settings import SECRET_KEY


# FBV
# 声明式缓存


@cache_page(timeout=31536000, cache='default', key_prefix='api')
@api_view(('GET',))
def get_province(request: HttpRequest) -> HttpResponse:
    '''获取省级城市信息'''
    queryset = District.objects.filter(parent__isnull=True).only('name')
    serializers = DistrictSimpleSerializer(queryset, many=True)
    return Response({
        'code': 1000,
        'message': '获取省级成功',
        'results': serializers.data,
    })


# # 编程式缓存1
# @api_view(('GET',))
# def get_cityside(HttpRequest, dist) :
#     '''
#     获取省级对应城市区信息
#     :param request: 获取得请求信息
#     :param dist: 获取得请求信息包含的字段内容
#     :return: 返回响应数据Response
#     '''
#     # 拿取django中的缓存进行查询
#     queryset = caches['default'].get(f'dist:{dist}')
#     # 如果空则查询加缓存
#     if not queryset:
#         queryset = District.objects.filter(distid=dist).defer('parent').first()
#         caches['default'].set(f'dist:{dist}', queryset)
#     serializers = DistrictComplexSerializer(queryset)
#     return Response(serializers.data)


# 编程式缓存2
@api_view(('GET',))
def get_district(HttpRequest, distid):
    '''
    获取省级对应城市区信息
    :param request: 获取得请求信息
    :param dist: 获取得请求信息包含的字段内容
    :return: 返回响应数据Response
    '''
    # 直接拿取django中的缓存的原生客户端进行查询
    redis_cli = get_redis_connection()
    # 如果空则查询加缓存
    data = redis_cli.get(f'izufang:district:{distid}')
    if data:
        data = ujson.loads(data)
    else:
        district = District.objects.filter(distid=distid).defer('parent').first()
        data = DistrictDetailSerializer(district).data
        redis_cli.set(f'izufang:district:{distid}', ujson.dumps(data), ex=900)
    return Response(data)


@method_decorator(decorator=cache_page(timeout=86400), name='get')
class HotCityView(ListAPIView):
    """热门城市视图
    get:
        获取热门城市
    """
    queryset = District.objects.filter(ishot=True).only('name')
    serializer_class = DistrictSimpleSerializer
    pagination_class = None


# FBV
# 增：有  删：有（暂时不给） 改：（有） 查：（有）
# RetrieveUpdate查看单条与更新
# queryset = Agent.objects.all().only('name', 'tel', 'servstar')
# serializer_class = AgentSimpleSerializer
# 首先查看单个经理人的 想要看全部字段包括负责楼盘这里的的楼盘名称
# 查看多个经理人 看经理人id和姓名以及星级即可
# 新增经理人，显示全部字段
# 更新经理人，只能更新部分字段
@method_decorator(decorator=cache_page(timeout=120), name='list')
@method_decorator(decorator=cache_page(timeout=300), name='retrieve')
class AgentViewSet(ModelViewSet):
    """经理人视图
    list:
        获取经理人列表
    retrieve:
        获取经理人详情
    create:
        创建经理人
    update:
        更新经理人信息
    partial_update:
        更新经理人信息
    delete:
        删除经理人
    """
    # pagination_class = AgentCursorPagination
    queryset = Agent.objects.all()

    def get_queryset(self):
        # name = self.request.GET.get('name')
        # if name:
        #     self.queryset = self.queryset.filter(name__contains=name)
        # servstar = self.request.GET.get('servstar')
        # if servstar:
        #     self.queryset = self.queryset.filter(servstar__gte=servstar)
        if self.action == 'list':
            self.queryset = self.queryset.only('name', 'tel', 'servstar')
        else:
            self.queryset = self.queryset.prefetch_related(
                Prefetch('estates', queryset=Estate.objects.all().only('name').order_by('-hot')))
            return self.queryset

    def get_serializer_class(self):
        if self.action in ('create', 'update'):
            return AgentCreateSerializer
        return AgentDetailSerializer if self.action == 'retrieve' \
            else AgentSimpleSerializer


# 使用ModelViewSet写CBV视图，完成接口的定制
# 声明式缓存完成类方法缓存装饰器
@method_decorator(decorator=cache_page(timeout=86400), name='list')
@method_decorator(decorator=cache_page(timeout=86400), name='retrieve')
class HouseTypeViewSet(ModelViewSet):
    '''获取户型接口'''
    queryset = HouseType.objects.all()
    serializer_class = HouseTypeSerializer
    pagination_class = None


@method_decorator(decorator=cache_page(timeout=86400), name='list')
class TagViews(ModelViewSet):
    '''房源标签'''
    queryset = Tag.objects.all()
    serializer_class = TagListSerializer
    pagination_class = None


# 楼盘的接口数据筛选
@method_decorator(decorator=cache_page(timeout=300), name='list')
@method_decorator(decorator=cache_page(timeout=300), name='retrieve')
class EstateViewSet(ModelViewSet):
    """楼盘视图集"""
    queryset = Estate.objects.all()
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    # 只能做精确查询，而且多个条件间只能是而且的关系
    # filter_fields = ('name', 'hot', 'district')
    filterset_class = EstateFilterSet
    ordering = '-hot'
    ordering_fields = ('district', 'hot', 'name')

    # authentication_classes = (LoginRequiredAuthentication,)
    # permission_classes = (RbacPermission,)

    def get_queryset(self):
        if self.action == 'list':
            queryset = self.queryset.only('name', 'hot')
        else:
            queryset = self.queryset \
                .defer('district__parent', 'district__ishot', 'district__intro') \
                .select_related('district')
        return queryset

    def get_serializer_class(self):
        if self.action in ('create', 'update'):
            return EstateCreateSerializer
        return EstateDetailSerializer if self.action == 'retrieve' \
            else EstateSimpleSerializer


@method_decorator(decorator=cache_page(timeout=120), name='list')
@method_decorator(decorator=cache_page(timeout=300), name='retrieve')
class HouseInfoViewSet(ModelViewSet):
    """房源视图集"""
    queryset = HouseInfo.objects.all()
    serializer_class = HouseInfoDetailSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = HouseInfoFilterSet
    ordering = ('-pubdate',)
    ordering_fields = ('pubdate', 'price')

    @action(methods=('GET',), detail=True)
    def photos(self, request, pk):
        queryset = HousePhoto.objects.filter(house=self.get_object())
        return Response(HousePhotoSerializer(queryset, many=True).data)

    def get_queryset(self):
        if self.action == 'list':
            return self.queryset \
                .only('houseid', 'title', 'area', 'floor', 'totalfloor', 'price',
                      'mainphoto', 'priceunit', 'street', 'type',
                      'district_level3__distid', 'district_level3__name') \
                .select_related('district_level3', 'type') \
                .prefetch_related('tags')
        return self.queryset \
            .defer('user', 'district_level2',
                   'district_level3__parent', 'district_level3__ishot', 'district_level3__intro',
                   'estate__district', 'estate__hot', 'estate__intro',
                   'agent__realstar', 'agent__profstar', 'agent__certificated') \
            .select_related('district_level3', 'type', 'estate', 'agent') \
            .prefetch_related('tags')

    def get_serializer_class(self):
        if self.action in ('create', 'update'):
            return HouseInfoCreateSerializer
        return HouseInfoDetailSerializer if self.action == 'retrieve' \
            else HouseInfoSimpleSerializer


@api_view(('POST',))
def login(request):
    '''登录'''
    username = request.data.get('username')
    password = request.data.get('password')
    captcha = request.data.get('captcha')
    if username and password and captcha:
        session_captcha = request.session['captcha']
        if session_captcha.lower() == captcha.lower():
            password = to_md5_hex(password)
            user = User.objects.filter(Q(username=username, password=password) |
                                       Q(tel=username, password=password) |
                                       Q(email=username, password=password)).first()
            if user:
                # 登陆成功后 先生成好token令牌
                payload = {
                    # 有效时间位一天，信息为userid
                    'exp': datetime.utcnow() + timedelta(days=1),
                    'data': user.userid,
                }
                token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode()
                with atomic():
                    # 获取当前时间
                    current_time = timezone.now()
                    if not user.lastvisit or (current_time - user.lastvisit >= 1):
                        user.point += 2
                        user.lastvisit = current_time
                        user.save()
                    login_log = LoginLog()
                    login_log.user = user
                    login_log.ipaddr = get_ip_address
                    login_log.logdate = current_time
                    login_log.save()
                resp = DefaultResponse(*USER_LOGIN_SUCCESS, data={
                    'token': token, 'username': user.username, 'realname': user.realname
                })
            else:
                resp = DefaultResponse(*USER_LOGIN_FAILED)
        else:
            resp = DefaultResponse(*INVALID_LOGIN_INFO)
    else:
        resp = DefaultResponse(*NULL_LOGIN_INFO)
    return resp


def get_captcha(request):
    '''行为验证码视图'''
    # 生成验证码文本    并将验证码文本存入session
    captcha_text = gen_captcha_text()
    request.session['captcha'] = captcha_text
    # 生成图片文本
    image_data = Captcha.instance().generate(captcha_text)
    # 返回并声明这是一个png格式的验证码图片
    return HttpResponse(image_data, content_type='image/png')


@api_view(('GET',))
def get_code_by_sms(request, tel):
    """获取短信验证码"""
    if check_tel(tel):
        if caches['default'].get(f'{tel}:block'):
            resp = DefaultResponse(*CODE_TOO_FREQUENCY)
        else:
            code = gen_mobile_code()
            # 异步化的执行函数（把函数放到消息队列中去执行）----> 消息的生产者
            send_sms_by_aliyun.delay(tel, code)
            caches['default'].set(f'{tel}:block', code, timeout=120)
            # caches['default'].set(f'{tel}:valid', code, timeout=600)
            resp = DefaultResponse(*MOBILE_CODE_SUCCESS)
    else:
        resp = DefaultResponse(*INVALID_TEL_NUM)
    return resp


@api_view(('POST',))
def upload_photo(request):
    '''上传图片'''
    file = request.FILES.get('mainphoto')
    photo_oss = read_file(file.chunks())
    filename = f'{uuid.uuid4().hex}{os.path.splitext(file.name)[1]}'
    files = OssFLies()
    files.upload(key=filename, data=photo_oss)
    # photo = HousePhoto(
    #     path=f'https://fjl-g-mysql.oss-cn-shenzhen.aliyuncs.com/izufang/izufang/static/izufang_image/{filename}'
    # )
    # photo.save()
    return DefaultResponse(*FILE_UPLOAD_SUCCESS, data={
        'photoid': 1,
        'url': f'https://fjl-g-mysql.oss-cn-shenzhen.aliyuncs.com/izufang/izufang/static/izufang_image/{filename}',
    })


class UserViewSet(ModelViewSet):
    """用户模型视图集"""
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action == 'update':
            return UserUpdateSerializer
        return UserSimpleSerializer
