import pickle

from django.core.cache import caches
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

# Create your views here.
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from django_redis import get_redis_connection
from rest_framework.decorators import api_view
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.helpers import AgentCursorPagination, EstateFilterSet, HouseInfoFilterSet
from api.serializers import *
from common.models import District, Agent


# FBV
# 声明式缓存
@cache_page(timeout=31536000, cache='default',key_prefix='api')
@api_view(('GET',))
def get_province(request: HttpRequest) -> HttpResponse:
    '''获取省级城市信息'''
    queryset = District.objects.filter(parent__isnull=True).only('name')
    serializers = DistrictSimpleSerializer(queryset,many=True)
    return Response({
        'code':1000,
        'message':'获取省级成功',
        'results':serializers.data,
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
def get_cityside(HttpRequest, dist) :
    '''
    获取省级对应城市区信息
    :param request: 获取得请求信息
    :param dist: 获取得请求信息包含的字段内容
    :return: 返回响应数据Response
    '''
    # 直接拿取django中的缓存的原生客户端进行查询
    cli = get_redis_connection()
    # 如果空则查询加缓存
    queryset = cli.get(f'izufang:dist:{dist}')
    if queryset:
        queryset = pickle.loads(queryset)
    else:
        queryset = District.objects.filter(distid=dist).defer('parent').first()
        data = pickle.dumps(queryset)
        cli.set(f'izufang:dist:{dist}', data, ex=900)
    serializers = DistrictComplexSerializer(queryset)
    return Response(serializers.data)


# FBV
# 增：有  删：有（暂时不给） 改：（有） 查：（有）
# RetrieveUpdate查看单条与更新
# queryset = Agent.objects.all().only('name', 'tel', 'servstar')
# serializer_class = AgentSimpleSerializer
# 首先查看单个经理人的 想要看全部字段包括负责楼盘这里的的楼盘名称
# 查看多个经理人 看经理人id和姓名以及星级即可
# 新增经理人，显示全部字段
# 更新经理人，只能更新部分字段
class AgentView(RetrieveUpdateAPIView,ListCreateAPIView):
    '''获取经理人视图'''
    pagination_class = AgentCursorPagination
    queryset = Agent.objects.all()
    def get_queryset(self):
        queryset = (self.queryset.prefetch_related('estates')) if 'pk' in self.kwargs \
            else (self.queryset.only('name', 'servstar'))
        return queryset.order_by('-servstar')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            serializer = AgentCreateSerializer
        else:
            serializer = AgentRetrieveSerializer if 'pk' in self.kwargs else AgentListSerializer
        return serializer

    def get(self, request, *args, **kwargs):
        cls = RetrieveUpdateAPIView if 'pk' in kwargs else ListCreateAPIView
        return cls.get(self, request, *args, **kwargs)

# 使用ModelViewSet写CBV视图，完成接口的定制
# 声明式缓存完成类方法缓存装饰器
@method_decorator(decorator=cache_page(timeout=86400), name='list')
@method_decorator(decorator=cache_page(timeout=86400), name='retrieve')
class HouseTypeViewSet(ModelViewSet):
    '''获取户型接口'''
    queryset = HouseType.objects.all()
    serializer_class = HouseTypeSerializer
    pagination_class = None


# 设置只读形式的楼盘接口
# 楼盘的接口数据筛选
@method_decorator(decorator=cache_page(timeout=86400), name='list')
@method_decorator(decorator=cache_page(timeout=86400), name='retrieve')
class EstateViewSet(ReadOnlyModelViewSet):
    '''获取楼盘信息接口'''
    queryset = Estate.objects.all()
    filter_backends = (DjangoFilterBackend,OrderingFilter)
    # filter_fields = ('name','hot','district') 指定字段直接使用filter_fields，
    # 定制类的筛选接口
    filterset_class = EstateFilterSet
    ordering = '-hot'
    ordering_fields = ('name','hot')
    def get_queryset(self):
        if self.action == 'list':
            queryset = self.queryset.only('name')
        else:
            queryset = self.queryset.\
                defer('district__parent','district__intro','district__ishot').\
                select_related('district')
        return queryset
    def get_serializer_class(self):
        return EstateRetrieveSerializer if self.action == 'retrieve' else EstateSimpleSerializer


@method_decorator(decorator=cache_page(timeout=86400), name='list')
class TagViews(ModelViewSet):
    '''房源标签'''
    queryset = Tag.objects.all()
    serializer_class = TagListSerializer
    pagination_class = None


class HouseInfoViews(ModelViewSet):
    '''房源信息视图'''
    queryset = HouseInfo.objects.all()
    filter_backends = (DjangoFilterBackend,OrderingFilter)
    filterset_class = HouseInfoFilterSet
    ordering = 'price'
    ordering_fields = ('floor','area')
    def get_queryset(self):
        if self.action == 'list':
            queryset = self.queryset.\
                only('title', 'area', 'floor', 'totalfloor', 'price', 'mainphoto', 'street', 'type',
                     'district_level3__distid', 'district_level3__name').select_related('district_level3', 'type').\
                prefetch_related('tags')
        else:
            queryset = self.queryset.defer('user', 'district_level2','district_level3__parent',
                                           'district_level3__intro', 'district_level3__ishot',
                                           'agent__realstar', 'agent__profstar', 'agent__certificated',
                                           'estate__intro', 'estate__hot', 'estate__district').\
                select_related('district_level3', 'type', 'estate', 'agent').\
                prefetch_related('tags')
        return queryset

    def get_serializer_class(self):
        if self.action in ('create', 'update'):
            cls = HouseInfoCreateSerializer
        else:
            cls = HouseInfoRetrieveSerializer if self.action == 'retrieve' else HouseInfoListSerializer
        return cls
