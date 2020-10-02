from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response

from api.serializers import DistrictSimpleSerializer, DistrictComplexSerializer
from common.models import District


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
    获取省级对应城市信息
    :param request: 获取得请求信息
    :param dist: 获取得请求信息包含的字段内容
    :return: 返回响应数据Response
    '''
    queryset = District.objects.filter(distid=dist).defer('parent').first()
    serializers = DistrictComplexSerializer(queryset)
    return Response(serializers.data)


# FBV
