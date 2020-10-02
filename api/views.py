from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.serializers import *
from common.models import District, Agent


# FBV

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


@api_view(('GET',))
def get_cityside(HttpRequest, dist) :
    '''
    获取省级对应城市区信息
    :param request: 获取得请求信息
    :param dist: 获取得请求信息包含的字段内容
    :return: 返回响应数据Response
    '''
    queryset = District.objects.filter(distid=dist).defer('parent').first()
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
    queryset = Agent.objects.all()
    def get_queryset(self):
        queryset = self.queryset.prefetch_related('estates')
        if 'pk' in self.kwargs:
            queryset = self.queryset.only('name', 'servstar')
        return queryset.order_by('agentid')

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
class HouseTypeViewSet(ModelViewSet):
    '''获取户型接口'''

    queryset = HouseType.objects.all()
    serializer_class = HouseTypeSerializer
    pagination_class = None


# 设置只读形式的楼盘接口
class EstateViewSet(ReadOnlyModelViewSet):
    '''获取楼盘信息接口'''
    queryset = Estate.objects.all()
    def get_queryset(self):
        if self.action == 'list':
            queryset = self.queryset.only('name')
        else:
            queryset = self.queryset.\
                defer('district__parent','district__intro','district__ishot')\
                .select_related('district')
        return queryset
    def get_serializer_class(self):
        return EstateRetrieveSerializer if self.action == 'retrieve' else EstateSimpleSerializer